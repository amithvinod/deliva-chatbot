# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Copy the JSON credentials file into the container
COPY config/service_account.json /app/config/service_account.json

# Set environment variable for the credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/config/service_account.json"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (Cloud Run listens on this port by default)
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
