# PremiScale

PremiScale brings autoscaling to on-premise infrastructure, with a particular focus on integrating with the [Kubernetes autoscaler](https://github.com/kubernetes/autoscaler).

<!-- [[[cog
import subprocess
import cog

cog.outl(f'```text\n$ premiscale --help\n{subprocess.run("poetry run premiscale --help".split(" "), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()}\n```')
]]] -->
```text
$ premiscale --help
usage: premiscale [-h] [--token TOKEN] [-d] [-c CONFIG] [--validate]
                  [--platform PLATFORM] [--version] [--pid-file PID_FILE]
                  [--log-level {info,error,warn,debug}]
                  [--log-file LOG_FILE | --log-stdout] [--cacert CACERT]

PremiScale autoscaler. © PremiScale, Inc. 2024

options:
  -h, --help            show this help message and exit
  --token TOKEN         Platform registration token. (default: )
  -d, --daemon          Start agent as a daemon. (default: False)
  -c CONFIG, --config CONFIG
                        Configuration file path to use. (default:
                        /opt/premiscale/config.yaml)
  --validate            Validate the provided configuration file and exit.
                        (default: False)
  --platform PLATFORM   URL of the PremiScale platform. (default:
                        app.premiscale.com)
  --version             Display agent version. (default: False)
  --pid-file PID_FILE   Pidfile name to use for the agent daemon. (default:
                        /opt/premiscale/premiscale.pid)
  --log-level {info,error,warn,debug}
                        Set the logging level. (default: info)
  --log-file LOG_FILE   Specify the file the service logs to if --log-stdout
                        is not set. (default: /opt/premiscale/agent.log)
  --log-stdout          Log to stdout (for use in containerized deployments).
                        (default: False)
  --cacert CACERT       Path to the certificate file (for use with self-signed
                        certificates). (default: )

```
<!-- [[[end]]] (checksum: 5fd99b57734fed0f90c8f06beab12676) (checksum: ) -->

## Architecture

PremiScale is a controller that works by

See the [architecture diagram](https://drive.google.com/file/d/1hjwaMVQESdU2KffEJ4FpWDC1hjVHCLZX/view?usp=sharing) for PremiScale, or check out the diagram below, for an overview of just the controller.

<p align="center" width="100%">
  <img width="100%" src="img/premiscale-architecture-controller.png" alt="premiscale architecture controller">
</p>

## Install

### Docker

```shell
docker run -itd
```

### Kubernetes

```shell
helm upgrade --install
```

## Development

### Dependencies

Install [asdf](https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies), followed by running `asdf install` in the root of this project.

### Local

```shell
yarn compose:up
```

This will bring up a number of services, including platform services that the controller registers and connects to for billing. When you're finished, run

```shell
yarn compose:down
```

### Remote

Connect to your development cluster of choice with kubectl access, followed by

```shell
devspace
```

This will bring up a development stack in a local or remote Kubernetes cluster of your choice.

### Tests

Run unit tests with

```shell
poetry run pytest tests/unit
```

e2e tests against a live environment with

```shell
poetry run pytest tests/e2e
```

And coverage against the codebase with

```shell
poetry run coverage run -m pytest
poetry run coverage report -m pytest
```
