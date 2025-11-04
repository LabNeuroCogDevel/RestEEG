#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "psychopy",
# ]
# ///
"""
fill in later for rest rewrite
"""
### LOADING ###
import sys
import os
from psychopy import visual, core, sound, event, gui  # importing key psychopy modules
from psychopy import parallel
from psychopy.sound.audioclip import AudioClip
import platform
import time
import random
import pandas as pd
import numpy as np

NUM_OF_PULSES = 15

# block start trigger values. end values are +1 (101, 201). pulse are //100 (1, 2)
TTL_EYES_CLOSED = 100
TTL_EYES_OPEN = 200

### DEFINING SOUND FILES ###
START_SND = "633.wav"
END_SND = "Correct.wav"
### PSEUDORANDOM BLOCK ORDER A and B ###
A_ORDER = ["closed", "open", "open", "closed", "open", "closed", "closed", "open"]
B_ORDER = ["open", "closed", "closed", "open", "closed", "open", "open", "closed"]


def load_snd(file, sampleRate=44100):
    """Preload sound data"""
    snddata = AudioClip.load(file)
    snddata.resample(sampleRate)
    return snddata


### DEFINING PARALLEL PORT GLOBALLY ###
nodename = platform.uname().node
print(f"running on {nodename}")

# if on the actual linux EEG computer
if nodename in ['eegtask']:
    print(f"is linux EEG")
    USE_TRIGGER = True
    PORT = "/dev/parport0"
    # for win7 PORT=0xD010  # set 2025-10-27; win7
else:
    print("WARNING: Unknown computer, not sending triggers")
    PORT = None
    USE_TRIGGER = False

if USE_TRIGGER:
    print(f"USING TRIGGER on {PORT}")
    pp = parallel.ParallelPort(address=PORT)


### TEST FUNCTION FOR TIMING ###
def timemark(msg):
    t = time.time()  # time in seconds
    print(f"{t:0.5f}\t{t - timemark.t:0.5f}\t{msg}")  # function for 5 numbers shown for seconds
    timemark.t = t  # cache time to report diff
    return t
timemark.t = 0 # initialize cached timestamp

### REST TASK FOR EEG ###
def main():
    ### SUBJECT: INFO ###
    # show box to get info before initiating the task
    subject_info = {
        "sub_id": "",
        "timepoint": "",
        "project": [
            "SPA7T",
            "Habit",
        ],  # this creates a dropdown menu so we can specify project type
        "sound": True,
        "fullscreen": True,
    }

    # creating a pop up dialog  box for entering info and if you cancel the script will end
    dlg = gui.DlgFromDict(subject_info, title="Rest Task Setup")
    if not dlg.OK:  # If user presses cancel
        print("User cancelled the experiment.")
        sys.exit()

    ### SETTING UP FILE NAME AND CONTENTS ###
    os.makedirs('log/', exist_ok=True) # make sure output directory exists
    file_name = f"log/{subject_info['sub_id']}_{subject_info['project']}_{time.time():.0f}.log"
    log_fh = open(file_name, 'w')


    if subject_info["sound"]:
        sound_dev = sound.Sound()
    else:
        # ugly mock of sound_dev for sound=No version
        # here only b/c WF's laptop segfaults w/psyhcopy audio
        sound_dev = lambda: None 
        sound_dev.play = lambda: print("# not playing sound")
        sound_dev.stop = lambda: None 
        sound_dev.setSound = lambda _: None
        sound_dev.duration = .1

    ### WINDOW SETUP ###
    # READY (maybe): if/else on subject_info['fullscreen']
    if subject_info['fullscreen'] == True: 
        win = visual.Window(color = "black", fullscr=True)
    else:
        win = visual.Window(
            [800, 600], color="black", fullscr=False)


    ### FORCE QUIT  - NB. must be set afer win is created
    event.globalKeys.add(key="escape", func=mark_and_quit, name="shutdown")

    # preload the text object to show during fixation
    # Note: this takes ~10ms to create and only needs to happen once
    fixation = visual.TextStim(win, text="+", color="white", wrapWidth=1.5)


    # extracting variables from the box
    sub_id = subject_info["sub_id"]
    timepoint = subject_info["timepoint"]
    project = subject_info["project"]
    print(f"sub_id:{sub_id}\timepoint:{timepoint}\project:{project}",file=log_fh)

    ### INTRODUCTION - INSTRUCTIONS ###
# place before any part of the experiment is called on #
    # first page #
    instructions = (
        "Resting Baseline Task\n\n"
        "This task measures your brain's activity while it is not engaged in any challenging test, or while it is resting.")
    show_instr(win, instructions)
    
    # second page #
    instructions = (
        "We will record your brain activity during 8 one minute-long blocks.\n\n"
        "During some of the blocks we will ask you to close your eyes and keep them closed for the full minute.\n\n"
        "During the other blocks we will ask you to keep your eyes open and look toward the plus sign in the middle of the screen.\n\n"
        "We will mix up the order of the 'eyes open' and 'eyes closed' blocks, and you will not know which type of block is coming up until right before it starts.")
    show_instr(win, instructions)
    
    # third page #
    instructions = (
        "You will hear a tone at the beginning of each block to let you know it is starting. A different tone will play one minute later to let you know that block has finished.\n\n"
        "During all of the blocks, it is very important that you do your best to stay still and to be alert.\n\n"
        "Get Ready...")
    show_instr(win, instructions)

    ### RANDOMIZED BLOCK SETUP ###
    if random.random() > 0.5:  # 50 percent of the time block A will run
        blocks = A_ORDER
    else:
        blocks = B_ORDER  # else 50 percent B block will run
    print(f"Block Order:{blocks}",file=log_fh)

    ### THE EXPERIMENT - EYES OPEN BLOCKS ###
    for block in blocks:

        # free audio sink when timing doesn't matter -- no pending action or trigger
        # takes 10ms

        ### EXPERIMENT BLOCK SETTINGS - EYES CLOSED BLOCKS ###
        if block == "open":
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES OPEN\n\n"
                "The minute will begin when you hear a beep \n\n"
                "When the minute is up, you will hear another beep and the plus sign in the middle of the screen will disappear, which will be your signal that you can relax \n\n"
                "The minute will begin after the next beep...\n\n"
            )
            block_start_trigger = TTL_EYES_OPEN
            end_trigger = block_start_trigger + 1  # 201
            pulse = 2
        elif block == "closed":
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES CLOSED\n\n"
                "Please close your eyes when you hear the next beep\n\n"
                "When the minute is up, you will hear a different beep, which will be your signal that you can open your eyes and relax \n\n"
                "The minute will begin after this next beep...\n\n"
            )
            block_start_trigger = TTL_EYES_CLOSED
            end_trigger = block_start_trigger + 1  # 101
            pulse = 1
        else:
            raise Exception(f"Uknown block type {block}!")

        # prepare sounds. wont play until start
        sound_dev.stop()
        sound_dev.setSound(START_SND)

        ## Run block - either open or closed. settings from above
        show_instr(win, instructions)
        # TODO: log start of block
        print(f"{time.time()}\tstarting {block} (logged before trigger sent)",file=log_fh)

        ## tone
        win.flip()  # empty screen "tone" slide in eprime
        sound_dev.play()
        core.wait(sound_dev.duration)

        # tell biosemi to start recording data file
        send_trigger(128, sleeptime=0.5)

        # indicatte block in status channel (100 = close, 200 = open)
        start = timemark("start_block")
        send_trigger(block_start_trigger, sleeptime=0.5)

        # prep for fixation, not show to screen until flip
        fixation.draw()
        for pulsenumber in range(NUM_OF_PULSES):
            # total time between pulses is 4.1 secs
            wait_end = core.getTime() + 4.1
            send_trigger(pulse, 0.1)
            # only flip to show drawn fix cross on first pass
            if pulsenumber == 0:
                win.flip()

            # likely wait ~4s, but flip might not have been instant
            time_to_wait = wait_end - core.getTime()
            core.wait(time_to_wait)

        end = timemark("end_block")
        send_trigger(end_trigger, 0.1)  # signal end of block
        send_trigger(129, 0.1)  # stop recording
        print(f"Block duration {end - start}")
        sound_dev.setSound(END_SND)
        sound_dev.play()
        show_instr(win, "You can relax...")  # this was originally green font

    ### END OF TASK ###
    show_instr(win, "Rest task is done.")
    win.close()
    core.quit()


### CREATING INSTRUCTIONS ###
def show_instr(win, text):
    instructions = visual.TextStim(win, text=text, color="white", wrapWidth=1.5)
    instructions.draw()  # Draw the text on the screen
    win.flip()  # Update the window to show it
    event.waitKeys(keyList=["space"])


Seconds = float

def send_trigger(value, sleeptime: Seconds):
    if not USE_TRIGGER:
        timemark(f"trigger={value}, sleep {sleeptime}s")
        core.wait(sleeptime)
        return
    pp.setData(value)
    core.wait(sleeptime)
    pp.setData(0)


def mark_and_quit():
    """
    Used to force quit. will send stop trigger to recording device before exiting
    """
    send_trigger(129, 0.1)
    core.quit()


### THIS IS TO START THE EXPERIMENT ###
if __name__ == "__main__":
    main()
