# Basic flask container

FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential gcc libgeos-dev libpq-dev postgresql-client

ADD ./app /home/app/
WORKDIR /home/app/
RUN pip install requests flask-sqlalchemy psycopg2 nltk geoparsepy
RUN pip install -r requirements.txt
CMD ["python", "import nltk"]
CMD ["python", "nltk.download('all')"] 

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
