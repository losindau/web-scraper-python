# Use the official Debian-based Python image as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Add the Debian package repositories
RUN echo "deb http://deb.debian.org/debian/ bookworm main" > /etc/apt/sources.list
RUN echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Install necessary system libraries
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnssutil3 \
    libsmime3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxdamage1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Install Node.js and npm
RUN apt-get install -y nodejs npm

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