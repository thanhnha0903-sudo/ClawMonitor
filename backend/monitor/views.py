import json
from zoneinfo import ZoneInfo
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Company, Device, Floorplan
from .utils import send_telegram_alert

def get_vn_now_str():
    vn_tz = ZoneInfo('Asia/Ho_Chi_Minh')
    return timezone.now().astimezone(vn_tz).strftime('%H:%M:%S %d/%m/%Y')

# API Đã gỡ bỏ @login_required để App điện thoại chọc vào
def api_devices(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    devices = Device.objects.filter(company=company)
    data = []
    now = timezone.now()

    for d in devices:
        # 1. Xử lý logic cảnh báo Offline (Code cũ của bạn)
        is_demo = getattr(d, 'is_demo', False)
        if d.is_online and getattr(d, 'last_seen', None) and not is_demo:
            if (now - d.last_seen).total_seconds() > 45:
                d.is_online = False
                d.cpu_usage = 0
                d.ram_usage = 0
                d.save()
                admin_id = getattr(company, 'admin_telegram_id', None)
                if admin_id and str(admin_id).strip() != "":
                    msg = f"🔴 <b>CẢNH BÁO MẤT KẾT NỐI</b>\nCông ty: <b>{company.name}</b>\nThiết bị: <b>{d.name}</b>\nIP: {d.ip_address}\nThời gian: {get_vn_now_str()}"
                    send_telegram_alert(msg, admin_id)

        # 2. Xử lý Waypoints (Code cũ của bạn)
        wp_data = []
        if getattr(d, 'waypoints', None):
            if isinstance(d.waypoints, str):
                try:
                    clean_wp = d.waypoints.replace("'", '"')
                    wp_data = json.loads(clean_wp)
                except Exception:
                    wp_data = []
            else:
                wp_data = d.waypoints

        # 3. Gói dữ liệu gửi ra Frontend (Đã tích hợp Bộ Lọc)
        data.append({
            'id': d.id,
            'name': d.name,
            'ip_address': d.ip_address,
            
            # --- 2 BIẾN QUAN TRỌNG ĐỂ LỌC VÀ CHUYỂN KHU ---
            'device_type': getattr(d, 'device_type', 'PC'),
            'floorplan_id': getattr(d, 'floorplan_id', None) if getattr(d, 'floorplan_id', None) else 'all',
            
            # --- THÔNG SỐ TRẠNG THÁI ---
            'is_online': d.is_online,
            'pos_x': d.pos_x,
            'pos_y': d.pos_y,
            'cpu_usage': getattr(d, 'cpu_usage', 0),
            'ram_usage': getattr(d, 'ram_usage', 0),
            
            # --- THÔNG TIN ĐẤU NỐI DÂY ---
            'my_device_port': getattr(d, 'device_port', ''),
            'uplink_id': getattr(d, 'uplink_id', None),
            'uplink_name': d.uplink.name if getattr(d, 'uplink', None) else "",
            'uplink_port': getattr(d, 'uplink_port', ''),
            'waypoints': wp_data,
        })
        
    map_url = company.floor_plan.url if getattr(company, 'floor_plan', None) else ""
    return JsonResponse({'devices': data, 'map_url': map_url})

@csrf_exempt
def api_report_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device = Device.objects.get(ip_address=data['ip'], company_id=data['company_id'])
            if not device.is_online and data.get('is_online', False):
                admin_id = getattr(device.company, 'admin_telegram_id', None)
                if admin_id and str(admin_id).strip() != "":
                    msg = f"🟢 <b>THIẾT BỊ ĐÃ ONLINE</b>\nCông ty: <b>{device.company.name}</b>\nThiết bị: <b>{device.name}</b>\nThời gian: {get_vn_now_str()}"
                    send_telegram_alert(msg, admin_id)
            device.is_online = data.get('is_online', False)
            device.last_seen = timezone.now()
            if 'cpu' in data and 'ram' in data:
                device.cpu_usage = data['cpu']
                device.ram_usage = data['ram']
            device.save() # Đã fix lỗi thụt lề ở dòng này
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=405)

@login_required(login_url='/admin/login/')
def map_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    floorplans = Floorplan.objects.filter(company=company)
    if not request.user.is_superuser and company not in request.user.companies.all():
        return HttpResponseForbidden("Bạn không có quyền xem bản đồ này.")
    return render(request, 'monitor/map.html', {
        'is_admin': request.user.is_superuser, 
        'company_id': company.id, 
        'company_name': company.name,
        'company': company,         
        'floorplans': floorplans    
    })

@csrf_exempt
def update_pos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device = Device.objects.get(id=data['id'])
            device.pos_x = data['x']
            device.pos_y = data['y']
            device.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def update_waypoints(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device = Device.objects.get(id=data['id'])
            wp = data.get('waypoints', [])
            if not isinstance(wp, str): wp = json.dumps(wp)
            device.waypoints = wp
            device.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def export_client_config(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    # Đã fix lỗi bị cắt cụt dòng ở đây
    config_data = {
        "type": "AGENT", 
        "company_id": device.company.id, 
        "company_name": device.company.name, 
        "device_name": device.name, 
        "my_ip": device.ip_address, 
        "server_url": f"http://{request.get_host()}:90/api/report-status/"
    }
    response = HttpResponse(json.dumps(config_data, indent=4, ensure_ascii=False), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="config_agent_{device.name}.json"'
    return response

def export_server_config(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    devices = Device.objects.filter(company=company)
    config_data = {"type": "SERVER", "company_id": company.id, "company_name": company.name, "server_url": f"http://{request.get_host()}:90/api/report-status/", "devices": [{"name": d.name, "ip": d.ip_address} for d in devices]}
    response = HttpResponse(json.dumps(config_data, indent=4, ensure_ascii=False), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="config_server_{company.name}.json"'
    return response

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            import json
            from django.contrib.auth.models import User
            from django.contrib.auth.hashers import check_password
            
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            # 1. Tìm User
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Tài khoản không tồn tại"}, status=401)
            
            # 2. Kiểm tra mật khẩu
            if check_password(password, user.password):
                return JsonResponse({
                    "status": "success", 
                    "company_id": data.get('company_id'),
                    "company_name": "NOC Dashboard"
                })
            
            return JsonResponse({"status": "error", "message": "Mật khẩu không chính xác"}, status=401)
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=405)
