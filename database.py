import configparser

config = configparser.ConfigParser()
config.read("config.ini")


def get_ordenes(page: int = 1, page_size: int = 50):
    raise NotImplementedError("database layer not yet implemented")
