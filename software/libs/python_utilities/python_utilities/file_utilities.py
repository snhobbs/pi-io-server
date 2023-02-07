import datetime
import os


def make_time_from_file_timestamp(file_string):
    split = file_string.split("_")
    isoformat = ".".join(split[-2:])
    return datetime.datetime.fromisoformat(isoformat)


def make_file_timestamp(now=None):
    if now is None:
        now = datetime.datetime.now()
    return now.isoformat().replace(".", "_")


def list_subdirectories(dir_name):
    subs = []
    for name in os.listdir(dir_name):
        dname = os.path.join(dir_name, name)
        if os.path.isdir(dname):
            subs.append(dname)
    return subs
