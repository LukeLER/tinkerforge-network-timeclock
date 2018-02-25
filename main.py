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

HOST = "192.168.178.10"
PORT = 4223
UID_RTC = "xPB"     # UID of Real-Time Clock Bricklet
UID_DR = "A6u"      # UID of Dual Relay Bricklet
UID_RLB_1 = "Daq"   # UID of RGB LED Button Bricklet #1
UID_RLB_2 = "Dap"   # UID of RGB LED Button Bricklet #2
UID_OLED = "yjC"    # UID of OLED128 Bricklet
UID_TEMP = "7xw"    # UID of Temperature Bricklet
UID_MB1 = "5VGL9A"  # UID of Master Brick #1
UID_MB2 = "6esDec"  # UID of Master Brick #2

#***********SilentModus***********************
silent = True # False for enabling Status LED*
#*********************************************

openH = 18
openM = 28
closeH = 18
closeM = 31

global opened
global activCH1
global activCH2
opened = 0
activCH1 = False
activCH2 = False

brightness = 5

from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_real_time_clock import BrickletRealTimeClock
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_rgb_led_button import BrickletRGBLEDButton
from tinkerforge.bricklet_oled_128x64 import BrickletOLED128x64
from tinkerforge.bricklet_temperature import BrickletTemperature

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

    temperature = temp.get_temperature()
    oled.write_line(5, 0, "Temperatur :     "+str(temperature/100.0))

    if opened == 0:
      if hour == openH:
        #print("Correct open hour")
        if minute == openM:
          print("Correct open minute")
          oled.write_line(3, 0, "Beleuchtung:      EIN")
          oled.write_line(4, 0, "Beschattung:     OBEN")
          rlb1.set_color(0,brightness,0)
          rlb2.set_color(0,brightness,0)
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          opened = 1

    if opened == 1:
      if hour == closeH:
        #print("Correct close hour")
        if minute == closeM:
          print("Correct close minute")
          oled.write_line(4, 0, "Beschattung:    UNTEN")
          rlb1.set_color(brightness,0,0)
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          time.sleep(10)
          dr.set_state(False, False)
          oled.write_line(3, 0, "Beleuchtung:      AUS")
          rlb2.set_color(brightness,0,0)
          opened = 0

def cb_alarm(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
    global opened
    oled.clear_display()
    time.sleep(10)
    status = dr.get_state()
    if opened == 0:
        oled.write_line(4, 0, "Beschattung:    UNTEN")
    else:
        oled.write_line(4, 0, "Beschattung:     OBEN")
    if status.relay2 == True:
        oled.write_line(3, 0, "Beleuchtung:      EIN")
    else:
        oled.write_line(3, 0, "Beleuchtung:      AUS")

    oled.write_line(7, 0, "IP: 192.168.178.10")

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
            oled.write_line(4, 0, "Beschattung:   faehrt")
            rlb1.set_color(brightness,(brightness/5),0)
            dr.set_monoflop(1, True, 1500)
            time.sleep(5)
            rlb1.set_color(brightness,0,0)
            oled.write_line(4, 0, "Beschattung:    UNTEN")
            opened = 0
        else:
            oled.write_line(4, 0, "Beschattung:   faehrt")
            rlb1.set_color(brightness,(brightness/5),0)
            dr.set_monoflop(1, True, 1500)
            time.sleep(5)
            rlb1.set_color(0,brightness,0)
            oled.write_line(4, 0, "Beschattung:     OBEN")
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
            rlb2.set_color(brightness,0,0)
        else:
            dr.set_selected_state(2, True)
            oled.write_line(3, 0, "Beleuchtung:      EIN")
            rlb2.set_color(0,brightness,0)

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    rtc = BrickletRealTimeClock(UID_RTC, ipcon)   # Create device object
    dr = BrickletDualRelay(UID_DR, ipcon)         # Create device object
    rlb1 = BrickletRGBLEDButton(UID_RLB_1, ipcon) # Create device object
    rlb2 = BrickletRGBLEDButton(UID_RLB_2, ipcon) # Create device object
    oled = BrickletOLED128x64(UID_OLED, ipcon)    # Create device object
    temp = BrickletTemperature(UID_TEMP, ipcon)   # Create device object
    mb1 = BrickMaster(UID_MB1, ipcon)             # Create device object
    mb2 = BrickMaster(UID_MB2, ipcon)             # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    #***********Brick-Config********************************************
    if silent == True:
        mb1.disable_status_led()
        mb2.disable_status_led()
    else:
        mb1.enable_status_led()
        mb2.enable_status_led()

    #***********Dual-Relay-Config***************************************
    dr.set_state(False, False)

    #***********Button-Config*******************************************
    rlb1.set_color(0, brightness, 0) # Tor oben
    rlb2.set_color(brightness, 0, 0) # Licht aus

    if silent == True:
        rlb1.set_status_led_config(rlb1.STATUS_LED_CONFIG_OFF)
        rlb2.set_status_led_config(rlb2.STATUS_LED_CONFIG_OFF)
    else:
        rlb1.set_status_led_config(rlb1.STATUS_LED_CONFIG_ON)
        rlb2.set_status_led_config(rlb2.STATUS_LED_CONFIG_ON)

    rlb1.register_callback(rlb1.CALLBACK_BUTTON_STATE_CHANGED, cb_button1_state_changed)
    rlb2.register_callback(rlb2.CALLBACK_BUTTON_STATE_CHANGED, cb_button2_state_changed)

    #***********RTC-Config**********************************************
    # Register date and time callback to function cb_date_time
    rtc.register_callback(rtc.CALLBACK_DATE_TIME, cb_date_time)
    rtc.register_callback(rtc.CALLBACK_ALARM, cb_alarm)
    rtc.set_alarm(-1, -1, 4, 15, -1, -1, -1) # Reset OLED every morning

    # Set period for date and time callback to 5s (5000ms)
    # Note: The date and time callback is only called every 5 seconds
    #       if the date and time has changed since the last call!
    rtc.set_date_time_callback_period(1000)

    #***********OLED-Config*********************************************
    oled.clear_display()
    oled.write_line(3, 0, "Beleuchtung:      AUS")
    oled.write_line(4, 0, "Beschattung:     OBEN")
    oled.write_line(7, 0, "IP: 192.168.178.10")

    raw_input("Press key to exit\n") # Use input() in Python 3
    ipcon.disconnect()
