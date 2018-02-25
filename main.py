#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#                                                                      #
# Timeclock for our Garage                                             #
#                                                                      #
# Copyright (C) 2018 by Lukas Lauer <lukas@doppel-l.de>                #
#                                                                      #
# Relay Channel 1: Garagedoor                                          #
# Relay Channel 2: Lights                                              #
#                             s                                         #
########################################################################

import time

HOST = "localhost"
PORT = 4223
UID_RTC = "xPB" # UID of Real-Time Clock Bricklet
UID_DR = "A6u" 
UID_RLB_1 = "Daq"
UID_RLB_2 = "Dap"
UID_OLED = "yjC"

openH = 17
openM = 47
closeH = 17
closeM = 48

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

    if second == 0 or second == 1 or second == 2 or second == 3 or second == 4 or second == 5 or second == 6 or second == 7 or second == 8 or second == 9:
      second = "0"+str(second)
    if minute == 0 or minute == 1 or minute == 2 or minute == 3 or minute == 4 or minute == 5 or minute == 6 or minute == 7 or minute == 8 or minute == 9:
      minute = "0"+str(minute)
    if hour == 0 or hour == 1 or hour == 2 or hour == 3 or hour == 4 or hour == 5 or hour == 6 or hour == 7 or hour == 8 or hour == 9:
      hour = "0"+str(hour)
    if day == 0 or day == 1 or day == 2 or day == 3 or day == 4 or day == 5 or day == 6 or day == 7 or day == 8 or day == 9:
      day = "0"+str(day)
    if month == 0 or month == 1 or month == 2 or month == 3 or month == 4 or month == 5 or month == 6 or month == 7 or month == 8 or month == 9:
      month = "0"+str(month)
    
    oled.write_line(0, 2, str(day)+"."+str(month)+"."+str(year)+" | "+str(hour)+":"+str(minute)+":"+str(second))
    
    if opened == 0:
      if hour == openH:
        print("Correct open hour")
        if minute == openM:
          print("Correct open minute")
          oled.write_line(3, 0, "Beleuchtung:      EIN")
          oled.write_line(4, 0, "Beschattung:     OBEN")
          rlb1.set_color(0,20,0)
          rlb2.set_color(0,20,0)
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
          rlb1.set_color(20,0,0)
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          time.sleep(10)
          dr.set_state(False, False)
          oled.write_line(3, 0, "Beleuchtung:      AUS")
          rlb2.set_color(20,0,0)
          opened = 0
    
#def cb_alarm(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
#    dr.set_state(True, True)
#    time.sleep(2)
#    dr.set_state(False, True)

def cb_button1_state_changed(state):
    global activCH1
    global opened
    #print("State 1: " + str(state))
    if state == rlb1.BUTTON_STATE_PRESSED:
        if activCH1 == False:
            activCH1 = True
        else:
            activCH1 = False
        if activCH1 == True:
            oled.write_line(4, 0, "Beschattung:    UNTEN")
            rlb1.set_color(20,4,0)
            dr.set_monoflop(1, True, 1500)
            time.sleep(5)
            rlb1.set_color(20,0,0)
            opened = 0
        else:
            oled.write_line(4, 0, "Beschattung:     OBEN")
            rlb1.set_color(20,4,0)
            dr.set_monoflop(1, True, 1500)
            time.sleep(5)
            rlb1.set_color(0,20,0)
            opened = 1

def cb_button2_state_changed(state):
    global activCH2
    #print("State 2: " + str(state))
    if state == rlb2.BUTTON_STATE_PRESSED:
        if activCH2 == False:
            activCH2 = True
        else:
            activCH2 = False
        if activCH2 == True:
            dr.set_selected_state(2, False)
            oled.write_line(3, 0, "Beleuchtung:      AUS")
            rlb2.set_color(20,0,0)
        else:
            dr.set_selected_state(2, True)
            oled.write_line(3, 0, "Beleuchtung:      EIN")
            rlb2.set_color(0,20,0)

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
    rlb1.set_color(0, 20, 0) # Tor oben
    rlb2.set_color(20, 0, 0) # Licht aus

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
    
    oled.clear_display()
    oled.write_line(3, 0, "Beleuchtung:      AUS")
    oled.write_line(4, 0, "Beschattung:     OBEN")
    oled.write_line(7, 0, "IP: localhost")
    
    raw_input("Press key to exit\n") # Use input() in Python 3
    ipcon.disconnect()
