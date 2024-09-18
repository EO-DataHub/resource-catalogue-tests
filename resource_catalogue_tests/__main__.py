import logging

import pytest


def main():
    try:
        pytest.main(["."])
    except Exception as e:
        logging.info(e)
        raise


if __name__ == "__main__":
    main()
