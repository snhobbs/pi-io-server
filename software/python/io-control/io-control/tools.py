def exit_command_received(command_queue):
    if not command_queue.empty():  # ignores all commands that are not stop
        d = command_queue.get_nowait()
        if d == "stop":
            return True
    return False
