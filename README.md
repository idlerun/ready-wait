---
page: https://idle.run/ready-wait
title: "Ready-Wait For Docker Containers"
tags: docker
date: 2015-11-24
---

Docker supports linking together containers and will ensure that containers only start if the containers they depend on are started. It doesn't have
anything (yet) for app-specific logic which indicates whether the dependency is actually *ready*.

Here is a simple Python script which can be run inside of a container to delay starting the app code until preconditions are met.

## Script

The following is the script which will run and wait until the preconditions defined in the yaml definition below are met

#### [ready_wait.py](https://github.com/idlerun/ready-wait/blob/master/ready_wait.py)

## Configuration

The script above expects a configuration file at `/etc/ready_wait.yaml` like the following

```yaml
hostname1:
  http:
    port: 80
    uri: /status
    status: 200
    contains: OK

hostname2:
  tcp:
    port: 80
```

## Docker Usage

Modify the Docker container CMD to wait for ready_wait to complete before running the normal app entrypoint for your container. For example:

```text
FROM ubuntu
ADD ready_wait.py /usr/bin/ready_wait
ADD ready_wait.yaml /etc/ready_wait.yaml
...
CMD ready_wait && /entrypoint.sh
```
