# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 9092 available to the world outside this container (optional, Kafka uses this port)
EXPOSE 9092 9093 9094

# Run the Python script when the container launches
CMD ["python", "./metrics_scraper.py"]

