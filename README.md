# devops-challenge

# Example Flask application

See ``src`` for the application code.

## Building Docker image

The Python 3 based [Dockerfile](Dockerfile.py3) uses an Alpine Linux base image
and expects the application source code to be volume mounted at `/application`
when run:

```
FROM python:3.6.1-alpine
ADD . /application
WORKDIR /application
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
	; \
	pip install -r src/requirements.txt; \
	apk del .build-deps;
EXPOSE 5000
VOLUME /application
CMD uwsgi --http :5000  --manage-script-name --mount /myapplication=flask_app:app --enable-threads --processes 5
```

The last statement shows how we are running the application via `uwsgi` with 5
worker processes.

To build the image:

```
$ docker build -t yomtell/flask_app -f Dockerfile.py3 .
```

## Running the application

We can just run the web application as follows:

```
$ docker run  -ti -p 5000:5000 -v `pwd`/src:/application yomtell/flask_app
```

## Bringing up the web application, along with prometheus

The [docker-compse.yml](docker-compose.yml) brings up the `webapp` service which is our web application
using the image `yomtell/flask_app` we built above. The [docker-compose-infra.yml](docker-compose-infra.yml)
file brings up the `prometheus` service and also starts the `grafana` service which
is available on port 3000. The config directory contains a `prometheus.yml` file
which sets up the targets for prometheus to scrape. The scrape configuration 
looks as follows:

```
# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
         - targets: ['localhost:9090']
  - job_name: 'webapp'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    static_configs:
        - targets: ['webapp:5000']
```

Prometheus scrapes itself, which is the first target above. The second target
is the our web application on port 5000.
Since these services are running via `docker-compose`, `webapp` automatically resolves to the IP of the webapp container. 

To bring up all the services:

```
$ docker-compose -f docker-compose.yml -f docker-compose-infra.yml up
```

