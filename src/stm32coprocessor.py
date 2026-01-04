import serial
import struct
import time
import numpy as np

class Stm32CoProcessor:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(port=self.port, baudrate=self.baud, timeout=1)
        self.ser.read_all()

    def disconnect(self):
        self.ser.flush()
        self.ser.close()

    def flush_rx(self):
        self.ser.read_all()

    def _read_n_bytes(self, n, timeout=1):
        data = bytearray()
        start = time.monotonic()

        while len(data) < n:
            chunk = self.ser.read(n - len(data))
            if chunk:
                data.extend(chunk)
            else:
                # read() timed out
                break

            if time.monotonic() - start >= timeout:
                break

        if len(data) != n:
            raise TimeoutError(f"Expected {n} bytes, received {len(data)}")
        return bytes(data)
    

    def _write_u32(self, cmd:int, val:int):
        cmd = cmd | 0x80000000
        tx_bytes = struct.pack('<II', cmd, val)
        self.ser.write(tx_bytes)
        self.ser.flush()

        rx = self._read_n_bytes(len(tx_bytes))
        return struct.unpack('<II', rx)[1]
    
    def _write_u8_list(self, cmd:int, vals:list[int]):
        cmd = cmd | 0x80000000
        tx_bytes = struct.pack('<I4B', cmd, *vals)
        self.ser.write(tx_bytes)
        self.ser.flush()

        rx = self._read_n_bytes(len(tx_bytes))
        return struct.unpack('<I4B', rx)[-4:]
    
    def _read_u32(self, cmd:int):
        tx_bytes = struct.pack('<II', cmd, 0)
        self.ser.write(tx_bytes)
        self.ser.flush()

        rx = self._read_n_bytes(len(tx_bytes))
        return struct.unpack('<II', rx)[1]
    
    def _write_f32(self, cmd:int, val:float):
        cmd = cmd | 0x80000000
        tx_bytes = struct.pack('<If', cmd, val)
        self.ser.write(tx_bytes)
        self.ser.flush()

        rx = self._read_n_bytes(len(tx_bytes))
        return struct.unpack('<If', rx)[1]
    
    def _read_f32(self, cmd:int):
        tx_bytes = struct.pack('<If', cmd, 0)
        self.ser.write(tx_bytes)
        self.ser.flush()

        rx = self._read_n_bytes(len(tx_bytes))
        return struct.unpack('<If', rx)[1]
    
    def set_vdut(self, voltage:float):
        return self._write_f32(1, voltage)
    
    def measure_vdut(self):
        return self._read_f32(2)
    
    def measure_idut(self):
        return self._read_f32(3)
    
    def set_rgb_str(self, rgb:str):
        rgb = int(rgb[1:], 16)
        return self._write_u32(4, rgb)
    
    def set_lcd_text(self, text:str, row=0, col=0, full_line=True):
        if len(text)+col > 16:
            raise Exception('String too long to fit on LCD at given position: %s at column %d' % (text, col))
        
        if row > 1 or row < 0:
            raise Exception('Row number must be 0 or 1: received %d' % row)
        
        if full_line:
            text = text[:16].ljust(16)

        tx_bytes = struct.pack('<BB', col, row)
        tx_bytes = tx_bytes + text.encode('utf-8')

        self._write_u32(5, len(tx_bytes))
        self.ser.write(tx_bytes)
        self._read_n_bytes(8)

    def set_fp_led_state(self, state=True):
        if state:
            return self._write_u32(6, 1)
        else:
            return self._write_u32(6, 0)
        
    def set_dout_state(self, dout_num, state):
        if state:
            return self._write_u8_list(7, [dout_num, 1, 0, 0])
        else:
            return self._write_u8_list(7, [dout_num, 0, 0, 0])
        
    def get_din_state(self, dout_num):
        return self._write_u32(8, dout_num)
    
    def measure_adc_ls(self):
        rx_len = self._read_u32(9)
        rx = self._read_n_bytes(rx_len)
        count = rx_len // 4
        values = struct.unpack('<' + 'f' * count, rx)
        return values
    
    def measure_adc_hs(self):
        rx_len = self._read_u32(10)
        rx = self._read_n_bytes(rx_len)
        count = rx_len // 2
        values = struct.unpack('<' + 'H' * count, rx)
        adc_data: np.ndarray = np.array(values, dtype=np.uint16) * (3.3 / 4095)
        num_channels = 4
        adc_reshaped = adc_data.reshape(-1, num_channels).T
        return adc_reshaped

        
