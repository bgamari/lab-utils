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
    parser.add_argument('-r', '--relative-time', action='store_true')
    args = parser.parse_args()

    dmm = dmm6500.Dmm6500(args.host)
    start = dmm.get_start_index(args.buffer)
    end = dmm.get_end_index(args.buffer)

    # Guess delta-t as we can't retrieve timestamps in raw mode
    tmp = list(dmm.get_buffer_data(args.buffer, 1, 3))
    t0 = tmp[0].time
    dt = tmp[1].time - t0

    for i, s in enumerate(dmm.get_buffer_data_raw(args.buffer, start, end)):
        t = t0 + i*dt
        print(f'{t},{s}')


if __name__ == '__main__':
    main()
