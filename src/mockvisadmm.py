""" This module provides a template wrapper for a USB driver. You can wrap an existing python driver here, or implement your own driver as needed. """

import logging
import random

logger = logging.getLogger(__name__)


class MockVisaDMM:
    @property
    def host(self):
        return self._host

    def __init__(self):
        """ Initialize the driver without actually connecting yet """
        self._host: str | None = None

    def connect(self, host: str):
        """ Form an active connection to the device with initial configuration """
        self._host = host

    def close(self):
        """ Safely disconnect from the device and return it to it's original state """
        self._host = None

    def measure_voltage(self):
        """ Request a voltage measurement to be performed by the MockVisaDMM """
        if self._host is None:
            raise Exception("MockVisaDMM is not yet connected!")
        return random.random() * 10
