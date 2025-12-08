FROM agrigorev/model-2025-hairstyle:v1

# Install Python deps needed for the lambda handler
RUN pip install --no-cache-dir pillow numpy onnxruntime

# Copy lambda handler into the image
COPY lambda_function.py /var/task/lambda_function.py

# Entrypoint is defined by the base Lambda image

