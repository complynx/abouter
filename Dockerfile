# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file or setup.py into the container at /app
COPY setup.py /app

# Install any needed packages specified in setup.py
RUN python setup.py install

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME abouter

CMD ["sh", "-c", "python -m abouter.main"]
