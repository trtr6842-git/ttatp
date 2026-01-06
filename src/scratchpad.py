#! .env/bin/python3

import subinitial.automation as automation
import time
import numpy as np

testroot = automation.locate_testroot()
testroot.insert_path()  # insert testroot into sys.path for consistent file imports!

from src.fixture import *
from src.connections import connection_manager


def main():

    f_deltas = f_deltas = np.linspace(-5e3, 5e3, 11, endpoint=True)
    print(f_deltas)
    # return

    fixture.stm.connect()
    fixture.stm.set_lcd_text('Scratchpad')
    fixture.stm.set_lcd_text('', 1)
    fixture.stm.set_dout_state(2, 1)
    fixture.stm.set_vdut(0)           
    time.sleep(0.5)
    fixture.stm.set_vdut(5)
    time.sleep(1.5)

    fixture.dut.connect()

    # fixture.dut.set_auto_state(1)
    # time.sleep(5)
    # fixture.dut.set_auto_state(0)

    # for i in [0b1110, 0b1101, 0b1011, 0b0111]:
    #     fixture.dut.set_tuning(i)
    #     time.sleep(0.1)
    #     fixture.dut._write_u16_list(1, [1200, 0])
    #     fixture.dut.set_pwm_state(1)        
    #     for pwm in np.arange(0, 720, 120):
    #         print(pwm, end='\r')
    #         fixture.dut._write_u16_list(1, [1200, pwm])

    #     vdut = fixture.stm.measure_vdut()
    #     idut = fixture.stm.measure_idut()    
    #     fixture.stm.set_lcd_text('%5.3fV %5.3fA' % (vdut, idut))
    #     fixture.stm.set_lcd_text('%5.3fW' % (vdut * idut), 1)

    #     adc = fixture.stm.measure_adc_hs()
    #     dut_isense = fixture.dut.get_isense()
    #     freqs, iout_fft = fixture.compute_adc_fft(adc[0,:], f_target=(160e3/3))
    #     freqs, dut_isense_fft = fixture.compute_adc_fft(adc[1,:], f_target=(160e3/3))
    #     print(iout_fft.shape)
    #     bin0 = np.abs(iout_fft[int(160e3/3/freqs[1])])
    #     vrms = np.std(adc[0,:])
    #     path = 'scratch_logs/fft_itune_%d.csv' % (i)
    #     np.savetxt(path, np.column_stack((freqs,np.abs(iout_fft))), delimiter=',')
    #     print('Tuning = %d' % (i))
    #     print('AC Volts RMS = %.4fV' % (vrms))
    #     print('BIN0 value %5.4fV' % (bin0))
    #     print('DUT Isense %5.4fA' % (dut_isense))
    #     print('AC Volts RMS = %.4fV' % (np.std(adc[1,:])))
    #     print('Pdut %5.3fW' % (idut * vdut))

    #     fixture.dut.set_pwm_state(0)        




    l_configs = [0b1111, 0b1110, 0b1101, 0b1011, 0b0111]
    print(l_configs)
    f_centers = [72.666e3, 65.666e3, 60.666e3, 51.666e3, 41.333e3]
    
    f0s = []
    ks = []
    
    for i in range(len(f_centers)):
        fs = f_deltas + f_centers[i]
        pers = np.round(64e6 / fs).astype(int)
        fixture.dut.set_pwm_state(0)
        fixture.dut.set_tuning(l_configs[i])
        time.sleep(0.02)
        fixture.dut.set_pwm_state(1)

        ipts = []

        for j in range(len(fs)):
            ft = fs[j]
            per = pers[j]

            fixture.dut.set_pwm_per_ccr(per, per//2)
            adc = fixture.stm.measure_adc_hs()
            iout = adc[0,:]
            rms = np.std(iout)
            freqs, iout_fft = fixture.compute_adc_fft(iout, f_target=ft)
            dft = np.abs(iout_fft[int(ft/freqs[1])])

            ipts.append(dft)

            print("{:04b}".format(l_configs[i]), i, per, per//2, ft, dft, rms)

        f0, K, pk_idx = fixture.estimate_peak(fs, ipts)
        f0s.append(f0)
        ks.append(K)
        print(f0, K, (2 * np.pi * f0)**-2 / 40e-9)

    # for i in range(len(f0s)):
    #     for j in range(len(f_deltas)):
    #         print(f0s[i], qs[i], ks[i])
    
    fixture.dut.set_pwm_state(0)
    fixture.stm.set_vdut(0)
    fixture.stm.disconnect()
    fixture.dut.disconnect()
    







if __name__ == "__main__":
    main()
