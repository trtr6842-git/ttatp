"""
This module is responsible for handling connection logic to test equipment, services, etc.
"""
import logging
import subinitial.automation as automation
from src.fixture import *

logger = logging.getLogger(__name__)


class DmmLogic(automation.PingConnectionLogic):
    def get_host_and_name(self) -> tuple[str, str]:
        return config.dmm_ipv4, 'MockVisaDMM'
    
    def make_connection(self):
        dmm.connect(config.dmm_ipv4)

    def disconnect(self):
        dmm.close()


connection_manager = automation.ConnectionManager()
connection_manager.add(DmmLogic(is_asynchronous=True))
