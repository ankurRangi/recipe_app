# Things docker need to build our image.
# Starting with a Base Image (with version) we need from docker hub on which we will install our dependencies
FROM python:3.9-alpine3.13

# The maintainer/creator of the docker image, can add any website to let our developers know.
LABEL maintainer="https://github.com/ankurRangi"

# Only needed when running in a docker container, it stops the buffering the output, python output will display
# on the console without delay.
ENV PYTHONUNBUFFERED 1

# Copy local txt file to docker image, which then will be used to install the requirements.
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

# Default dir to run the commands on docker image.  
WORKDIR /app

# Connect with the django dev server
EXPOSE 8000

# Currently development mode is false (off)
ARG DEV=false

# Runing a single command for a list of things to avoid creating multiple images for each run command.
# 1. Installing venv (Not really needed since we are working on a docker container) to handle edge cases of dependencies.
# 2. Pip upgrade
# 3. Installing requirements
# 4. Deleting /tmp folder to remove unnecessary files.
# 5. Adding current user (and not root user of docker hub) to access the container which will have limited access based on role and if 
    # System gets compramised, the attacker will have limited access of that of the user.
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Adding default path for env to fast processing
ENV PATH="/py/bin:$PATH"

# Docker will run with last user that the image switched to.
USER django-user