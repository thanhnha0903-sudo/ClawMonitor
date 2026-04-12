from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.core.cache import cache
from .models import Company, Floorplan, Device
from django.contrib.auth.models import User
from .models import UserDashboard

# ==========================================
# 1. GIAO DIỆN QUẢN LÝ CÔNG TY
# ==========================================
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'admin_telegram_id', 'view_map_button', 'download_server_button', 'action_buttons')

    def action_buttons(self, obj):
        edit_url = reverse('admin:monitor_company_change', args=[obj.pk])
        delete_url = reverse('admin:monitor_company_delete', args=[obj.pk])
        
        return format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: nowrap;">'
            '<a class="btn btn-sm btn-info" style="color:white;" href="{}"><i class="fas fa-edit"></i> Sửa</a>'
            '<a class="btn btn-sm btn-danger" style="color:white;" href="{}"><i class="fas fa-trash"></i> Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'Thao tác'
    
    def view_map_button(self, obj):
        url = reverse('map_view', args=[obj.id])
        return format_html(
            '<a class="btn btn-sm" style="background-color: #417690; color: white;" href="{}" target="_blank"><i class="fas fa-map"></i> Giám sát</a>',
            url
        )
    view_map_button.short_description = "Giám sát"

    def download_server_button(self, obj):
        url = reverse('export_server_config', args=[obj.id])
        return format_html(
            '<a class="btn btn-sm" style="background-color: #ba2121; color: white;" href="{}"><i class="fas fa-download"></i> Server</a>',
            url
        )
    download_server_button.short_description = "Cấu hình Server"


# ==========================================
# 2. GIAO DIỆN QUẢN LÝ KHU VỰC / BẢN VẼ
# ==========================================
@admin.register(Floorplan)
class FloorplanAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'device_count', 'action_buttons')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')

    def device_count(self, obj):
        count = obj.devices.count()
        return format_html('<b>{} thiết bị</b>', count)
    device_count.short_description = "Số lượng thiết bị"

    def action_buttons(self, obj):
        edit_url = reverse('admin:monitor_floorplan_change', args=[obj.pk])
        delete_url = reverse('admin:monitor_floorplan_delete', args=[obj.pk])
        return format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: nowrap;">'
            '<a class="btn btn-sm btn-info" style="color:white;" href="{}"><i class="fas fa-edit"></i> Sửa</a>'
            '<a class="btn btn-sm btn-danger" style="color:white;" href="{}"><i class="fas fa-trash"></i> Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    action_buttons.short_description = 'Thao tác'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# ==========================================
# 3. GIAO DIỆN QUẢN LÝ THIẾT BỊ
# ==========================================
@admin.register(Device)
class DeviceAdmin(ImportExportModelAdmin):
    list_display = ('name', 'ip_address', 'device_type', 'company', 'get_floorplan_name', 'get_is_online_status', 'actions_column', 'download_client_button')
    list_filter = ('company', 'floorplan', 'device_type', 'is_online')
    search_fields = ('name', 'ip_address')
    ordering = ('-last_seen',)

    def get_floorplan_name(self, obj):
        if obj.floorplan:
            name = obj.floorplan.name
            if ' - ' in name:
                return name.split(' - ')[-1].strip()
            return name
        return "-"
    get_floorplan_name.short_description = "Khu vực"

    def get_is_online_status(self, obj):
        return obj.is_online
    get_is_online_status.short_description = "Status"
    get_is_online_status.boolean = True

    def actions_column(self, obj):
        edit_url = reverse('admin:monitor_device_change', args=[obj.pk])
        delete_url = reverse('admin:monitor_device_delete', args=[obj.pk])
        return format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: nowrap;">'
            '<a class="btn btn-sm btn-info" style="color: white;" href="{}"><i class="fas fa-edit"></i> Sửa</a>'
            '<a class="btn btn-sm btn-danger" style="color: white;" href="{}"><i class="fas fa-trash"></i> Xóa</a>'
            '</div>',
            edit_url, delete_url
        )
    actions_column.short_description = "Thao tác"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
           del actions['delete_selected']
        return actions

    def download_client_button(self, obj):
        valid_types = ['pc', 'máy tính', 'laptop', 'server', 'srv']
        if obj.device_type and any(t in obj.device_type.lower() for t in valid_types):
            url = reverse('export_client_config', args=[obj.id])
            return format_html(
                '<a class="btn btn-sm btn-success" style="color: white;" href="{}"><i class="fas fa-download"></i> Client</a>',
                url
            )
        return format_html('<span style="color: #999;">-</span>')
    download_client_button.short_description = "Client"


# ==========================================
# 4. GIAO DIỆN QUẢN LÝ USER
# ==========================================
@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_telegram_id', 'first_name', 'last_name', 'get_online_status', 'get_companies', 'action_buttons')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    def get_telegram_id(self, obj):
        return obj.email if obj.email else "-"
    get_telegram_id.short_description = "ID Telegram"

    def get_online_status(self, obj):
        cache_key = f'seen_{obj.username}'
        is_online = cache.get(cache_key) is not None
        return is_online
    get_online_status.short_description = "Status"
    get_online_status.boolean = True

    def get_companies(self, obj):
        companies = obj.companies.all()
        if companies.exists():
            return ", ".join([c.name for c in companies])
        return format_html('<span style="color: red;">Chưa gán</span>')
    get_companies.short_description = "Thuộc công ty"

    def action_buttons(self, obj):
        edit_url = reverse('admin:auth_user_change', args=[obj.pk])
        pwd_url = reverse('admin:auth_user_password_change', args=[obj.pk])

        return format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: nowrap; justify-content: flex-start;">'
            '<a class="btn btn-sm btn-warning" style="color:black; font-weight:bold;" href="{}"><i class="fas fa-key"></i> Đổi Pass</a>'
            '<a class="btn btn-sm btn-info" style="color:white; font-weight:bold;" href="{}"><i class="fas fa-edit"></i> Sửa</a>'
            '</div>',
            pwd_url, edit_url
        )
    action_buttons.short_description = 'Thao tác'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or super().has_view_permission(request, obj)

    def has_module_permission(self, request):
        return request.user.is_superuser or super().has_module_permission(request)
