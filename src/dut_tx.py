import serial
import struct
import time
import numpy as np

class DutTx:
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
    
    
        
