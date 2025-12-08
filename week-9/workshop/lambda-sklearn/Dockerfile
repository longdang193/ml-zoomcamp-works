
# Use the official AWS Lambda base image for Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# # Instead of installing 'uv' via curl/pip, we copy the binary directly from its official Docker image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy dependency definition files into the container
COPY pyproject.toml uv.lock ./

# Install dependencies system-wide inside the Lambda image
# AWS Lambda does NOT use virtual environments, so packages must go into the system site-packages
RUN uv pip install --system -r <(uv export --format requirements-txt)

# Copy the application code into the container
COPY lambda_function.py model.bin ./

# Set the entry point to the lambda_handler function
CMD ["lambda_function.lambda_handler"]
