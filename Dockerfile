# Use of the official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the required modules and files
COPY . .
COPY requirements.txt .

# Run pip
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8081

# Run FastAPI application using uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]