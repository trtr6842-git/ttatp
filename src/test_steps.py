""" This module contains all the user-defined test steps for the ATP """
import logging
import subinitial.automation as automation
from src.fixture import *

from pathlib import Path
import re

logger = logging.getLogger(__name__)


# class TemplateStep(automation.Step):
#     class Data:
#         def __init__(data):
#             # Configuration fields can control how the test runs, and can be
#             # overriden in construction (see atp.py:define_test() method) as well
#             # as overriden via config.csv's StepTable 
#             data.try_count = 2
#             data.limit_max = 15.0

#             # Measurements fields
#             data.measurement: float = None

#     def criteria(self, data: Data):
#         # These assertions load into the test tree before the run, and are evaluated after procedure (below) completes.
#         self.assert_inrange('DMM Measurement', measurement=data.measurement, min=-1.0, max=data.limit_max)
#         self.assert_record('Try Count', measurement=data.try_count)

#     def procedure(self, data: Data):
#         for i in range(data.try_count):
#             self.report_info(f"DMM Voltage Measurement, Attempt# {i+1}")
#             try:
#                 data.measurement = dmm.measure_voltage()
#                 break
#             except Exception as ex:
#                 self.report_error(ex)


#     def teardown(self, data: Data):
#         # Safely return to normal state after procedure (runs even if procedure exits early due to an error)
#         pass

class DutDetect(automation.Step):
    class Data:
        def __init__(data):
            # Config Fields
            data.vdut = 0.5
            data.min_threshold = 0.25

            # Measurements
            data.measurement: float = None
    
    def criteria(self, data: Data):
        self.assert_greaterthan('DUT 5V Sense', measurement=data.measurement, min=data.min_threshold, units='V')

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Detecting DUT', 1)
        fixture.stm.set_vdut(data.vdut)
        time.sleep(0.1)
        data.measurement = fixture.measure_tx_5v()
    
    def teardown(self, data: Data):
        fixture.stm.set_vdut(0)


class PowerUp(automation.Step):
    class Data:
        def __init__(data, imax=0.5, boot=False):
            # Config Fields
            data.vdut_set = 5.0
            data.vdut_min = 4.8
            data.vdut_max = 5.2

            data.idut_min = 0.001
            data.idut_max = imax
            data.imax = imax

            data.dut_3v3_min = 3.0
            data.dut_3v3_max = 3.6

            data.dut_5v_min = 4.2
            data.dut_5v_max = 5.2

            data.boot = boot

            # Measurements
            data.dut_5v: float = None
            data.dut_3v3: float = None
            data.idut: float = None
            data.vdut: float = None
    
    def criteria(self, data: Data):
        self.assert_inrange('Measured Vdut', data.vdut, data.vdut_min, data.vdut_max, units='V')
        self.assert_inrange('Measured Idut', data.idut, data.idut_min, data.idut_max, units='A')
        self.assert_inrange('DUT 5V', data.dut_5v, data.dut_5v_min, data.dut_5v_max, units='V')
        self.assert_inrange('DUT 3V3', data.dut_3v3, data.dut_3v3_min, data.dut_3v3_max, units='V')

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Power Up', 0)  
        if data.boot:
            fixture.stm.set_dout_state(2, 0) # Assert low to trigger bootchecker if already programmed
        else:
            fixture.stm.set_dout_state(2, 1)
        fixture.stm.set_vdut(data.vdut_set)
        time.sleep(0.1)
        if data.boot:
            time.sleep(0.3)
        data.idut = fixture.stm.measure_idut()
        data.vdut = fixture.stm.measure_vdut()
        data.dut_5v = fixture.measure_tx_5v()
        data.dut_3v3 = fixture.measure_tx_3v3()
    
    def teardown(self, data: Data):
        fixture.stm.set_vdut(0)


class EraseAll(automation.Step):
    class Data:
        def __init__(data):
            # Measurements
            data.erase_result: bool = None
    
    def criteria(self, data: Data):
        self.assert_true('Erase Success', data.erase_result)

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Erase Flash', 1)
        PORT = "/dev/ttyAMA3"
        res = fixture.run_rpi(["stm32flash", "-o", PORT])
        if res.returncode == 0:
            data.erase_result = True
        else:
            data.erase_result = False


class FlashMain(automation.Step):
    class Data:
        def __init__(data):
            # Config Fields
            data.bin_path = "tx/stm32/RCTF_WFTX_REVA_STM32G030C8T6.bin"

            # Measurements
            data.flash_result: bool = None
    
    def criteria(self, data: Data):
        self.assert_true('Flash Main', data.flash_result)

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Flash Main', 1)
        PORT = "/dev/ttyAMA3"

        res = fixture.run_rpi(["stm32flash", "-b", "1000000", "-w", data.bin_path, "-v", "-S", "0x08000800", PORT])
        if res.returncode == 0:
            data.flash_result = True
        else:
            data.flash_result = False


class FlashBootchecker(automation.Step):
    class Data:
        def __init__(data):
            # Config Fields
            data.bin_path = "tx/stm32/STM32G030C8T6_RCTF_TTTX_REVA_BOOTCHECKER.bin"

            # Measurements
            data.flash_result: bool = None
    
    def criteria(self, data: Data):
        self.assert_true('Flash Bootchecker', data.flash_result)

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Flash Bootcheck', 1)
        PORT = "/dev/ttyAMA3"

        res = fixture.run_rpi(["stm32flash", "-b", "115200", "-w", data.bin_path, "-v", "-S", "0x08000000", PORT])
        if res.returncode == 0:
            data.flash_result = True
        else:
            data.flash_result = False


class ConnectDutUart(automation.Step):
    class Data:
        def __init__(data):
            pass
    
    def criteria(self, data: Data):
        pass

    def procedure(self, data: Data):
        fixture.dut.connect()
        fixture.dut.flush_rx()

    def teardown(self, data: Data):
        fixture.dut.disconnect()


class GetUid(automation.Step):
    class Data:
        def __init__(data):
            data.uid = None
    
    def criteria(self, data: Data):
        self.assert_record('UID', data.uid)
        self.assert_true('UID Found', data.uid is not None)

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Get UID', 1)
        t_start = time.time()

        while time.time() - t_start < 3:
            if fixture.dut.ser.in_waiting > 3:
                break
        time.sleep(0.15)

        rx = fixture.dut.ser.read_all()
        print(rx)
        rx_str = rx.decode('utf-8')
        print(rx_str)
        match = re.search(r'UID: (\d{30})', rx_str)
    
        if match:
            data.uid = match.group(1)  # Return the UID value
            fixture.dut_uid = data.uid
            

    def teardown(self, data: Data):
        pass

    

