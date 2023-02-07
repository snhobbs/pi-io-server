import logging
import socket
import pickle


def make_run_url(branch="data-view", sn=None, fwv=None, time=None):
    if sn is None:
        sn = "*"
    if fwv is None:
        fwv = "*"
    if time is None:
        time = "*"
    time = str(time).replace(".", "_")
    return "/" + "/".join([branch, sn, fwv, time])


def ParseUrl(pathname):
    if isinstance(pathname, bytes):
        pathname = pathname.decode("utf-8")
    assert isinstance(pathname, str)
    path_sections = pathname.strip("/").split("/")
    sn, fwv, time = None, None, None
    branch = "main"
    if len(path_sections) > 0:
        branch = path_sections[0]
    if len(path_sections) > 1:
        sn = path_sections[1]
    if len(path_sections) > 2:
        fwv = path_sections[2]
    if len(path_sections) > 3:
        time = path_sections[3]
        time.replace("_", ".")
    logging.getLogger().info("%s %s %s", sn, fwv, time)
    return branch, sn, fwv, time



def send_command(command, server_host, server_port):
    """
    Send a ControlCommand to the give host and port
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))
        sock.sendall(pickle.dumps(ControlCommand(command)))


def get_run_status(server_host, server_port):
    run_status = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))
        sock.sendall(pickle.dumps(ControlCommand("print")))
        received = sock.recv(1024)
        try:
            run_status = pickle.loads(received)
        except (pickle.UnpicklingError, EOFError) as e:
            logging.getLogger().warning(e)
    return run_status.__dict__
