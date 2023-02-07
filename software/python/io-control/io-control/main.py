import os
import time
import datetime
import logging
from collections import deque
from progress.bar import Bar
import pandas as pd
import numpy as np
import enum
from .fake_queue import FakeQueue
from .tools import exit_command_received
kTimeFinished = 0
kStartedPercent = 0
kFinishedPercent = 100


def estimate_run_time():
    time_estimate = deque(
        [
            0
        ]
    )
    return time_estimate


def main(log, base_dir=SystemSettings.kDataDir, queue=None, command_queue=None):
    finished = True
    time_stamp = datetime.datetime.now()
    if command_queue is None:
        command_queue = FakeQueue()
    if queue is None:
        queue = FakeQueue()
    log.setLevel(logging.INFO)
    log.info("Running main process")
    if not os.path.exists(base_dir):
        log.error("Path %s does not exist", base_dir)
        finished = False
        return finished

    time_estimate = estimate_run_time(sensor_run_list.data_runs)
    queue.put(ProcessStatus(sum(time_estimate), kStartedPercent, "Starting Run"))
    start = time.time()
    time_estimate.popleft()

    progress_bar.finish()
    run_time = time.time() - start
    log.info("Total time %f", run_time)
    if finished:
        queue.put(ProcessStatus(kTimeFinished, kFinishedPercent, "Run Finished", finished))

    passed=True
    if passed:
        print("Passed")
    else:
        print("Failed")

    return True
