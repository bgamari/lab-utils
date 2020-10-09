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
    dump_parser.add_argument('-A', '--average', type=int, default=1,
                             help='Number of samples to average')

    args = parser.parse_args()

    instr = RTB2004(args.address)
    if args.channel.startswith('fft'):
        names = {
            'fft-min': b'MIN',
            'fft-max': b'MAX',
            'fft-avg': b'AVER',
            'fft': b'SPEC',
        }
        name = b'SPEC:WAV:%b' % names[args.channel]
        samples = []
        for i in range(args.average):
            sys.stderr.write('%d / %d\r' % (i+1, args.average))
            samples.append(instr._read_float_data(b'%b:DATA?' % name))

        samples = np.array(samples)
        xorigin = float(instr.ask_raw(b'%b:DATA:XORIGIN?' % name))
        xincr = float(instr.ask_raw(b'%b:DATA:XINC?' % name))
        freqs = np.arange(samples.shape[1]) * xincr + xorigin
        mean = np.mean(samples, axis=0)
        std = np.std(samples, axis=0)
        out = np.vstack([freqs, mean, std]).T
        np.savetxt(args.output, out, header='freq(Hz) amp(dBm) sigma(dBm)')
    else:
        ch = int(args.channel)
        data = instr.read_channel_float(ch)
        args.output.write(str(data))


if __name__ == '__main__':
    main()
