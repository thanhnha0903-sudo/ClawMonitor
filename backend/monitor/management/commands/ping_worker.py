import time
import subprocess
from django.core.management.base import BaseCommand
from monitor.models import Device

class Command(BaseCommand):
    help = 'Chạy tiến trình Ping thiết bị liên tục'

    def handle(self, *args, **kwargs):
        self.stdout.write("Bắt đầu quét mạng Real-time...")
        while True:
            devices = Device.objects.all()
            for dev in devices:
                # Lệnh ping 1 gói tin, chờ 1 giây
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', dev.ip_address],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                is_alive = (result.returncode == 0)

                # Logic phát hiện thay đổi trạng thái và gửi Telegram
                if dev.is_online != is_alive:
                    dev.is_online = is_alive
                    dev.save()
                    status_text = "🟢 ONLINE" if is_alive else "🔴 OFFLINE"
                    self.stdout.write(f"{dev.name} ({dev.ip_address}) -> {status_text}")

                    # ---> CHÈN CODE GỌI API TELEGRAM CỦA BẠN VÀO ĐÂY <---

            # Nghỉ 5 giây trước khi vòng lặp quét lại toàn bộ
            time.sleep(5)
