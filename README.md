# Visualization of Structural Monitoring Data of the Penobscot Narrows Bridge

## Development

The project is primarily developed in Python, and follows the 
[Python Packaging User Guide](https://packaging.python.org/en/latest/overview/),
with [`hatch`](https://hatch.pypa.io/latest/) used as a build and packaging tool.

### Getting Started

Local development uses Docker and a devcontainer-compatible IDE to run a local
copy of the entire visualization stack. This requires the following dependencies:

- [docker](https://docs.docker.com/get-docker/)
- [devcontainers for vscode](https://code.visualstudio.com/docs/devcontainers/containers)

Once Docker is installed, use the "Dev Containers: Open Folder in Container" command in
vscode. If you are on Windows, make sure that Git is not changing the line endings
for files inside your container.

Starting the dev container extension, or running `docker compose up` from `.devcontainer`,
will start 3 containers. Note that the configuration is not secure, and these should only be
run from a local workstation with a firewall.

1. A Debian-based Python container for development work. This contains all of the dependencies for our code. VSCode is running as user `work` within the container.
Port 4000 + 5000 are exposed to localhost so you can access Flask and Python debugging.
2. InfluxDB with some example data, on port 8086.
3. Grafana with some pre-configured dashboards, on port 3000.

Once your dev container is running, you can use `hatch` to run your code.

Run a single script:
```
hatch run <script>
```

Grab a shell
```
hatch shell
```


### Developer How To

To manually reset Influx/Grafana databases:

```
cd .devcontainer
docker compose down -v
docker compose build
```
Or you can run the "Dev Containers: Rebuild Container" command from inside Vscode.


To run a shell inside the dev container:

```
docker exec -it vismod-dev bash
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


Add new Pip Dependencies

Find the `dependencies` section in `pyproject.toml` and add it to the list.
`hatch` will automatically install the next time you start a shell or run
a command. If you currently have a shell open, restart it.

Run Tests using `pytest`

```
hatch run test
```

## Deployment

### Packages

```
python3 -m build --wheel
```

### Server

The visualization project can be entirely deployed to a live server
using only the provided Github Actions and Ansible Playbooks. The `DeployProject`
job runs on Actions after a push to the `main` branch (such as after a PR).
The job target can be controlled via a Github Secret.

The Ansible Playbooks are found in `/infrastructure`. Running them requires
Ansible to be installed.

To run Ansible manually, add the correct SSH private key to your agent,
and then try

```
ansible-playbook -i inventory.yaml deploy-prod.yaml
```
