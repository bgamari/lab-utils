#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vxi11

import enum
import logging
import time
import datetime
import array
from typing import List, NewType, NamedTuple, Iterator

BufferName = NewType("BufferName", str)

class Sample(NamedTuple):
    time: datetime.datetime
    channel: str
    reading: float

class Function(enum.Enum):
    dc_voltage  = 'VOLTAGE:DC'
    ac_voltage  = 'VOLTAGE:AC'
    dc_current  = 'CURRENT:DC'
    ac_current  = 'CURRENT:AC'
    resistance  = 'RESISTANCE'
    diode       = 'DIODE'
    capacitance = 'CAPACITANCE'
    temperature = 'TEMPERATURE'

class Dmm6500(vxi11.Instrument):
    def __init__(self, address):
        vxi11.Instrument.__init__(self, address)
        self.clear()
        logging.info(self.ask('*IDN?'))
        self.write(':FORMAT:DATA ASCII')

    def wait(self):
        self.write('*WAI')

    def set_function(self, function: Function):
        self.write(f'SENSE1:FUNCTION "{function.value}"')

    def create_buffer(self, buf_name: BufferName, size: int):
        self.write(f'TRACE:MAKE "{buf_name}", {size}')

    def delete_buffer(self, buf_name: BufferName):
        self.write(f'TRACE:DELETE "{buf_name}"')

    def clear_buffer(self, buf_name: BufferName):
        self.write(f'TRACE:CLEAR "{buf_name}"')

    def set_buffer_size(self, buf_name: BufferName, size: int):
        self.write(f'TRACE:POINTS {size}, "{buf_name}"')

    def get_buffer_size(self, buf_name: BufferName) -> int:
        r = self.ask(f'TRACE:POINTS? "{buf_name}"')
        return int(r)

    def get_start_index(self, buf_name: BufferName) -> int:
        r = self.ask(f'TRACE:ACTUAL:START? "{buf_name}"')
        return int(r)

    def get_end_index(self, buf_name: BufferName) -> int:
        r = self.ask(f'TRACE:ACTUAL:END? "{buf_name}"')
        return int(r)

    def get_buffer_data(self, buf_name: BufferName, start: int, end: int) -> Iterator[Sample]:
        self.write(':FORMAT:DATA ASCII')
        while start < end:
            n = min(20, end - start)
            yield from self.get_buffer_data_one(buf_name, start, start+n-1)
            start += n

    def get_buffer_data_one(self, buf_name: BufferName, start: int, end: int) -> Iterator[Sample]:
        assert start > 0
        r = self.ask(f'TRACE:DATA? {start}, {end}, "{buf_name}", SEC, FRAC, CHAN, READING')
        xs = r.split(',')
        while xs:
            t_sec,t_frac,ch,x = xs[:4]
            xs = xs[4:]
            t = datetime.datetime.fromtimestamp(int(t_sec)) + \
                    datetime.timedelta(microseconds=1e6*float(t_frac))

            yield Sample(t, ch, float(x))

    def get_buffer_data_raw(self, buf_name: BufferName, start: int, end: int) -> array.array:
        assert start > 0
        self.write(':FORMAT:DATA REAL')
        r = self.ask_raw(f'TRACE:DATA? {start}, {end}, "{buf_name}", READING'.encode('ascii'))
        assert r[:2] == b'#0', f'unexpected response: {r[:10]}'
        print(len(r))
        return array.array('d', r[2:-1])

    def trigger_imm(self):
        self.write(f'INITIATE:IMMED')

    def trigger_cont(self):
        self.write(f'TRIGGER:CONT')

    def trigger_pause(self):
        self.write(f'TRIGGER:PAUSE')

    def trigger_resume(self):
        self.write(f'TRIGGER:RESUME')

    def follow_buffer(self, buf_name: BufferName) -> Iterator[Sample]:
        i = self.get_start_index(buf_name)
        while True:
            end = self.get_end_index(buf_name)
            if i == end:
                time.sleep(0.1)
            else:
                yield from self.get_buffer_data(buf_name, i, end)
                i = end

    def measure(self) -> float:
        r = self.ask(f'MEASURE?')
        return float(r)

