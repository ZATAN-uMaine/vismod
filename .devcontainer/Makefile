# Note: this file is only necessary if you're not using the devcontainer vscode extension

env:
	docker compose run --rm devcontainer /bin/bash

build:
	docker compose build devcontainer
down:
	docker compose down -v
	docker volume rm      devcontainer_influxdb_config
    docker volume rm      devcontainer_influxdb_data
    docker volume rm      vismod_devcontainer_grafana_storage
    docker volume rm      vismod_devcontainer_influx_config
    docker volume rm      vismod_devcontainer_influx_storage
    docker volume rm      vscode
