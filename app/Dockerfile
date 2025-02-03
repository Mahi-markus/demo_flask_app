# Use a slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory to /app inside the container
WORKDIR /app

# Copy the requirements.txt file to the container's /app directory
COPY requirements.txt requirements.txt

# Install the dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files into the /app directory
COPY . .

# Set the default command to run the Python server
CMD ["python", "server.py"]


