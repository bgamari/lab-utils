from lab_utils import dmm6500
from matplotlib import pyplot as pl
import matplotlib
import threading
from collections import defaultdict

def main() -> None:
    dmm = dmm6500.Dmm6500('192.168.2.248')
    fig = pl.figure()
    chans = defaultdict(lambda: ([], []))
    for s in dmm.follow_buffer('defbuffer1'):
        print(s)
        chans[s.channel][0].append(s.time)
        chans[s.channel][1].append(s.reading)
        pl.clf()
        for channel,d in chans.items():
            pl.plot(d[0], d[1], label=channel)

if __name__ == '__main__':
    main()
