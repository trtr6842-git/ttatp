#! .env/bin/python3

import subinitial.automation as automation
import time

testroot = automation.locate_testroot()
testroot.insert_path()  # insert testroot into sys.path for consistent file imports!

from src.fixture import *
from src.connections import connection_manager


def main():
    fixture.stm.connect()
    fixture.stm.set_lcd_text('Scratchpad')
    fixture.stm.set_lcd_text('', 1)
    fixture.stm.set_dout_state(2, 1)
    fixture.stm.set_vdut(0)           
    time.sleep(0.5)
    fixture.stm.set_vdut(5)



if __name__ == "__main__":
    main()
