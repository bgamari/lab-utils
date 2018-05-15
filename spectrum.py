#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3Packages.vxi11 python3Packages.numpy python3Packages.scipy python3Packages.matplotlib

import logging
import time
import collections
import math
import vxi11
import numpy as np
import scipy.signal

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

    def read_channel_float(self, ch):
        self.write('CHAN%d:DATA:POINTS MAX' % ch)
        start = time.time()
        self.write('FORMAT:DATA REAL,32')
        b = self.ask_raw(b'CHAN%d:DATA?' % ch)
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

def sweep(instr: RTB2004, excitation_chan: int, response_chan: int, ampl, freqs, save_curves=None):
    instr.write('WGEN:FUNC SIN')
    instr.write('WGEN:VOLT %f' % ampl)
    instr.write('WGEN:OFFS 0')
    instr.write('WGEN:OUTPUT:DEST BNC')
    instr.write('WGEN:OUTPUT:ENABLE ON')

    instr.write('TRIG:A:MODE NORM')
    instr.write('TRIG:A:MODE:SOUR CH%d' % excitation_chan)
    instr.write('TRIG:A:TYPE EDGE')
    instr.write('TRIG:A:HOLD:MODE OFF')
    instr.write('TRIG:A:EDGE:SLOPE POS')
    instr.write('STOP')
    instr.write('ACQ:NSINGLE:COUNT 1')
    instr.write('ACQ:POINTS:VALUE 1e6')
    instr.write('ACQ:TYPE REFRESH')

    instr.write('CHAN%d:STATE ON' % response_chan)
    instr.write('PROBE%d:SETUP:ATTEN:MAN 1' % (response_chan))
    instr.write('CHAN%d:RANGE %f' % (response_chan, 4*ampl))

    instr.write('CHAN%d:STATE ON' % excitation_chan)
    instr.write('PROBE%d:SETUP:ATTEN:MAN 1' % (excitation_chan))
    instr.write('CHAN%d:RANGE %f' % (excitation_chan, 4*ampl))
    instr.write('TIMEBASE:ZOOM:STATE ON')

    d = {}
    pts = []
    for freq in freqs:
        instr.wait_for_complete()
        logging.info(freq)
        instr.write('WGEN:FREQ %f' % freq)
        instr.write('TIMEBASE:RANGE %f' % (1000/freq))
        instr.write('TIMEBASE:ZOOM:SCALE %f' % (1/2/freq))
        instr.write('SINGLE')
        instr.wait_for_complete()

        logging.debug(instr.read_data_header(excitation_chan))
        excitation = instr.read_channel(excitation_chan)
        logging.debug(instr.read_data_header(response_chan))
        response = instr.read_channel(response_chan)
        offset = np.mean(response)
        response -= offset

        d[freq] = (excitation, response)
        if save_curves:
            np.save('out/freq%f-exc' % freq, excitation)
            np.save('out/freq%f-resp' % freq, response)

        corr = scipy.signal.correlate(excitation, response, mode='full')
        phase = np.argmax(corr)
        gain = math.sqrt(np.sum(response**2) / np.sum(excitation**2))
        print(freq, phase, gain, offset)
        pts.append((freq, gain, phase, offset))

    instr.write('WGEN:OUTPUT:ENABLE OFF')
    pts = np.array(pts)
    return pts

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='192.168.2.106')
    parser.add_argument('-e', '--excitation-ch', type=int, default=1, help='Channel on which to measure excitation')
    parser.add_argument('-r', '--response-ch', type=int, default=4, help='Channel on which to measure response')
    parser.add_argument('-A', '--amplitude', type=float, default=1, help='excitation amplitude')
    parser.add_argument('-S', '--start-freq', type=float, default=1000, help='sweep start frequency')
    parser.add_argument('-E', '--end-freq', type=float, default=9e6, help='sweep end frequency')
    parser.add_argument('-N', '--points', type=float, default=256, help='sweep point count')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help='output CSV')
    parser.add_argument('-p', '--plot', type=argparse.FileType('w'), help='output CSV')
    args = parser.parse_args()

    instr = RTB2004(args.address)
    instr.reset()
    freqs = np.logspace(math.log10(args.start_freq), math.log10(args.end_freq), args.points)
    pts = sweep(instr,
                excitation_chan = args.excitation_ch,
                response_chan = args.response_ch,
                ampl = args.amplitude,
                freqs = freqs)

    if args.output:
        np.savetxt(args.output.name, pts)

    if args.plot:
        import matplotlib.pyplot as pl
        pl.subplot(211)
        pl.plot(pts[:,0], pts[:,1])
        pl.ylabel('gain')
        pl.xscale('log')
        pl.ylim(0,1)

        pl.subplot(212)
        pl.plot(pts[:,0], pts[:,2], label='phase')
        pl.xscale('log')
        pl.ylabel('phase')
        pl.xlabel('frequency (Hz)')

        pl.savefig(args.plot.name)

if __name__ == "__main__":
    main()
