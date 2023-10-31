# Use the official Python image as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code to the container
COPY . .

# Expose the port that your Flask app will run on
EXPOSE 5000

# Install Playwright browsers
RUN npx playwright install

# Run your application
CMD ["python", "app.py"]
