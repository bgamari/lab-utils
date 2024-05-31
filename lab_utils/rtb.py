import collections
import time
import logging

import numpy as np
import vxi11

DataHeader = collections.namedtuple('DataHeader', 'x_start,x_stop,n_samples,n_values_per_sample')

class RTB2004(vxi11.Instrument):
    def __init__(self, address):
        vxi11.Instrument.__init__(self, address)
        logging.info(self.ask('*IDN?'))

    def reset(self):
        self.write('*RST')

    def read_data_header(self, ch):
        head = self.ask('CHAN%d:DATA:HEAD?' % ch)
        xstart, xstop, nsamples, nvalues = head.split(',')
        return DataHeader(float(xstart), float(xstop), int(nsamples), int(nvalues))

    def read_channel(self, ch):
        self.write('CHAN%d:DATA:POINTS MAX' % ch)
        start = time.time()
        self.write('FORMAT:DATA UINT,8')
        b = self.ask_raw(b'CHAN%d:DATA?' % ch)
        end = time.time()
        logging.debug('Tranferred in %f seconds'%(end-start))

        assert b[0] == 35
        nchars = int(b[1:2].decode())
        nbytes = int(b[2:2+nchars].decode())
        start = 2+nchars
        end = start + nbytes
        arr = np.frombuffer(b[start:end], dtype='>u1')
        xorigin = float(self.ask('CHAN%d:DATA:XORIGIN?' % ch))
        xincr = float(self.ask('CHAN%d:DATA:XINC?' % ch))
        yorigin = float(self.ask('CHAN%d:DATA:YORIGIN?' % ch))
        yincr = float(self.ask('CHAN%d:DATA:YINC?' % ch))
        yres = float(self.ask('CHAN%d:DATA:YRES?' % ch))
        return arr*yincr + yorigin

    def read_channel_float(self, ch: int):
        self.write('CHAN%d:DATA:POINTS MAX' % ch)
        return self._read_float_data(b'CHAN%d:DATA?' % ch)

    def _read_float_data(self, cmd: bytes):
        start = time.time()
        self.write('FORMAT:DATA REAL,32')
        b = self.ask_raw(cmd)
        end = time.time()
        logging.debug('Tranferred in %f seconds'%(end-start))

        assert b[0] == 35
        nchars = int(b[1:2].decode())
        nbytes = int(b[2:2+nchars].decode())
        start = 2+nchars
        end = start + nbytes
        arr = np.frombuffer(b[start:end], dtype='>f4')
        return arr

    def wait_for_complete(self):
        while True:
            x = self.ask('*OPC?')
            if x == '1':
                break
            time.sleep(1e-3)

    def set_wgen_function(self, function: str):
        assert function in {'dc', 'sin', 'square', 'pulse', 'triangle', 'ramp', 'sinc', 'arbitrary', 'exponential'}
        self.write(f'WGEN:FUNC {function}')

    def set_wgen_amplitude(self, amp: float):
        self.write(f'WGEN:VOLT {amp}')

    def set_wgen_offset(self, offset: float):
        self.write(f'WGEN:OFFSET {offset}')

    def set_wgen_frequency(self, freq: float):
        self.write(f'WGEN:FREQ {freq}')

    def set_wgen_enabled(self, enabled: bool):
        x = 'ON' if enabled else 'OFF'
        self.write(f'WGEN:OUT:ENABLE {x}')
