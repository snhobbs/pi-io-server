import logging


class FakeQueue:
    @classmethod
    def put(cls, arg):
        logging.getLogger().info(arg)

    @classmethod
    def empty(cls):
        return True
