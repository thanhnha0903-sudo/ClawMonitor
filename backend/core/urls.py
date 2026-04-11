"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from monitor import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
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
# Thêm 2 dòng này ở cuối file:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
