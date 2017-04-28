mnm
===

Mastodon Network Monitoring: track and display browsable stats about Mastodon network (instances, toots, users...).

Public instance available here: https://mnm.eliotberriot.com

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: MIT

Architecture
------------

- Data about instances is pulled from https://instances.mastodon.xyz/instances.json
- Data is stored temporary in a database, then pushed in a dedicated timeseries database (influxdb)
- Grafana is connected to influxdb in order to create pretty and useful charts / dashboards

Deploying
---------

Docker-only at the moment::

    cp env.example .env
    nano .env

    docker-compose up --build -d

    # create initial tables in database
    docker-compose run django python manage.py migrate

    # create a super user
    docker-compose run django python manage.py createsuperuser

    # create the required influxdb database
    docker-compose -f dev.yml exec influxdb curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE mnm"
