#!/usr/bin/env python

import sys
import numpy as np
from rtb import RTB2004

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, required=True)
    subparser = parser.add_subparsers()

    dump_parser = subparser.add_parser('dump', help='Dump waveform data')
    dump_parser.add_argument('-c', '--channel', type=str, required=True,
                             help='Channel to transfer (1..4, ref1..ref4, fft, fft-min, fft-max, fft-avg)')
    dump_parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
                             help='Output file name')

    args = parser.parse_args()

    instr = RTB2004(args.address)
    if args.channel.startswith('fft-'):
        names = {
            'fft-min': b'MIN',
            'fft-max': b'MAX',
            'fft-avg': b'AVER',
            'fft': b'SPEC',
        }
        name = b'SPEC:WAV:%b' % names[args.channel]
        data = instr._read_float_data(b'%b:DATA?' % name)
        xorigin = float(instr.ask_raw(b'%b:DATA:XORIGIN?' % name))
        xincr = float(instr.ask_raw(b'%b:DATA:XINC?' % name))
        freqs = np.arange(len(data)) * xincr + xorigin
        out = np.vstack([freqs, data]).T
        np.savetxt(args.output, out, header='freq(Hz) amp(dBm)')
    else:
        ch = int(args.channel)
        data = instr.read_channel_float(ch)
        args.output.write(str(data))


if __name__ == '__main__':
    main()
