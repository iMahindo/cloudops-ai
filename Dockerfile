#Base image
FROM python:3.13-slim

#create the root directory
WORKDIR /app

#copy the requirement doc before the whole project to create the first layer with pip install
#this avoid the pip install execution every time code changes
COPY requirements.txt .

#install the libraries required
RUN pip install --no-cache-dir -r requirements.txt

#Copy the aplication code (root project to docker image->/app)
COPY . .

#DOCKER execution
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]