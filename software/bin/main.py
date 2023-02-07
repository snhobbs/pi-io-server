import click
import logging
from io_control import main

@click.group()
class gr1:
    pass


@gr1.command(name="main")
def run_main(directory, device, address):
    main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gr1()
