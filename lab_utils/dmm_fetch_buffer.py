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
    for s in dmm.get_buffer_data(args.buffer, start, end):
        print(f'{s.time},{s.channel},{s.reading}')


if __name__ == '__main__':
    main()
