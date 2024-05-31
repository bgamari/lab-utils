from lab_utils import dmm6500
from matplotlib import pyplot as pl
import matplotlib
import threading
from collections import defaultdict

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='192.168.2.248')
    parser.add_argument('-b', '--buffer', default='defbuffer1')
    args = parser.parse_args()

    dmm = dmm6500.Dmm6500(args.host)
    fig = pl.figure()
    chans = defaultdict(lambda: ([], []))
    for s in dmm.follow_buffer(args.buffer):
        print(f'{s.time} {s.channel} {s.reading}')
        chans[s.channel][0].append(s.time)
        chans[s.channel][1].append(s.reading)
        pl.clf()
        for channel,d in chans.items():
            pl.plot(d[0], d[1], label=channel)

if __name__ == '__main__':
    main()
