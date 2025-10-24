#!/usr/bin/env python3
"""
fill in later for rest rewrite
"""
### LOADING ###
from psychopy import visual, core, sound, event, gui  #importing key psychopy modules
import time
import random
import pandas as pd
import numpy as np
USE_TRIGGER = False

### DEFINING SOUND FILES ###
open_sound = sound.Sound('Correct.wav')
closed_sound = sound.Sound('633.wav')

### REST TASK FOR EEG ###
def main():
### FORCE QUIT ###
    event.globalKeys.add(key='escape', func=mark_and_quit, name='shutdown')

### WINDOW SETUP ###
    win = visual.Window([800, 600],
    color = 'black',
    fullscr = False) #set to True for fullscreen

### IMPORTING AUDIO ###
    #beep = sound.Sound(value=1000, secs=2) 

### PARALLEL PORT SETUP ###
    #from lncdtask.externalcom import ParallelPortEEG 
    #import psychopy.parallel
    #PORT = 53264  #connecting to the EEG hardware "/dev/ttyS0" might be a serial port
    #pp = psychopy.parallel.ParallelPort(address=PORT)
    #pp = ParallelPortEEG(address=PORT) 

    # utilize the following throuhgout the experiment #
    #pp.start() #start communication with EEG
    #pp.send(10) #send signal/trigger to EEG via port 
    #pp.stop()

### SUBJECT INFO ###
    #show box to get info before initiating the task
    subject_info = {
    'sub_id': '',
    'run_num': '', 
    'timepoint': '',
    'project': ['SPA7T', 'Habit'] #this creates a dropdown menu so we can specify project type
    }

    #creating a pop up dialog  box for entering info and if you cancel the script will end
    dlg = gui.DlgFromDict(subject_info, title="Rest Task Setup")
    if not dlg.OK:  # If user presses cancel
        print("User cancelled the experiment.")
        sys.exit()
    
    #extracting variables from the box
    sub_id = subject_info['sub_id']
    run_num = subject_info['run_num']
    timepoint = subject_info['timepoint']
    project = subject_info['project']
    
### INTRODUCTION - INSTRUCTIONS ### 
    # place before any part of the experiment is called on #
    instructions = (
        "Welcome to the LNCD resting task. Press spacebar to continue"
        "In this task you will do X, Y, Z. (press spacebar)"
        "The minute will begin after the next beep.")
    show_instr(win, instructions)

### PSEUDORANDOM BLOCK ORDER A and B ###
    A = ['closed', 'open', 'open', 'closed', 'open', 'closed', 'closed', 'open']
    B = ['open', 'closed', 'closed', 'open', 'closed', 'open', 'open', 'closed']

### RANDOMIZED BLOCK SETUP ###
    if random.random() > 0.5: #50 percent of the time block A will run
        blocks = A 
    else:
        blocks = B #else 50 percent B block will run 
    print('Block order:', blocks) #if interested in logging the order of blocks 

    ### THE EXPERIMENT - EYES OPEN BLOCKS ###
    for block in blocks:
        ### EXPERIMENT BLOCK SETTINGS - EYES CLOSED BLOCKS ###
        if block == 'open':
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES OPEN\n\n"
                "The minute will begin when you hear a beep \n\n"
                "When the minute is up, you will hear another beep and the plus sign in the middle of the screen will disappear, which will be your signal that you can relax \n\n"
                "The minute will begin after the next beep...\n\n")
            tone = open_sound
            trigger = 200
            pulse = 2
        elif block == 'closed':
            instructions = (
                "The next block will be one minute with your\n\n"
                "EYES CLOSED\n\n"
                "Please close your eyes when you hear the next beep\n\n"
                "When the minute is up, you will hear a different beep, which will be your signal that you can open your eyes and relax \n\n"
                "The minute will begin after this next beep...\n\n")
            trigger = 100
            pulse = 1
            tone = closed_sound
        
        ## Run block - either open or closed. settings from above
        show_instr(win, instructions)
        win.flip() # empty screen "tone" slide ineprime
        tone.play()
        send_trigger(128, sleeptime=.5) # start recording
        send_trigger(trigger, 0) # block trigger  100 or 200
        
        for pulsenumber in range(15):
            send_trigger(pulse, 0.1)
            show_fix(win, duration=4)  # 4 secs
        send_trigger(129, 0.1) # stop recording
        show_instr(win, "You can relax...") #this was originally green font

### END OF TASK ###
    show_instr(win, 'Rest task is done.')
    win.close()
    core.quit()
    
### CREATING INSTRUCTIONS ###
def show_instr(win, text):
    instructions = visual.TextStim(win, text=text, color='white', wrapWidth=1.5)
    instructions.draw()  # Draw the text on the screen
    win.flip()  # Update the window to show it
    event.waitKeys(keyList=['space'])

### FIXATION CROSS ###
def show_fix(win, duration=10):
    fixation = visual.TextStim(win, text='+', color='white', wrapWidth=1.5)
    fixation.draw()
    win.flip()
    core.wait(duration) # duration 10 seconds for test but eventually 60 secs

Seconds = int
def send_trigger(value, sleeptime : Seconds):
     if not USE_TRIGGER:
        print(f"would send {value} and sleep {sleeptime}")
        return
     send(value)
     core.wait(sleeptime)
     send(0)
     
def mark_and_quit():
    """
    Used to force quit. will send stop trigger to recording device before exiting
    """
    event.waitKeys(keyList=['escape'])
    send_trigger(129, 0.1)
    core.quit()

###PLAYING THE SOUND ###
#def beep(win, sound):
    #beep.play()
    #core.wait(2)
    
### THIS IS TO START THE EXPERIMENT ###
if __name__ == "__main__":
    main() 