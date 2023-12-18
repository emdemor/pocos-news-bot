-include .env

export

PROJECT_NAME := bot

CHROMA_IMAGE := $(PROJECT_NAME)_chroma
JUPYTER_IMAGE := $(PROJECT_NAME)_jupyter

DOCKER_COMPOSE_FILEPATH := docker/docker-compose.yml
CHROMA_DOCKERFILE_PATH := docker/Dockerfile.chroma
JUPYTER_DOCKERFILE_PATH := docker/Dockerfile.jupyter

CHROMA_PORT ?= 8000
JUPYTER_PORT ?= 8888

DOCKER_RUN := docker run --rm -t
DOCKER_RUN_ITERACTIVE := $(DOCKER_RUN) -i
DOCKER_ENV := --env-file .env
DOCKER_COMPOSE := docker-compose -f $(DOCKER_COMPOSE_FILEPATH)

RUNNING_CONTAINERS = $(docker ps -a -q)

RUN_JUPYTER := $(DOCKER_RUN) $(DOCKER_ENV) -p $(JUPYTER_PORT):$(JUPYTER_PORT) $(JUPYTER_IMAGE)

up:
	$(DOCKER_COMPOSE) up --build

down:
	$(DOCKER_COMPOSE) down

build-jupyter:
	docker build -f $(JUPYTER_DOCKERFILE_PATH) -t $(JUPYTER_IMAGE) .

run-jupyter:
	$(RUN_JUPYTER)

shell-jupyter:
	$(DOCKER_RUN_ITERACTIVE) $(DOCKER_ENV) -p $(JUPYTER_PORT):$(JUPYTER_PORT) $(JUPYTER_IMAGE) /bin/bash
