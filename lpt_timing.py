#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "mne", "numpy"
# ]
# ///
"""
Read in bdf file and calculate time between triggers.

BioSemi Status channel correction from /Volumes/Hera/Projects/Habit/task/results/LoeffEEGPhotoTiming
"""

import os.path
import sys
import mne
import numpy as np

def add_stim_corrected(raw):
    raw.load_data()
    stim_raw = raw.pick_channels(["Status"]).get_data()
    info = mne.create_info(["StatusCorrected"], raw.info["sfreq"], ["stim"])
    stim_vals = correct_ttl(stim_raw[0]).reshape(stim_raw.shape)
    stim = mne.io.RawArray(stim_vals, info)
    raw.add_channels([stim], force_update_info=True)

def read_events(bdf):
    "read events by making a new channel"
    ## read in eeg and get separate stim channel info
    eeg = mne.io.read_raw_bdf(bdf)
    # eeg.describe() # 247808 (484.0 s) == 512Hz

    # events = mne.find_events(eeg, shortest_event=2)
    add_stim_corrected(eeg)
    events = mne.find_events(eeg, stim_channel="StatusCorrected", shortest_event=2)
    return (events, eeg.info)

def correct_ttl(x):
    """mne expects 8bit channel. biosemi has 24 bit. go down to 16 and adjust
    >>> correct_ttl(np.array([16128],dtype='int64')) # first stim ch val
    np.array([0],dtype='int16')
    """
    return x.astype(np.int32) - 127**2 + 1
    v = x - 16128  #  np.log2(16128+256)==14
    v[v == 65536] = 0  # 65536==2**16
    return v

if len(sys.argv) != 2:
    raise Exception("Need bdf file as sole argument to script")
elif not os.path.isfile(sys.argv[1]):
    raise Exception(f"Bad input argument: '{sys.argv[1]}' must be a bdf file")

bdf = sys.argv[1]
events, info = read_events(bdf)
print(info)

trigger = events[:,2]

ttl_search = 100
# info.sfreq == 512
time_between_pulse = np.diff(events[trigger == ttl_search, 0] / 512.0)
print(time_between_pulse)
