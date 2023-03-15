# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code into the container at /app
COPY . .

# Copy the gunicorn configuration file into the container at /config
COPY gunicorn.conf.py /config/

# Expose port 5000 to the outside world
EXPOSE 5000

# Start the application with gunicorn using the configuration file in the /config directory
CMD ["gunicorn", "--chdir", "app", "--config", "/config/gunicorn.conf.py", "app:app"]
