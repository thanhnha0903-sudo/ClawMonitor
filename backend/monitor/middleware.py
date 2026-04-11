from django.core.cache import cache
from django.utils import timezone

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Nếu user đã đăng nhập, lưu trạng thái của họ vào Cache trong 300 giây (5 phút)
        if request.user.is_authenticated:
            cache_key = f'seen_{request.user.username}'
            cache.set(cache_key, timezone.now(), 300)
            
        return response
