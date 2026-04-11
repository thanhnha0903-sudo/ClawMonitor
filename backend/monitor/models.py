from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. QUẢN LÝ CÔNG TY
# ==========================================
class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên công ty")
    admin_telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Telegram Admin")
    # Giữ lại trường này nếu công ty nhỏ chỉ có 1 bản vẽ duy nhất
    floor_plan = models.ImageField(upload_to='floorplans/', blank=True, null=True, verbose_name="Sơ đồ mặt bằng gốc")
    viewers = models.ManyToManyField(User, blank=True, related_name='companies', verbose_name="Người dùng được xem")

    class Meta:
        verbose_name = "Công ty"
        verbose_name_plural = "Danh sách Công ty"

    def __str__(self):
        return self.name

# ==========================================
# 2. QUẢN LÝ KHU VỰC / TẦNG (Thay thế cho Zone)
# ==========================================
class Floorplan(models.Model):
    """Bảng quản lý Phân khu / Tầng / Xưởng cho từng Công ty"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='floorplans', verbose_name="Thuộc Công ty")
    name = models.CharField(max_length=100, verbose_name="Tên khu vực (VD: Xưởng A, Tầng 1)")
    bg_image = models.ImageField(upload_to='floorplans/', null=True, blank=True, verbose_name="Ảnh bản vẽ nền")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả thêm")

    class Meta:
        verbose_name = "Khu vực / Bản vẽ"
        verbose_name_plural = "Danh sách Khu vực"

    def __str__(self):
        return f"[{self.company.name}] - {self.name}"

# ==========================================
# 3. QUẢN LÝ THIẾT BỊ
# ==========================================
class Device(models.Model):
    DEVICE_TYPES = [
        ('FW', 'Firewall'), 
        ('CSW', 'Core Switch'), 
        ('ASW', 'Access Switch'), 
        ('PC', 'Máy tính'),
        ('CAM', 'Camera'), 
        ('SRV', 'Server'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='devices', verbose_name="Công ty")
    # Trỏ thiết bị về Floorplan (đóng vai trò là Zone)
    floorplan = models.ForeignKey(Floorplan, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices', verbose_name="Thuộc khu vực/Bản vẽ")
    
    name = models.CharField(max_length=100, verbose_name="Tên thiết bị")
    ip_address = models.GenericIPAddressField(verbose_name="Địa chỉ IP", unique=True)
    device_type = models.CharField(max_length=5, choices=DEVICE_TYPES, default='PC', verbose_name="Loại thiết bị")
    is_demo = models.BooleanField(default=False, verbose_name="Thiết bị Demo (Giữ Online)")
    waypoints = models.JSONField(default=list, blank=True, null=True, verbose_name="Điểm bẻ cáp")

    # --- KẾT NỐI MẠNG (TOPOLOGY) ---
    uplink = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='downlinks', 
        verbose_name="Thiết bị cha (Uplink)"
    )
    uplink_port = models.CharField(max_length=50, blank=True, verbose_name="Cổng trên thiết bị cha")
    device_port = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cổng tại thiết bị")

    # --- THÔNG SỐ TRẠNG THÁI ---
    is_online = models.BooleanField(default=False, verbose_name="Trạng thái Online")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Lần cuối nhìn thấy")
    cpu_usage = models.FloatField(default=0.0, verbose_name="CPU (%)")
    ram_usage = models.FloatField(default=0.0, verbose_name="RAM (%)")
    
    # --- TỌA ĐỘ BẢN VẼ ---
    pos_x = models.FloatField(default=0.0)
    pos_y = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Thiết bị"
        verbose_name_plural = "Danh sách Thiết bị"

    def __str__(self):
        return f"{self.name} - {self.ip_address}"

class UserDashboard(User):
    class Meta:
        proxy = True
        verbose_name = "User Dashboard"
        verbose_name_plural = "Danh Sách Người Dùng"
