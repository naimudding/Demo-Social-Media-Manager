FROM python:3.9.13

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /demo_sm_manager

COPY ./requirements.txt ./requirements.txt
# COPY entrypoint.sh /usr/src/

# ENTRYPOINT [ "sh", "/usr/src/entrypoint.sh" ]

RUN apt-get update -y

RUN pip install --upgrade pip

RUN pip install --upgrade wheel

RUN pip install --upgrade setuptools

RUN pip install --no-cache-dir -r requirements.txt

# port where the Django app runs  
EXPOSE 8000

COPY . .

ADD . /demo_sm_manager

RUN cd demo_sm_manager

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

# CMD "gunicorn --preload --bind :8000 --workers 1 --threads 8 --timeout 0 demo_sm_manager.wsgi:application"

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "demo_sm_manager.wsgi:application"]