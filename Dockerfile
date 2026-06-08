FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
# Install CPU-only PyTorch first to save ~4GB of space
RUN pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
# Install the rest of the requirements
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p /app/logs
CMD ["python", "app.py"]
