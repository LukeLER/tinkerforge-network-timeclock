#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

HOST = "localhost"
PORT = 4223
UID_RTC = "xPB" # UID of Real-Time Clock Bricklet
UID_DR = "A6u" 
UID_RLB_1 = "Dap"
UID_RLB_2 = "Daq"
UID_OLED = "yjC"

openH = 15
openM = 13
closeH = 15
closeM = 14

global opened
global activCH1
global activCH2

opened = 0
activCH1 = False
activCH2 = False

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_real_time_clock import BrickletRealTimeClock
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_rgb_led_button import BrickletRGBLEDButton
from tinkerforge.bricklet_oled_128x64 import BrickletOLED128x64

# Callback function for date and timefrom tinkerforge.bricklet_dual_relay import BrickletDualRelay callback
def cb_date_time(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
    global opened

    #print("Year: " + str(year))
    #print("Month: " + str(month))
    #print("Hour: " + str(hour))
    #print("Minute: " + str(minute))
    #print("Second: " + str(second))
    #print("Weekday: " + str(weekday))
    #print("")
    #oled.clear_display()

    oled.write_line(0, 2, str(day)+"."+str(month)+"."+str(year)+" | "+str(hour)+":"+str(minute)+":"+str(second))
    
    if opened == 0:
      if hour == openH:
        print("Correct open hour")
        if minute == openM:
          print("Correct open minute")
          oled.write_line(3, 0, "Beleuchtung:      EIN")
          oled.write_line(4, 0, "Beschattung:     OBEN")
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          opened = 1

    if opened == 1:
      if hour == closeH:
        print("Correct close hour")
        if minute == closeM:
          print("Correct close minute")
          oled.write_line(4, 0, "Beschattung:    UNTEN")
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          time.sleep(10)
          dr.set_state(False, False)
          oled.write_line(3, 0, "Beleuchtung:      AUS")
          opened = 0
    
#def cb_alarm(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
#    dr.set_state(True, True)
#    time.sleep(2)
#    dr.set_state(False, True)

def cb_button1_state_changed(state):
    global activCH1
    #print("State 1: " + str(state))
    if state == rlb1.BUTTON_STATE_PRESSED:
        if activCH1 == False:
            activCH1 = True
        else:
            activCH1 = False
        if activCH1 == True:
            #old0.write_line(1, 15, " MUTE ")
            rlb1.set_color(100,0,0)
        else:
            #old0.write_line(1, 15, "      ")
            rlb1.set_color(0,100,0)

def cb_button2_state_changed(state):
    global activCH2
    #print("State 2: " + str(state))
    if state == rlb2.BUTTON_STATE_PRESSED:
        if activCH2 == False:
            activCH2 = True
        else:
            activCH2 = False
        if activCH2 == True:
            #old0.write_line(1, 15, " MUTE ")
            rlb2.set_color(100,0,0)
        else:
            #old0.write_line(1, 15, "      ")
            rlb2.set_color(0,100,0)

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    rtc = BrickletRealTimeClock(UID_RTC, ipcon) # Create device object
    dr = BrickletDualRelay(UID_DR, ipcon) # Create device object
    rlb1 = BrickletRGBLEDButton(UID_RLB_1, ipcon) # Create device object
    rlb2 = BrickletRGBLEDButton(UID_RLB_2, ipcon) # Create device object
    oled = BrickletOLED128x64(UID_OLED, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected
    
    dr.set_state(False, False)
    rlb1.set_color(0, 100, 0) # Tor oben
    rlb2.set_color(100, 0, 0) # Licht aus

    # Register date and time callback to function cb_date_time
    rtc.register_callback(rtc.CALLBACK_DATE_TIME, cb_date_time)
    #rtc.register_callback(rtc.CALLBACK_ALARM, cb_alarm)
    
    rlb1.register_callback(rlb1.CALLBACK_BUTTON_STATE_CHANGED, cb_button1_state_changed)
    rlb2.register_callback(rlb2.CALLBACK_BUTTON_STATE_CHANGED, cb_button2_state_changed)

    # Set period for date and time callback to 5s (5000ms)
    # Note: The date and time callback is only called every 5 seconds
    #       if the date and time has changed since the last call!
    rtc.set_date_time_callback_period(1000)
    #rtc.set_alarm(-1, -1, 13, 17, -1, -1, -1)

    oled.write_line(7, 0, "IP: localhost")
    
    raw_input("Press key to exit\n") # Use input() in Python 3
    ipcon.disconnect()
