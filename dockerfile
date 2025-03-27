# Use an official Python runtime as a parent image
FROM python:3.11.0-slim


# Install gcc and python3-dev
RUN apt-get update && apt-get install -y gcc python3-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt -v

# Copy the rest of the application to the working directory
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "srpc_new.wsgi:application"]
