#!/usr/bin/env python3
"""
fill in later for rest rewrite
"""
### LOADING ###
from psychopy import visual, core, sound, event, gui  # importing key psychopy modules
from psychopy import parallel
from psychopy.sound.audioclip import AudioClip
import time
import random
import pandas as pd
import numpy as np

USE_TRIGGER = False
NUM_OF_PULSES = 15

### DEFINING SOUND FILES ###
sound = sound.Sound()
open_snd = "Correct.wav"
close_snd = "633.wav"


def load_snd(file, sampleRate=sound.sampleRate):
    snddata = AudioClip.load(file)
    snddata.resample(sampleRate)
    return snddata


### DEFINING PARALLEL PORT GLOBALLY ###
PORT = 0xD010  # set 2025-10-27; win7
if USE_TRIGGER:
    print(f"USING TRIGGER on {PORT}")
    pp = parallel.ParallelPort(address=PORT)


### TEST FUNCTION FOR TIMING ###
def timemark(msg):
    t = time.time()  # time in seconds
    print(f"{t:0.5f}\t{msg}")  # function for 5 numbers shown for seconds
    return t


### REST TASK FOR EEG ###
def main():
    ### FORCE QUIT ###
    event.globalKeys.add(key="escape", func=mark_and_quit, name="shutdown")

    ### WINDOW SETUP ###
    win = visual.Window(
        [800, 600], color="black", fullscr=False
    )  # set to True for fullscreen

    ### SUBJECT INFO ###
    # show box to get info before initiating the task
    subject_info = {
        "sub_id": "",
        "run_num": "",
        "timepoint": "",
        "project": [
            "SPA7T",
            "Habit",
        ],  # this creates a dropdown menu so we can specify project type
    }

    # creating a pop up dialog  box for entering info and if you cancel the script will end
    dlg = gui.DlgFromDict(subject_info, title="Rest Task Setup")
    if not dlg.OK:  # If user presses cancel
        print("User cancelled the experiment.")
        sys.exit()

    # extracting variables from the box
    sub_id = subject_info["sub_id"]
    run_num = subject_info["run_num"]
    timepoint = subject_info["timepoint"]
    project = subject_info["project"]

    ### INTRODUCTION - INSTRUCTIONS ###
    # place before any part of the experiment is called on #
    instructions = (
        "Welcome to the LNCD resting task. Press spacebar to continue"
        "In this task you will do X, Y, Z. (press spacebar)"
        "The minute will begin after the next beep."
    )
    show_instr(win, instructions)

    ### PSEUDORANDOM BLOCK ORDER A and B ###
    A = ["closed", "open", "open", "closed", "open", "closed", "closed", "open"]
    B = ["open", "closed", "closed", "open", "closed", "open", "open", "closed"]

    ### RANDOMIZED BLOCK SETUP ###
    if random.random() > 0.5:  # 50 percent of the time block A will run
        blocks = A
    else:
        blocks = B  # else 50 percent B block will run
    print("Block order:", blocks)  # if interested in logging the order of blocks

    ### THE EXPERIMENT - EYES OPEN BLOCKS ###
    for block in blocks:

        # free audio sink when timing doesn't matter -- no pending action or trigger
        # takes 10ms
        sound.stop()

        ### EXPERIMENT BLOCK SETTINGS - EYES CLOSED BLOCKS ###
        if block == "open":
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES OPEN\n\n"
                "The minute will begin when you hear a beep \n\n"
                "When the minute is up, you will hear another beep and the plus sign in the middle of the screen will disappear, which will be your signal that you can relax \n\n"
                "The minute will begin after the next beep...\n\n"
            )
            sound.setSound(open_snd)
            trigger = 200
            end_trigger = 201
            pulse = 2
        elif block == "closed":
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES CLOSED\n\n"
                "Please close your eyes when you hear the next beep\n\n"
                "When the minute is up, you will hear a different beep, which will be your signal that you can open your eyes and relax \n\n"
                "The minute will begin after this next beep...\n\n"
            )
            trigger = 100
            end_trigger = 101
            pulse = 1
            sound.setSound(close_snd)

        ## Run block - either open or closed. settings from above
        show_instr(win, instructions)
        win.flip()  # empty screen "tone" slide in eprime
        sound.play()
        # tell biosemi to start recording data file
        send_trigger(128, sleeptime=0.5)

        # indicatte block in status channel (100 = close, 200 = open)
        b = timemark("start_block")
        t = b
        send_trigger(trigger, sleeptime=0.5)

        for pulsenumber in range(NUM_OF_PULSES):
            t2 = timemark("inner_pulse")
            print(t2 - t)
            t = t2
            send_trigger(pulse, 0.1)
            show_fix(win, duration=4)  # 4 secs
        t = timemark("end_block")
        print(t - b)
        send_trigger(end_trigger, 0.1)  # signal end of block
        send_trigger(129, 0.1)  # stop recording
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


### FIXATION CROSS ###
def show_fix(win, duration=10):
    fixation = visual.TextStim(win, text="+", color="white", wrapWidth=1.5)
    fixation.draw()
    win.flip()
    core.wait(duration)


Seconds = int


def send_trigger(value, sleeptime: Seconds):
    if not USE_TRIGGER:
        print(f"would send {value} and sleep {sleeptime}")
        core.wait(sleeptime)
        return
    pp.setData(value)
    core.wait(sleeptime)
    pp.setData(0)


def mark_and_quit():
    """
    Used to force quit. will send stop trigger to recording device before exiting
    """
    event.waitKeys(keyList=["escape"])
    send_trigger(129, 0.1)
    core.quit()


### THIS IS TO START THE EXPERIMENT ###
if __name__ == "__main__":
    main()
