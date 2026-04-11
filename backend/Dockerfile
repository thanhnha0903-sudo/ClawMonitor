FROM python:3.11-slim

# Cài đặt thư viện hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt thư viện Python từ requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào image
COPY . .

# Lệnh chạy mặc định
CMD ["python", "manage.py", "runserver", "0.0.0.0:7000"]
