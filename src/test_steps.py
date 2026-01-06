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
        def __init__(data, imax=0.5, boot=False, lcd='Power Up'):
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
            data.lcd = lcd

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
        fixture.stm.set_lcd_text(data.lcd, 0)  
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
        time.sleep(0.2)



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
        # print(rx)
        rx_str = rx.decode('utf-8')
        # print(rx_str)
        match = re.search(r'UID: (\d{30})', rx_str)
    
        if match:
            data.uid = match.group(1)  # Return the UID value
            fixture.dut_uid = data.uid
            

    def teardown(self, data: Data):
        pass


class MeasureResonance(automation.Step):
    class Data:
        def __init__(data):
            data.num_f_centers = 4
            data.f_centers = [41.333e3, 51.666e3, 60.666e3, 65.666e3]
            data.f_deltas = np.linspace(-4e3, 4e3, 9, endpoint=True)
            data.l_configs = [0b0111, 0b1011, 0b1101, 0b1110]

            data.lval_titles = ['L4 220uH', 'L3 100uH', 'L2 47uH', 'L1 22uH']
            data.lmins = [170e-6, 75e-6, 35e-6, 15e-6]
            data.lmaxs = [270e-6, 125e-6, 60e-6, 30e-6]

            data.kmins = [0.192, 0.244, 0.276, 0.286, 0.298]
            data.kmaxs = [0.282, 0.334, 0.366, 0.376, 0.388]

            data.cres_min = 35e-9
            data.cres_max = 55e-9
            data.cres_ftest = 72.666e3

            data.lfix = 103e-6

            data.vdut_min = 4.5
            data.vdut_max = 5.5

            data.idut_min = 0.01
            data.idut_max = 0.55

            data.v5v_min = 4
            data.v5v_max = 5.5

            data.v3v3_min = 3.0
            data.v3v3_max = 3.6            

            # Measurements
            data.cres: float = None
            data.ltunes = [None] * len(data.f_centers)
            data.ktunes = [None] * len(data.f_centers)
            data.isenses = [None] * len(data.f_centers)
            data.vduts = [None] * len(data.f_centers)
            data.iduts = [None] * len(data.f_centers)
            data.v5vs = [None] * len(data.f_centers)
            data.v3v3s = [None] * len(data.f_centers)

    def criteria(self, data: Data):
        self.assert_inrange('Resonant Capacitance', data.cres, data.cres_min, data.cres_max, units='F')

        for i in range(4):
            self.assert_inrange(data.lval_titles[i], data.ltunes[i], data.lmins[i], data.lmaxs[i], units='H')
            self.assert_inrange(data.lval_titles[i]+' Ipeak', data.ktunes[i], data.kmins[i], data.kmaxs[i], units='A RMS')
            self.assert_inrange(data.lval_titles[i]+' Vdut', data.vduts[i], data.vdut_min, data.vdut_max)
            self.assert_inrange(data.lval_titles[i]+' Idut', data.iduts[i], data.idut_min, data.idut_max)
            self.assert_inrange(data.lval_titles[i]+' DUT 5V', data.v5vs[i], data.v5v_min, data.v5v_max)
            self.assert_inrange(data.lval_titles[i]+' DUT 3V3', data.v3v3s[i], data.v3v3_min, data.v5v_max)
            
        

        # for assr in self.assertions:
        #     print(assr.title, assr.procedural, assr.result)

    def procedure(self, data: Data):
        # Start with all short to test resonant capacitance
        fixture.stm.set_lcd_text('C_RES', 1)
        fixture.dut.set_tuning(0b1111)  
        fs = data.cres_ftest + data.f_deltas
        pers = np.round(64e6 / fs).astype(int)
        fixture.dut.set_pwm_per_ccr(pers[0], pers[0] // 2)
        fixture.dut.set_pwm_state(1)
        ipts = []
        for i in range(len(fs)):
            fixture.dut.set_pwm_per_ccr(pers[i], pers[i] // 2)
            ft = float(fs[i])
            adc = fixture.stm.measure_adc_hs()
            iout = adc[0,:]
            dut_isense = fixture.dut.get_isense()
            isense = float(np.std(adc[1,:]))
            rms = float(np.std(iout))
            freqs, iout_fft = fixture.compute_adc_fft(iout, f_target=ft)
            dft = float(np.abs(iout_fft[int(ft/freqs[1])]) )
            ipts.append(dft)
            self.assert_record('ALL SHORT Data Point', '%d %.1f %.6f %.6f %.6f %.6f' % (0b1111, ft, dft, rms, isense, dut_isense))
            # print('xxxx', i, pers[i], pers[i]//2, ft, dft, rms)

        fixture.dut.set_pwm_state(0)
        f0, K, pk_idx = fixture.estimate_peak(fs, ipts)
        data.cres = float((2 * np.pi * f0)**(-2) / data.lfix)
        self.assert_record('ALL SHORT F0', f0, units='Hz')
        self.assert_record('ALL SHORT Ipeak', K, units='A RMS')
        self.assert_record('Resonant Capacitance', '%.2f' % (data.cres*1e9), units='nF')

        if data.cres_min <= data.cres <= data.cres_max:
            # Loop through tuning inductors
            for i in range(len(data.f_centers)):
                cfg_title = data.lval_titles[i]
                fixture.stm.set_lcd_text(cfg_title, 1)
                fixture.dut.set_tuning(data.l_configs[i])  
                fs = data.f_centers[i] + data.f_deltas
                pers = np.round(64e6 / fs).astype(int)
                fixture.dut.set_pwm_per_ccr(pers[0], pers[0] // 2)
                fixture.dut.set_pwm_state(1)
                ipts = []
                for j in range(len(fs)):
                    fixture.dut.set_pwm_per_ccr(pers[j], pers[j] // 2)
                    ft = float(fs[j])
                    adc = fixture.stm.measure_adc_hs()
                    if ft == data.f_centers[i]:
                        v5v, v3v3 = fixture.measure_tx_5v_3v3()
                        data.v5vs[i] = v5v
                        data.v3v3s[i] = v3v3
                        data.vduts[i] = fixture.stm.measure_vdut()
                        data.iduts[i] = fixture.stm.measure_idut()

                    iout = adc[0,:]
                    dut_isense = fixture.dut.get_isense()
                    isense = float(np.std(adc[1,:]))
                    rms = float(np.std(iout))
                    freqs, iout_fft = fixture.compute_adc_fft(iout, f_target=ft)
                    dft = float(np.abs(iout_fft[int(ft/freqs[1])]) )
                    ipts.append(dft)

                    self.assert_record(cfg_title+' Data Point', '%d %.1f %.6f %.6f %.6f %.6f' % (data.l_configs[i], ft, dft, rms, isense, dut_isense))
                    # print('xxxx', i, pers[j], pers[j]//2, ft, dft, rms)

                fixture.dut.set_pwm_state(0)
                f0, K, pk_idx = fixture.estimate_peak(fs, ipts)
                data.ltunes[i] = float((2 * np.pi * f0)**(-2) / data.cres - data.lfix)
                data.ktunes[i] = K
                self.assert_record(cfg_title+' F0', f0, units='Hz')
                self.assert_record(cfg_title+' Ipeak', K, units='A RMS')
                self.assert_record(cfg_title, '%.2f' % (data.ltunes[i]*1e6), units='uH')

            # Add LCD message catching any incorrect Inductor Values
            anyfail = False
            failmsg = ''
            for i in range(len(data.f_centers)):
                if data.lmins[i] <= data.ltunes[i] <= data.lmaxs[i]:
                    pass
                else:
                    anyfail = True
                    failmsg += 'L%d ' % (4 - i)

            if anyfail:
                fixture.stm.set_lcd_text(failmsg, 1)




class AutoTune(automation.Step):
    class Data:
        def __init__(data):
            data.f_target = 53.333e3
            data.z_max = 20
            data.dft_min = 0.205
            data.dft_max = 0.235
            data.dut_isense_min = 0.21
            data.dut_isense_max = 0.23

            # Measurements
            data.dft: float = None
            data.rms: float = None
            data.isense: float = None
            data.dut_isense: float = None
            data.vdut: float = None
            data.idut: float = None
            data.v5v: float = None
            data.v3v: float = None

            data.tune_rms = []
            data.tune_ohms = []
            data.tune_cfgs = []
            data.tune_steps: int = 0
            data.tune_minz: float = None
    
    def criteria(self, data: Data):
        self.assert_record('Number Tuning Steps', data.tune_steps)
        for i in range(data.tune_steps):
            self.assert_record('Relay cfg %d Current' % (data.tune_cfgs[i]), data.tune_rms[i], units='A RMS')
            self.assert_record('Relay cfg %d |Z|' % (data.tune_cfgs[i]), data.tune_ohms[i], units='|Ω|')
        self.assert_lessthan('Min |Z|', data.tune_minz, data.z_max, units='|Ω|')
        self.assert_inrange('Measured Iout DFT', data.dft, data.dft_min, data.dft_max, units='A RMS')
        self.assert_inrange('Measured Iout RMS', data.rms, data.dft_min, data.dft_max, units='A RMS')
        self.assert_inrange('Measured Iout DFT', data.dut_isense, data.dut_isense_min, data.dut_isense_max, units='A RMS')

    def procedure(self, data: Data):
        fixture.stm.set_lcd_text('Auto Tune', 1)
        fixture.dut.flush_rx()
        fixture.dut.set_auto_state(1)
        time.sleep(3.0)

        rx = fixture.dut.ser.read_all()
        rx_str = rx.decode('utf-8')
        # print(rx_str)
        cfg_pattern = re.compile(r"Relay cfg:\s*(\d+)")
        ma_pattern = re.compile(r"(\d+)mA")
        moh_pattern = re.compile(r"(\d+)mOhm")
        lines = rx_str.split('\n\r')
        for line in lines:
            if 'Relay cfg:' in line:
                # print(line)
                data.tune_steps += 1
                cfg = cfg_pattern.search(line)
                ma = ma_pattern.search(line)
                moh = moh_pattern.search(line)
                data.tune_cfgs.append(int(cfg.group(1)) if cfg else None)
                data.tune_rms.append(float(ma.group(1)) / 1000 if ma else None)
                data.tune_ohms.append(float(moh.group(1)) / 1000 if moh else None)


        z_vals = [z for z in data.tune_ohms if z is not None]
        data.tune_minz = min(z_vals) if z_vals else None

        # print(data.tune_steps)
        # print(data.tune_cfgs)
        # print(data.tune_rms)
        # print(data.tune_ohms)
        

        adc = fixture.stm.measure_adc_hs()
        ft = data.f_target
        iout = adc[0,:]
        data.dut_isense = fixture.dut.get_isense()
        data.isense = np.std(adc[1,:])
        data.rms = np.std(iout)
        freqs, iout_fft = fixture.compute_adc_fft(iout, f_target=ft)
        data.dft = np.abs(iout_fft[int(ft/freqs[1])])

        fixture.dut.set_auto_state(0)
        


# class TestManualConfig(automation.Step):
#     class Data:
#         def __init__(data, l_config, lcd_text,
#                      rms_target, rms_tol,
#                      dft_target, dft_tol,
#                      isense_target, isense_tol,
#                      peak_limit):
            
#             data.l_config = l_config
#             data.lcd_text = lcd_text

#             data.rms_target = rms_target
#             data.rms_tol = rms_tol

#             data.dft_target = dft_target
#             data.dft_tol = dft_tol

#             data.isense_target = isense_target
#             data.isense_tol = isense_tol

#             data.peak_limit = peak_limit

#             # Measurements
#             data.rms: float = None
#             data.dft: float = None
#             data.peak: float = None
#             data.avg: float = None
#             data.harmonics = None
#             data.isense: float = None        
#             data.vdut: float = None
#             data.idut: float = None    

#     def criteria(self, data: Data):
#         self.assert_record('Tuning L Config #', data.l_config)
#         self.assert_tolerance('Measured Irms', data.rms, data.rms_target, data.rms_tol, units='A')
#         self.assert_lessthan('Measured Peak', data.peak, data.peak_limit, units='A')
#         self.assert_tolerance('Measured dft', data.dft, data.dft_target, data.dft_tol, units='A')
#         self.assert_tolerance('DUT Reported Irms', data.isense, data.isense_target, data.isense_tol, units='A')
#         self.assert_record('Measured Vdut', data.vdut, units='V')
#         self.assert_record('Measured Idut', data.idut, units='A')    

#     def procedure(self, data: Data):
#         fixture.stm.set_lcd_text(data.lcd_text, 1)
#         fixture.dut.set_pwm_per_ccr(1200, 0)
#         fixture.dut.set_tuning(data.l_config)

#         for pwm in np.arange(0, 720, 120):
#             fixture.dut.set_pwm_per_ccr(1200, pwm)
#         time.sleep(0.1)
#         data.vdut = fixture.stm.measure_vdut()
#         data.idut = fixture.stm.measure_idut()  
#         adc = fixture.stm.measure_adc_hs()
#         itrace = adc[0,:]
#         freqs, iout_fft = fixture.compute_adc_fft(adc[0,:], f_target=(160e3/3))
#         data.dft = np.abs(iout_fft[int(160e3/3/freqs[1])])
#         data.rms = np.std(itrace)
#         data.avg = np.mean(itrace)
#         data.peak = np.max(np.abs(itrace - data.avg))
#         data.isense = fixture.dut.get_isense()

#         fixture.dut.set_pwm_per_ccr(1200, 0)


#     def teardown(self, data: Data):
#         pass

    

