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

COPY app.py config.py flask_config.py model.py trello_app.py .env.template /devops-course-starter/src/app/

# Expose instruction
EXPOSE 5000


FROM  base as production
# Dockerfile Entrypoint
#CMD [exec gunicorn --bind 0.0.0.0:5000 --forwarded-allow-ips='*' app:app]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src/app", "app:app"]


FROM base as development
ENV FLASK_ENV development
ENTRYPOINT FLASK_APP=/devops-course-starter/src/app/app.py flask run --host=0.0.0.0


# testing stage
FROM base as test

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chromestable_current_amd64.deb -o chrome.deb &&\
  apt-get install ./chrome.deb -y &&\
  rm ./chrome.deb

# Install Chromium WebDriver
RUN LATEST=`curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE` &&\
  echo "Installing chromium webdriver version ${LATEST}" &&\
  curl -sSL https://chromedriver.storage.googleapis.com/${LATEST}/chromedriver_linux64.zip -o chromedriver_linux64.zip &&\
  apt-get install unzip -y &&\
  unzip ./chromedriver_linux64.zip

COPY test_integration_trello.py test_ViewModel.py .env.test ./tests_e2e /devops-course-starter/src/app/
ENTRYPOINT ["poetry", "run", "pytest"]
