# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /powerUrl

# Copy the current directory contents into the container at /app
COPY . /powerUrl

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python3", "app.py"]

# docker build -t powerurl .
# docker run -d -p 5000:5000 -v ${PWD}:/powerUrl --name powerurl powerurl