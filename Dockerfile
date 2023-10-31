# Use the official Playwright Docker image as a parent image
FROM mcr.microsoft.com/playwright/python:v1.35.0-focal

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code to the container
COPY . .

# Expose the port that your Flask app will run on
EXPOSE 5000

# Run your application
CMD ["python", "app.py"]