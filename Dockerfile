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
RUN poetry install

COPY app.py config.py flask_config.py model.py trello_app.py /devops-course-starter/src/app/

# Expose instruction
EXPOSE 5000


FROM  base as production
ENV PORT 5000
# Dockerfile Entrypoint
#CMD [exec gunicorn --bind 0.0.0.0:5000 --forwarded-allow-ips='*' app:app]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src/app", "app:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--chdir", "src/app", "app:app"]


FROM base as development
ENV FLASK_ENV development
ENTRYPOINT FLASK_APP=/devops-course-starter/src/app/app.py flask run --host=0.0.0.0


# testing stage
FROM base as test

RUN apt-get update -qqy && apt-get install -qqy wget gnupg unzip
# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install google-chrome-stable \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*
# Install Chrome WebDriver
RUN CHROME_MAJOR_VERSION=$(google-chrome --version | sed -E "s/.* ([0-9]+)(\.[0-9]+){3}.*/\1/") \
  && CHROME_DRIVER_VERSION=$(wget --no-verbose -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}") \
  && echo "Using chromedriver version: "$CHROME_DRIVER_VERSION \
  && wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
  && unzip /tmp/chromedriver_linux64.zip -d /usr/bin \
  && rm /tmp/chromedriver_linux64.zip \
  && chmod 755 /usr/bin/chromedriver

COPY test_integration_trello.py test_ViewModel.py ./tests_e2e /devops-course-starter/src/app/
ENTRYPOINT ["poetry", "run", "pytest"]
