FROM python:3.8.3-buster as base

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

RUN mkdir /devops-course-starter
WORKDIR /devops-course-starter

RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY poetry.toml pyproject.toml README.md /devops-course-starter/

# Prevent poetry from installing todo_app enabling docker to cache layers
RUN mkdir -p /devops-course-starter/src/app
RUN touch /devops-course-starter/src/app/__init__.py

RUN pip install -U pip
RUN poetry install --no-dev

COPY app.py config.py flask_config.py model.py trello_app.py /devops-course-starter/src/app/

# Expose instruction
EXPOSE 5000


FROM  base as production
# Dockerfile Entrypoint
#CMD [exec gunicorn --bind 0.0.0.0:5000 --forwarded-allow-ips='*' app:app]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src/app", "app:app"]


FROM base as development
ENV FLASK_ENV development
ENTRYPOINT FLASK_APP=/devops-course-starter/src/app/app.py flask run --host=0.0.0.0
