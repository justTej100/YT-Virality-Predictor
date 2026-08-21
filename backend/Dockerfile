FROM python:3.11-slim

WORKDIR /app

# Install backend deps first for better layer caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared feature engineering code, trained model artifacts, and backend app
COPY common ./common
COPY ml/models ./ml/models
COPY backend/main.py ./main.py
COPY backend/app ./app

ENV PYTHONUNBUFFERED=1
ENV APP_BASE_DIR=/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
