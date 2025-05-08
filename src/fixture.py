import logging
import os
import re
import subinitial.automation as automation
from subinitial.automation import Parameter
from src.mockvisadmm import MockVisaDMM


# Setup logging
logger = logging.getLogger(__name__)


# Global configuration
class Config(automation.ConfigStruct):
    dmm_ipv4 = Parameter.String("192.168.1.30")
    """DMM Hostname or ipv4"""

config = automation.get_testconfig(schema=Config)  # read config.csv
args = automation.get_testargs()
state = automation.get_teststate()    # read state.json


# Global equipment objects
dmm = MockVisaDMM()


class Fixture:
    """Generic fixture object to wrap fixture function helpers into"""
    def __init__(self):
        pass
    
    def get_rpi_serial(self):
        output = os.popen('cat /proc/cpuinfo | grep Serial').read()
        return re.search(r':\s(.{16})', output).group(1)
    
    
        
        
        

fixture = Fixture()
