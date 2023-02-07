import logging
import time
from enum import Enum
import pickle
from multiprocessing import Process, Queue
import sys
import socketserver
import click
from io_control import main, SystemSettings


class ProcessWrapper(Process):
    pass



def main_wrapper(log, queue, command_queue, base_dir):
    return main(
        log,
        queue=queue,
        command_queue=command_queue,
    )


# takes utc time and return seconds since
def seconds_since(start):
    return time.time() - start


class RunState(Enum):
    kInitial = 0
    kRunning = 1
    kStopped = 2
    kFinished = 3


class RunStatus:
    def __init__(self, base_dir):
        self._base_dir = base_dir
        self._queue = Queue()
        self._command_queue = Queue()
        self._process = Process(
            target=main_wrapper,
            args=(
                logging.getLogger(),
                self._queue,
                self._command_queue,
                self._base_dir,
            ),
        )
        self._state = RunState.kInitial
        self._last_status = ProcessStatus(0, 0, "No Data")
        self._start_time = None
        self.reset()

    @property
    def running_time(self):
        return seconds_since(self._start_time)

    def update_state(self):
        if self._state == RunState.kInitial:
            pass
        elif self._state == RunState.kRunning:
            while not self._queue.empty():
                self._last_status = self._queue.get_nowait()
            if not self.process_running():
                if self._process.exitcode != 0:
                    self._last_status = ProcessStatus(0, 0, "Error, Reset to Clear")
                else:
                    pass
        elif self._state == RunState.kFinished:
            pass
        elif self._state == RunState.kStopped:
            pass
        else:
            assert 0  # unknown state

    @property
    def status(self):
        self.update_state()
        return self._last_status

    def process_running(self):
        return self._process.is_alive()

    def reset(self):
        logging.getLogger().info("Reset Process")
        self._last_status = ProcessStatus(0, 0, "Ready")
        self._state = RunState.kInitial

        # Send stop command and wait till the process finishes
        if self.process_running():
            self._command_queue.put("stop")

        start = time.time()
        kMaxNormalStopTime = 5
        while self.process_running() and time.time() - start < kMaxNormalStopTime:
            time.sleep(0.1)

        while self.process_running():
            # self._process.terminate()
            self._process.kill()
        self._process.close()
        self._queue.close()
        self._command_queue.close()

        self._queue = Queue()
        self._command_queue = Queue()
        self._process = ProcessWrapper(
            target=main_wrapper,
            args=(
                logging.getLogger(),
                self._queue,
                self._command_queue,
                self._base_dir,
            ),
        )

    @property
    def finished(self):
        return not self._process.is_alive() #  and self._process.started

    def stop_process(self):
        self._state = RunState.kStopped
        self.reset()

    def start_process(self):
        self._state = RunState.kRunning
        try:
            print(self._process)
            self._process.start()
            print("Starting Process")
        except AssertionError as e:
            self._last_status = ProcessStatus(0, 0, "Error, Reset to Clear")
            print("Assertion Error", e)
        print(self._process)


kDataDir = SystemSettings.kDataDir
run_status = RunStatus(kDataDir)

def get_run_status():
    return run_status


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        if len(self.data) > 0:
            logging.getLogger().info("%d wrote:", self.client_address[0])
            try:
                obj = pickle.loads(self.data)
                logging.getLogger().info("ControlCommand %s", str(obj))
                if obj.stop:
                    get_run_status().stop_process()
                elif obj.start:
                    get_run_status().start_process()
            except pickle.UnpicklingError:
                pass
            except Exception:
                raise

        state = get_run_status().status
        logging.getLogger().info(str(state))
        pickled = pickle.dumps(state)
        self.request.sendall(pickled)


@click.command()
@click.option("--host", "-h", type=str, default="localhost", help="IP Address")
@click.option("--port", "-p", type=int, default=8000, help="Port")
def run_server(host, port):
    with socketserver.TCPServer((host, port), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

if __name__ == "__main__":
    logging.basicConfig()
    run_server()
    # Create the server, binding to localhost on port 9999
