#! .venv/bin/python
import os
from pathlib import Path
import logging
import subinitial.automation as automation
from src.test_steps import *
from src.connections import connection_manager


logger = logging.getLogger(__name__)


class Atp(automation.TestDefinition):
    def init(self):
        self.title = "RCTF TRAIL TRACER ATP"
        # ATP version/revision, displaying in TestCenter and generated SiSteps docs
        self.version = "v{major}.{minor}.{patch}".format(major=0, minor=1, patch=0)
        

    class Data:
        def __init__(data):
            # Store test-run scoped data in this class
            data.variable = 'test run scoped variable here'

            # You can also set Step parameters for the top-level step here
            data.step_is_resilient = True # Tells automation to still try following steps if one fails, unless it was as requiremnt


    def define_test(self, data: Data):
        # Define the fields (user and automatic input to a test run)
        self.fields.add(
            automation.Field("TestVersion", default=self.version, is_static=True),
            automation.Field("PartNumber", default="RCTF-TT-TX-REVA", is_static=True),
            automation.Field("STM32 UID", default="[AUTOMATIC]", is_static=True),
            automation.Field("DateTime", default="[AUTOMATIC]", is_static=True),
            automation.Field("CpuTemp", default="[AUTOMATIC]", is_static=True)
            # ...
        )
        
        # Define the test tree
        self.steps.add(
            DutDetect(title='DUT Detection', skip=False),
            PowerUp(title='DUT Power Up Erase', skip=False, imax=0.05, boot=True)(
                EraseAll(title='Erase All')
            ),
            PowerUp(title='DUT Power Up Flash Main', skip=False, boot=True)(
                FlashMain(title='Flash Main')
            ),
            PowerUp(title='DUT Power Up Flash Boot', skip=False, boot=True)(
                FlashBootchecker(title='Flash Bootchecker')
            ),
            ConnectDutUart(title='Connect to DUT')(
                PowerUp(title='DUT Power Up Functional Test', skip=False, imax=0.5)(
                    GetUid(title='Read UID')
                )
            )

        )

    def connect(self, data: Data):
        fixture.stm.connect()
        return connection_manager.connect()
        

    def disconnect(self, data: Data):
        fixture.stm.disconnect
        return connection_manager.disconnect()

    def pre_run(self, data: Data):
        # Generate automatic fields
        fixture.stm.set_rgb_str('#FFFF00')
        fixture.stm.set_lcd_text('TESTING...')
        fixture.stm.set_lcd_text('', 1)
        self.fields.update_entries({
            "DateTime": self.get_datetime(),
            # "PartNumber": 'AutoPartNum',  # TODO read
            "CpuTemp": fixture.get_rpi_cpu_temp()
        })

        # Save state.json for next time the test is run.
        state.update({
            "SerialNumber": self.fields.get_entry("STM32 UID"),
            # ...
        })
        fixture.dut_uid = None

    def post_run(self, data: Data):
        self.fields.update_entries({
            "STM32 UID": fixture.dut_uid
        })
        # Write the full test outcome to a .CSV file      
        part_number, serial_number, datetime = self.fields.get_entries("PartNumber", "STM32 UID", "DateTime")
        passfail = 'PASS' if self.result else 'FAIL'
        filename = f"{part_number}_{passfail}_{datetime}_{serial_number}_Report.csv".replace("/", "-").replace("\\", "-").replace(":", "-").replace(' ', '_')
        ats_num = self.config[fixture.get_rpi_serial()]
        automation.CsvPublisher(self, Path("~/ttatp_reports", ats_num, filename)).generate()
        # print(self.result)
        
        # Look for USB drives and save data there if possible        
        lsblk = os.popen('lsblk | grep sd | grep part').read().strip()  # find all USB drives
        lsblk = lsblk.split('\n')
        for i in lsblk:
            if '/' in i:  # drive mounted
                mount_path = re.search(r'.*part (\/.*)', i).group(1)
                if 'atp_reports' in os.listdir(mount_path):  # find target folder, otherwise ignore                    
                    automation.CsvPublisher(self, Path(mount_path, 'atp_reports', ats_num, filename)).generate()
                    
            elif i != '':  # drive not mounted
                sd_name = re.search(r'(sd\S{2,5})', i).group(1)            
                blkid = os.popen('sudo blkid | grep %s' % sd_name).read().strip()
                uuid = re.search(r'UUID="(\S*)" BLOCK', blkid).group(1)
                mount_path = os.path.join('../media', uuid)
                if uuid not in os.listdir('../media'):
                    os.mkdir(mount_path)
                os.popen('sudo mount /dev/%s %s' % (sd_name, mount_path)).read()
                if 'atp_reports' in os.listdir(mount_path): # find target folder, otherwise ignore      
                    automation.CsvPublisher(self, Path(mount_path, 'atp_reports', ats_num, filename)).generate()   

        if self.result:
            fixture.stm.set_rgb_str('#00FF00')
            fixture.stm.set_lcd_text('PASS')
            fixture.stm.set_lcd_text('', 1)
        else:
            fixture.stm.set_rgb_str('#FF0000')
            fixture.stm.set_lcd_text('!! FAIL !!')
        

    def on_exit(self, data: Data):
        # Runs once just before the ATP unloads
        pass
       

# Entry point
if __name__ == "__main__":
    atp = Atp().start(autorun=False)
    # print(atp)
