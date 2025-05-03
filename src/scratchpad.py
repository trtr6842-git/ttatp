#! .env/bin/python3

import subinitial.automation as automation

testroot = automation.locate_testroot()
testroot.insert_path()  # insert testroot into sys.path for consistent file imports!

from src.fixture import *
from src.connections import connection_manager


def main():
    something_hacky()


def something_hacky():
    connection_manager.connect()
    print(f"DMM Measured {dmm.measure_voltage()}V")


if __name__ == "__main__":
    main()
