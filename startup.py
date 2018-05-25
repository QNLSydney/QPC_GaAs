# -*- coding: utf-8 -*-
"""
Created on Fri May 25 09:41:38 2018

@author: Alexis Jouan
"""


# Log all output
from IPython import get_ipython
ip = get_ipython()
ip.magic("logstop")
ip.magic("logstart -o -t iPython_Logs/QPC_GaAs_log.py rotate")

#Lock-In IP address : 10.66.42.251

import qcodes as qc
import pyvisa
import matplotlib.pyplot as plt
import numpy as np
import time 
import visa


#from time import sleep, monotonic

from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from qcodes.dataset.data_set import load_by_id
from qcodes.dataset import experiment_container

from qcodes import Station
from qcodes.dataset.experiment_container import Experiment, load_last_experiment, new_experiment, load_experiment_by_name
from qcodes.tests.instrument_mocks import DummyInstrument
from qcodes.dataset.param_spec import ParamSpec
from qcodes.dataset.data_export import get_shaped_data_by_runid

from qcodes.instrument.parameter import ManualParameter

# Module to use system1.yaml
from qdev_wrappers.station_configurator import StationConfigurator

# Close any instruments that may already be open
instruments = list(qc.Instrument._all_instruments.keys())
for instrument in instruments:
    instr = qc.Instrument._all_instruments.pop(instrument)
    instr = instr()
    instr.close()

# Set up experiment
exp_name = 'qcodes_controls_mdac'
sample_name = 'mdac'

try:
    exp = load_experiment_by_name(exp_name, sample=sample_name)
    print('Experiment loaded. Last ID no:', exp.last_counter)
except ValueError:
    exp = new_experiment(exp_name, sample_name)
    print('Started new experiment')

scfg = StationConfigurator()

mdac = scfg.load_instrument('mdac')
#lockin = scfg.load_instrument('sr860')
#ithaco = scfg.load_instrument('ithaco')
multimeter=scfg.load_instrument('Keysight')

dummy_time = DummyInstrument(name="dummy_time")
time_zero = time.time()
def getTime():
    return time.time() - time_zero
dummy_time.add_parameter('seconds',
                  label='time',
                  unit='s',
                  get_cmd=getTime,
                  set_cmd=lambda x: x)
dummy_time.add_parameter('dummy_set',
                         label='count',
                         set_cmd=lambda x: x)
dummy_time.seconds()

def veryfirst():
    print('Starting the measurement')
    global time_zero
    time_zero = time.time()


def thelast():
    print('End of measurement')



def make_title(dataset):
    '''Make a descriptive title for the dataset.'''
    experiment = experiment_container.load_experiment(dataset.exp_id)
    title = '{} on {} - {}.{} ({})'
    title = title.format(experiment.name, experiment.sample_name,
                         experiment.exp_id, dataset.counter, dataset.run_id)
    return title
        
def redraw(run_id, axes, cbars):
    '''Call plot_by_id to plot the available data on axes.'''
    pause_time = 0.001
    dataset = load_by_id(run_id)
    if not dataset: # there is not data available yet
        axes, cbars = [], []
    elif not axes: # there is data available but no plot yet
        axes, cbars = plot_by_id(run_id)
    else: # there is a plot already
        for axis in axes:
            axis.clear()
        for cbar in cbars:
            if cbar is not None:
                cbar.remove()
        axes, cbars = plot_by_id(run_id, axes)
        title = make_title(dataset)
        for axis in axes:
            axis.set_title(title)
        plt.pause(pause_time)
    return axes, cbars