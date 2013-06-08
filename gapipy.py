#!/usr/bin/env python2.7
# Based on Alex Eames' python scripts for gertboard, see http://RasPi.TV

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)      #Run in BCM mode

# Now set up the detection for the buttons
for i in range(23,26):
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP) #sets up for switches to1 be detected on gertboard
    GPIO.add_event_detect(i, GPIO.RISING, bouncetime=200)  #Defines an event 

# Print instructions to user
print "These are the connections for the Gertboard buttons test:"
print "GP25 in J2 --- B1 in J3"
print "GP24 in J2 --- B2 in J3"
print "GP23 in J2 --- B3 in J3"
print "Optionally, if you want the LEDs to reflect button state do the following:"
print "jumper on U3-out-B1"
print "jumper on U3-out-B2"
print "jumper on U3-out-B3"

raw_input("When ready hit enter.\n")

while True:
    if GPIO.event_detected(23): #calls based on add_event_detect -- you could run a callback in add_event_detect to do more
        print "button press on channel 23 \n"
    if GPIO.event_detected(24):
        print "something 24"
    if GPIO.event_detected(25):
        print "something 25"
