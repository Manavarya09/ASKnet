FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ASKNet ./ASKNet
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create symlinks for easier import
RUN ln -s /app/ASKNet /app/ASKNet

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["./docker-entrypoint.sh"]