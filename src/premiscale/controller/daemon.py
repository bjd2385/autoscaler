"""
Define subprocesses encapsulating each control loop.
"""


import concurrent.futures
import multiprocessing as mp
import logging
import signal
import sys
import concurrent
import os

from multiprocessing.queues import Queue
from typing import cast
from setproctitle import setproctitle
from daemon import DaemonContext, pidfile

from premiscale.config._config import Config
from premiscale.controller.platform import Platform, register
from premiscale.controller.autoscaling import ASG
from premiscale.controller.metrics import Metrics
from premiscale.controller.reconciliation import Reconcile
from premiscale.healthcheck import app as healthcheck


log = logging.getLogger(__name__)


def start(
        working_dir: str,
        pid_file: str,
        controller_config: Config,
        controller_version: str,
        token: str,
        host: str,
        cacert: str
    ) -> int:
    """
    Start our four daemon processes passing along relevant configuration.

    Args:
        working_dir (str): working directory for this daemon.
        pid_file (str): PID file to use for the main daemon process.
        controller_config (Config): controller config object.
        controller_version (str): controller version (from the package metadata).
        token (str): controller registration token.
        host (str): PremiScale platform host.
        cacert (str): Path to the certificate file (for use with self-signed certificates).

    Returns:
        int: return code.
    """
    setproctitle('premiscale')

    # Start the healthcheck API in a separate thread as a daemon.
    with concurrent.futures.ThreadPoolExecutor() as main_process_tp:
        main_process_tp.submit(
            healthcheck.run, host=host, port=8085
        )

    with concurrent.futures.ProcessPoolExecutor() as executor, mp.Manager() as manager:
        # DaemonContext(
        #     stdin=sys.stdin,
        #     stdout=sys.stdout,
        #     stderr=sys.stderr,
        #     # files_preserve=[],
        #     detach_process=False,
        #     prevent_core=True,
        #     pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        #     working_directory=working_dir,
        #     signal_map={
        #         signal.SIGTERM: executor.shutdown,
        #         signal.SIGHUP: executor.shutdown,
        #         signal.SIGINT: executor.shutdown,
        #     }
        # ):

        autoscaling_action_queue: Queue = cast(Queue, manager.Queue())
        platform_message_queue: Queue = cast(Queue, manager.Queue())

        processes = [
            # Platform websocket connection subprocess. Maintains registration, connection and data stream -> premiscale platform).
            executor.submit(
                Platform(
                    registration=registration,
                    version=controller_version,
                    host=f'wss://{host}',
                    path='agent/websocket',
                    cacert=cacert
                ),
                platform_message_queue
            ) if (registration := register(
                token=token,
                version=controller_version,
                host=f'https://{host}',
                path='agent/registration',
                cacert=cacert
            )) else None,

            # Autoscaling controller subprocess (works on Actions in the ASG queue)
            executor.submit(
                ASG(),
                autoscaling_action_queue
            ),

            # Host metrics collection subprocess (populates metrics database)
            executor.submit(
                Metrics(
                    controller_config.controller_databases_metrics_connection() # type: ignore
                )
            ),

            # Metrics <-> state database reconciliation subprocess (creates actions on the ASGs queue)
            executor.submit(
                Reconcile(
                    controller_config.controller_databases_state_connection(), # type: ignore
                    controller_config.controller_databases_metrics_connection() # type: ignore
                ),
                autoscaling_action_queue,
                platform_message_queue
            )
        ]

        for process in processes:
            if process is not None:
                process.result()

    return 0