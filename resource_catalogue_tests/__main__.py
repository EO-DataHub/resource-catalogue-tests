import logging

import pytest


def main():
    try:
        results = pytest.main(["."])
    except Exception as e:
        logging.info(e)
        raise

    if results != 0:
        raise Exception("Not all tests have passed")


if __name__ == "__main__":
    main()
