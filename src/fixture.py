import logging
import os
import re
import struct
import serial
import time
import sys
import subprocess
import numpy as np
from scipy import signal
from scipy.fft import fft
from scipy.optimize import curve_fit

from pathlib import Path
import subinitial.automation as automation
from subinitial.automation import Parameter
from src.stm32coprocessor import Stm32CoProcessor
from src.dut_tx import DutTx


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
# dmm = MockVisaDMM()




class Fixture:
    """Generic fixture object to wrap fixture function helpers into"""
    def __init__(self):
        self.stm = Stm32CoProcessor('/dev/ttyAMA2', 2000000)
        self.dut = DutTx('/dev/ttyAMA3', 115200)
        self.dut_uid = None
        self.l_passes = None
        pass
    
    def get_rpi_serial(self):
        output = os.popen('cat /proc/cpuinfo | grep Serial').read()
        return re.search(r':\s(.{16})', output).group(1)
    
    def get_rpi_cpu_temp(self):
        output = os.popen('vcgencmd measure_temp').read()
        temp = re.search(r"temp=(\S*)'C", output).group(1)
        return float(temp)
    
    def measure_tx_5v(self):
        return self.stm.measure_adc_ls()[3] * 1.5
    
    def measure_tx_3v3(self):
        return self.stm.measure_adc_ls()[2] * 1.5
    
    def measure_tx_5v_3v3(self):
        vals = self.stm.measure_adc_ls()
        return vals[3] * 1.5, vals[2] * 1.5        
    
    def run_rpi(self, cmd):
        print(" ".join(cmd))
        res = subprocess.run(cmd)
        return res
    
    def compute_adc_fft(self, ch_data, samplerate=625e3, f_target=100):
        samples_per_cycle = samplerate / f_target
        num_cycles = len(ch_data) / samples_per_cycle

        trimmed_length = int(np.floor(num_cycles) * samples_per_cycle)
        trimmed_signal = ch_data[:int(trimmed_length)]
    
        # Apply the flattop window
        window  = signal.windows.flattop(trimmed_length)
        windowed_signal = trimmed_signal * window
        
        # Calculate the DFT of the windowed signal
        dft_result = fft(windowed_signal) / np.sum(window) * np.sqrt(2)
        freqs = np.fft.fftfreq(trimmed_length, 1/samplerate)

        return freqs, dft_result
    
    
    def estimate_peak(self, freq, amp):
        """
        Model-free estimation of resonance metrics from magnitude-only data.

        Parameters
        ----------
        freq : ndarray
            Frequency data (Hz), must be monotonic
        amp : ndarray
            Linear magnitude data

        Returns
        -------
        f0 : float or None
            Resonant frequency (Hz)
        K : float or None
            Peak gain
        """

        freq = np.asarray(freq, dtype=float)
        amp = np.asarray(amp, dtype=float)

        if freq.size < 3 or amp.size != freq.size:
            return None, None, None

        # --- Peak detection ---
        peak_idx = np.argmax(amp)
        K = amp[peak_idx]

        # Quadratic peak refinement (if possible)
        if 0 < peak_idx < len(amp) - 1:
            x = freq[peak_idx - 1:peak_idx + 2]
            y = amp[peak_idx - 1:peak_idx + 2]

            if np.all(np.isfinite(x)) and np.all(np.isfinite(y)):
                c = np.polyfit(x, y, 2)
                if c[0] < 0:  # concave down
                    f0 = -c[1] / (2 * c[0])
                    K = np.polyval(c, f0)
                else:
                    f0 = freq[peak_idx]
            else:
                f0 = freq[peak_idx]
        else:
            f0 = freq[peak_idx]

        
        return f0, K, peak_idx


    
    


    
    
        
        
        

fixture = Fixture()