# PremiScale

PremiScale is a controller that brings autoscaling of virtual infrastructure to local, self-hosted and private datacenters, with a particular focus on integrating with the Kubernetes cluster [autoscaler](https://github.com/kubernetes/autoscaler).

## Architecture

PremiScale is a controller that administers hosts and virtual machines by leveraging [libvirt](https://libvirt.org/). Libvirt is a very flexible open source hypervisor API and daemon that runs on hosts.

The controller can be configured to run in two different modes, including a `kubernetes` (the default) and a `standalone` mode.

See also the [architecture diagram](https://drive.google.com/file/d/1hjwaMVQESdU2KffEJ4FpWDC1hjVHCLZX/view?usp=sharing) for PremiScale.

### Kubernetes

Starting the controller in `kubernetes` mode (the default) starts relevant components of the controller that allow it to interface with the cluster autoscaler.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller_internal_autoscaler_disabled.png" alt="premiscale architecture controller">
</p>

### Standalone

In `standalone` mode, the controller starts its own metrics collection process. Users are required to provide a list of hosts on which virtual machines can be created. Users are also required to provide a list of autoscaling groups into which virtual machines the controller manages are organized.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller.png" alt="premiscale architecture controller">
</p>

## Configuration

The controller is configured in a couple ways, including its command line interface, environment variables (as indicated in the help text below), and through the required config file (all versions of which are documented [here](./src/premiscale/config/docs/README.md) in this repository).

<!-- [[[cog
import subprocess
import cog

cog.outl(f'```text\n$ premiscale --help\n{subprocess.run("poetry run premiscale --help".split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()}\n```')
]]] -->
```text
$ premiscale --help

```
<!-- [[[end]]] (checksum: 8cebe6abdefb1648e599b1c9ea8c441d) (checksum: ) -->

## Installation

This project is intended to be deployed to Kubernetes, whether you intend to integrate with the cluster autoscaler or not.

See the Helm [chart README](https://github.com/premiscale/premiscale/tree/master/helm/premiscale) for an overview of controller installation.

## Development

### Dependencies

Install [asdf](https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies), followed by running `asdf install` in the root of this project.

### Docker Compose

> **Note:** Some tweaks may need to be made to the repository's [compose.yaml](./compose.yaml) file to get the stack to run on your system.

```shell
yarn compose:up
```

This will bring up a number of local services for running the agent. To tear the stack down, simply run

```shell
yarn compose:down
```

### Kubernetes

Connect to your development cluster of choice with kubectl access, followed by

```shell
devspace
```

This will bring up a development stack in a local or remote Kubernetes cluster of your choice.

#### Minikube

To start a local development minikube cluster for deploying the devspace stack to, run

```shell
yarn minikube:up
```

When you're done and want to clean it up, run

```shell
yarn minikube:down
```

This cluster can also used for [running e2e tests](#end-to-end-tests), locally.

### Unit tests

Run [unit tests](./src/tests/unit/) with

```shell
yarn test:unit
```

Unit tests require you to install the relevant dependencies in your local virtualenv with poetry (`poetry install`).

### End-to-end tests

Run e2e tests against a live (local) environment with

```shell
yarn test:e2e
```

This command will

1. Stand up a local 2-node minikube cluster with 4 cores, 4GiB memory and 30GiB storage, each. *(Modify [./scripts/minikube.sh](./scripts/minikube.sh) if these resources are unsuitable for your local development environment.)*
2. Create a `localhost` docker registry redirect container based on `socat`.
3. Build both e2e and PremiScale controller container images, as well as push these images to the local redirect for minikube to access.
4. Installs both [`premiscale`](./helm/premiscale/) and [`premiscale-e2e`](./helm/premiscale-e2e/) Helm charts.
5. Runs the [e2e tests](./src/tests/e2e/).
6. Tear down the cluster and local registry, as well as cleans up locally-built artifacts.

### Coverage

Test coverage against the codebase with

```shell
poetry run coverage run -m pytest
poetry run coverage report -m pytest
```