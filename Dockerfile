FROM python:3.7-alpine
WORKDIR /RESTFULapp
COPY . /RESTFULapp
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python", "myapp.py"]
