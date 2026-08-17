#Base image
FROM python:3.13-slim

#Send Python output immediately to the container logs
ENV PYTHONUNBUFFERED=1

#create the root directory
WORKDIR /app

#copy the requirement doc before the whole project to create the first layer with pip install
#this avoid the pip install execution every time code changes
COPY requirements.txt .

#install the libraries required
RUN pip install --no-cache-dir -r requirements.txt

#Create a non-root user for running the application
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

#Copy the aplication code (root project to docker image->/app using a non-root user)
COPY --chown=appuser:appuser . .

#Run the application without root privileges
USER appuser

#Document the internal port used by the application
EXPOSE 8000

#DOCKER execution
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]