# Visualization of Structural Monitoring Data of the Penobscot Narrows Bridge

## Development

Local development uses Docker and a devcontainer-compatible IDE to run a local
copy of the entire visualization stack. This requires the following dependencies:

- [docker](https://docs.docker.com/get-docker/)
- [devcontainers for vscode](https://code.visualstudio.com/docs/devcontainers/containers)

Starting the dev container extension, or running `docker compose up` from `.devcontainer`,
will start 3 containers. Note that the configuration is not secure, and these should only be
run from a local workstation with a firewall.

1. A Debian-based Python container for development work. This contains all of the dependencies for our code.
2. InfluxDB with some example data.
3. Grafana with some pre-configured dashboards.

The InfluxDB seed data can be found in `.devcontainer/influx/example-data.csv`. At this time,
it is based on the 081523 example spreadsheet. It has been [formatted](https://docs.influxdata.com/influxdb/cloud/reference/syntax/annotated-csv/#annotated-csv-in-flux)
so that it can be imported into Influx.
Import is performed with the `.devcontainer/influx/influx-setup.sh` script.

### How To

To reset Influx/Grafana databases or use different seed data:

```
cd .devcontainer
docker compose down -v
docker compose build
```

To use the Influx Web GUI with the dev container stack running:

1. Visit http://localhost:8086
2. Credentials are zatan / Zatan123!
3. Check out the "Data Explorer" on the left.

We are using Influx 2.0, which means that [Flux](https://docs.influxdata.com/influxdb/v2/query-data/get-started/)
is the preferred query langauge.

To use the Influx CLI (this is mostly good for database admin, not querying):

1. From the `.devcontainer` directory...
2. Run `docker compose exec influxdb <YOUR COMMAND HERE>`

To use Grafana

1. Visit http://localhost:3000
2. Credentials are admin / admin
