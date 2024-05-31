#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lab_utils import dmm6500
import rtb

import time

import numpy as np
from matplotlib import pyplot as pl

dmm = dmm6500.Dmm6500('192.168.2.248')
buf = 'tmp'
dmm.delete_buffer(buf)
dmm.create_buffer(buf, 100)
dmm.set_function('ac-voltage')

gen = rtb.RTB2004('192.168.2.150')
gen.set_wgen_function('square')
gen.set_wgen_amplitude(1)
gen.set_wgen_offset(0)
gen.set_wgen_frequency(50000)
gen.set_wgen_enabled(True)

samples = {}
for amp_mv in range(100, 1000, 10):
#for amp_mv in np.logspace(3, 5, 50):
    gen.set_wgen_amplitude(amp_mv/1000)
    #gen.set_wgen_frequency(amp_mv)
    dmm.clear_buffer(buf)
    dmm.write('SENSE1:COUNT 100')
    time.sleep(0.5)

    dmm.write(f'TRACE:TRIGGER "{buf}"')
    dmm.wait()
    r = dmm.get_buffer_data(buf, 1, 100)
    print(amp_mv, np.mean(r), np.std(r))
    amp = amp_mv / 1000
    samples[amp] = np.array(r)

# Fit
all_points = np.array([ (x, y) for x, ys in samples.items() for y in ys ])
fit_param = np.polyfit(all_points[:,0], all_points[:,1], 1)
print(fit_param)

np.savetxt('out.csv', all_points)

if False:
    pl.clf()
    means = np.array([(x, np.mean(r)) for x, r in samples.items()])
    #pl.plot(means[:,0], means[:,1])
    pl.xlabel('amplitude (V)')
    pl.ylabel('mean response (V)')
    pl.show()

if True:
    pl.clf()
    pl.violinplot(dataset=list(samples.values()), positions=list(samples.keys()), widths=0.02)
    pl.plot(list(samples.keys()), np.polyval(fit_param, list(samples.keys())), label='fit')
    pl.xlabel('amplitude (V)')
    pl.ylabel('mean response (V)')
    pl.show()

if False:
    pl.clf()
    for x, r in samples.items():
        pl.hist(r, range=(0, 0.03), bins=200, label=f'{amp_mv} mV')

    pl.legend()
    pl.show()
