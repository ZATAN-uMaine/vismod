# Visualization of Structural Monitoring Data of the Penobscot Narrows Bridge

## Development

The project is primarily developed in Python, and follows the 
[Python Packaging User Guide](https://packaging.python.org/en/latest/overview/),
with [`hatch`](https://hatch.pypa.io/latest/) used as a build and packaging tool.
All the vismod packages and development tools are available as hatch scripts.

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

Development also uses [dotenv](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)
for managing environment variables and secrets. You will need to copy the
`.env.example` file to `.env` before code will run.

Once your dev container is running, you can use `hatch` to run your code.

Run a single script:
```
hatch run <script>
```

Grab a shell
```
hatch shell
```

Run `vismod_processing`

```
hatch run process
```

Run web server

```
hatch run web
```

Run Tests
```
hatch run test
```

### Developer How To

#### Dev containers

To manually reset Influx database:

```
cd .devcontainer
docker compose down -v
```
The, list docker volumes with `docker volume ls` and remove all of the
the Influx ones. They will be reset after the containers are rebuilt.


To run a shell inside the dev container:

```
docker exec -it vismod-dev bash
```

#### Influx

To use the Influx Web GUI with the dev container stack running:

1. Visit http://localhost:8086
2. Credentials are zatan / Zatan123!
3. Check out the "Data Explorer" on the left.

We are using Influx 2.0, which means that [Flux](https://docs.influxdata.com/influxdb/v2/query-data/get-started/)
is the preferred query langauge.

To use the Influx CLI (this is mostly good for database admin, not querying):

1. From the `.devcontainer` directory...
2. Run `docker compose exec influx <YOUR COMMAND HERE>`


#### Python

Add new Pip Dependencies

Find the `dependencies` section in `pyproject.toml` and add it to the list.
`hatch` will automatically install the next time you start a shell or run
a command. If you currently have a shell open, restart it.

Run Tests (using `pytest` internally)

```
hatch run test
```

## Deployment

### Packages

```
hatch build
```

We create a single package that contains both the vismod_process and vismod_web
module. This package can be installed with pip, and then you can run both modules
separately.

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
ansible-playbook -i inventory.yaml deploy.yaml
```


# TSP Release Schedule

Zach Scott, Andres Vargas, Tyler Harwood,	Alex Bourgoin, Nick Dieffenbacher-Krall

Set a Feature freeze date - what is the date.
Feb 26th 2024

Set a CODE freeze date - what is the date.
March 27, 2024

Decide on a Release candidate name. This will be the code version from which all defects will be removed ( i.e v0.1a, red, blackbird, etc.)
	Verona

Fix (a) release date(s)  (Note:  If you are beta testing your code, you will have more than one release date.) Also keep in mind any presentations you'll be presenting.
v0.1 to be released on the 26th of February.
The PNB Portal will be deployed continuously upon a successful push to the main branch in Github.

Fix release dates for your User Guide and Administrator Manuals  (Note:  Plan to do a feature freeze before the date(s).)
	March 25, 2024 - AM v0.1
	April 13, 2024 - AM v1.0
	April 6, 2024 - UG v0.1
	April 22, 2024 - UG v1.0

