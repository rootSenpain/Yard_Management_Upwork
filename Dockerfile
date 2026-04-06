# Hafif ve güncel bir Python imajı seçiyoruz
FROM python:3.11-slim

# Çalışma dizini oluştur
WORKDIR /app

# Sistem bağımlılıklarını kur (PostgreSQL için gerekli kütüphaneler)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Başlangıç betiğini çalıştırılabilir yap
RUN chmod +x /app/start.sh

# Uygulama portunu aç
EXPOSE 8000

# Başlangıç komutu (Migration ve App başlatma)
CMD ["/app/start.sh"]