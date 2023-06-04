FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV HOME=/code

ENV DJANGO_SECRET_KEY=ghwe490wghuj8w4tgiw4hu9jw4hj9er
ENV ENV_NAME=Production

RUN mkdir -p $HOME
WORKDIR $HOME

COPY . $HOME

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
