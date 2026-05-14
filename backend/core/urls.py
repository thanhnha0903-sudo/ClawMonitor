"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from monitor import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', views.dashboard_redirect, name='dashboard_redirect'),  # <-- TRẠM TRUNG CHUYỂN NẰM ĐÂY
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='monitor/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('api/devices/<int:company_id>/', views.api_devices, name='api_devices'),
    path('api/devices/update-pos/', views.update_pos, name='update_pos'),
    path('api/devices/update-waypoints/', views.update_waypoints, name='update_waypoints'),
    path('api/report-status/', views.api_report_status, name='report_status'),
    path('export-server-config/<int:company_id>/', views.export_server_config, name='export_server_config'),
    path('export-client-config/<int:device_id>/', views.export_client_config, name='export_client_config'),
    path('map/<int:company_id>/', views.map_view, name='map_view'),
    path('api/login/', views.api_login, name='api_login'),
]

# Phần này để phục vụ hiển thị ảnh bản đồ (Giữ nguyên ở cuối file)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
