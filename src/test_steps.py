""" This module contains all the user-defined test steps for the ATP """
import logging
import subinitial.automation as automation
from src.fixture import *

logger = logging.getLogger(__name__)


class TemplateStep(automation.Step):
    class Data:
        def __init__(data):
            # Configuration fields can control how the test runs, and can be
            # overriden in construction (see atp.py:define_test() method) as well
            # as overriden via config.csv's StepTable 
            data.try_count = 2
            data.limit_max = 15.0

            # Measurements fields
            data.measurement: float = None

    def criteria(self, data: Data):
        # These assertions load into the test tree before the run, and are evaluated after procedure (below) completes.
        self.assert_inrange('DMM Measurement', measurement=data.measurement, min=-1.0, max=data.limit_max)
        self.assert_record('Try Count', measurement=data.try_count)

    def procedure(self, data: Data):
        for i in range(data.try_count):
            self.report_info(f"DMM Voltage Measurement, Attempt# {i+1}")
            try:
                data.measurement = dmm.measure_voltage()
                break
            except Exception as ex:
                self.report_error(ex)


    def teardown(self, data: Data):
        # Safely return to normal state after procedure (runs even if procedure exits early due to an error)
        pass
