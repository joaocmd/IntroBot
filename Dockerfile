FROM python:3.9

RUN apt-get update && apt-get -y upgrade
RUN apt-get install ffmpeg -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "./main.py"]
