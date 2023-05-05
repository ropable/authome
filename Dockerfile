# Prepare the base environment.
FROM python:3.7.8-slim-buster as builder_base_authome
MAINTAINER asi@dbca.wa.gov.au
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y wget python3-dev \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip

#install and config poetry
ENV POETRY_VERSION=1.0.5
RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Install Python libs from pyproject.toml.
FROM builder_base_authome as python_libs_authome
WORKDIR /app/release
# Install the project.
FROM python_libs_authome
COPY manage.py gunicorn.py testperformance testrequestheaders ./
COPY authome ./authome
COPY templates ./templates
RUN export IGNORE_LOADING_ERROR=True ; python manage.py collectstatic --noinput --no-post-process

RUN cp -rf /app/release /app/dev

#comment out logger.debug to improve perfornace in production environment.
RUN find ./ -type f -iname '*.py' -exec sed -i 's/logger\.debug/#logger.debug/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/from \. import performance/#from . import performance/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/from \.\. import performance/#from .. import performance/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/performance\.start_processingstep/#performance.start_processingstep/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/performance\.end_processingstep/#performance.end_processingstep/g' "{}" +;

RUN find ./ -type f -iname '*.py' -exec sed -i 's/from \.models import DebugLog/#from .models import DebugLog/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/from \.\.models import DebugLog/#from ..models import DebugLog/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/DebugLog\.log/#DebugLog.log/g' "{}" +;
RUN find ./ -type f -iname '*.py' -exec sed -i 's/DebugLog\.attach_request/#DebugLog.attach_request/g' "{}" +;

WORKDIR /app
RUN echo "#!/bin/bash \n\
if [[ \"\$DEBUG\" == \"True\" || \"\${LOGLEVEL}\" == \"DEBUG\" ]]; then \n\
    echo \"Running in dev mode\" \n\
    cd /app/dev && gunicorn authome.wsgi --bind=:8080 --config=gunicorn.py \n\
else \n\
    echo \"Running in release mode\" \n\
    cd /app/release && gunicorn authome.wsgi --bind=:8080 --config=gunicorn.py \n\
fi \n\
" > start_app

RUN chmod 555 start_app

RUN echo "#!/bin/bash \n\
if [[ \"\$DEBUG\" == \"True\" || \"\${LOGLEVEL}\" == \"DEBUG\" ]]; then \n\
    echo \"Running in dev mode\" \n\
    cd /app/dev && python manage.py \"\$@\" \n\
else \n\
    echo \"Running in release mode\" \n\
    cd /app/release && python manage.py \"\$@\" \n\
fi \n\
" > run_command

RUN chmod 555 run_command


# Run the application as the www-data user.
USER www-data
EXPOSE 8080
CMD ./start_app
