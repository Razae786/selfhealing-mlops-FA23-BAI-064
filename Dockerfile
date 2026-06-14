FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
# Install CPU-only PyTorch FIRST to prevent downloading 2.5GB of Nvidia CUDA wheels
RUN pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
# Install the rest of the requirements (pip skips torch since it's already installed)
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
