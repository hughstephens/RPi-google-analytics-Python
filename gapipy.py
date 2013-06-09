#!/usr/bin/env python2.7
# Based on Alex Eames' python scripts for gertboard, see http://RasPi.TV
# uses 'pyus' project from regisd/pyus as basis for pushing calls to GA

import RPi.GPIO as GPIO
from pyus import AppTracker
GPIO.setmode(GPIO.BCM)      #Run in BCM mode

# Now set up the detection for the buttons
for i in range(23,26):
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP) #sets up for switches to1 be detected on gertboard
    GPIO.add_event_detect(i, GPIO.RISING, bouncetime=200)  #Defines an event 


raw_input("When ready hit enter.\n")

while True:
    if GPIO.event_detected(23): #calls based on add_event_detect -- you could run a callback in add_event_detect to do more
        AppTracker("coffeemachine","UA-41589819-1").track_event("coffee","make",label="machine",value=1)
    if GPIO.event_detected(24):
        print('something 24')
    if GPIO.event_detected(25):
        print('something 25')
