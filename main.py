#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

HOST = "localhost"
PORT = 4223
UID_RTC = "xPB" # UID of Real-Time Clock Bricklet
UID_DR = "A6u" 

openH = 13
openM = 53
closeH = 13
closeM = 54

global opened
opened = 0

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_real_time_clock import BrickletRealTimeClock
from tinkerforge.bricklet_dual_relay import BrickletDualRelay

# Callback function for date and timefrom tinkerforge.bricklet_dual_relay import BrickletDualRelay callback
def cb_date_time(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
    global opened
    
    print("Year: " + str(year))
    print("Month: " + str(month))
    print("Hour: " + str(hour))
    print("Minute: " + str(minute))
    print("Second: " + str(second))
    print("Weekday: " + str(weekday))
    print("")
    
    if opened == 0:
      if hour == openH:
        print("Correct open hour")
        if minute == openM:
          print("Correct open minute")
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          opened = 1

    if opened == 1:
      if hour == closeH:
        print("Correct close hour")
        if minute == closeM:
          print("Correct close minute")
          dr.set_state(True, True)
          time.sleep(2)
          dr.set_state(False, True)
          time.sleep(10)
          dr.set_state(False, False)
          opened = 0
    
#def cb_alarm(year, month, day, hour, minute, second, centisecond, weekday, timestamp):
#    dr.set_state(True, True)
#    time.sleep(2)
#    dr.set_state(False, True)

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    rtc = BrickletRealTimeClock(UID_RTC, ipcon) # Create device object
    dr = BrickletDualRelay(UID_DR, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected
    
    dr.set_state(False, False)

    # Register date and time callback to function cb_date_time
    rtc.register_callback(rtc.CALLBACK_DATE_TIME, cb_date_time)
    #rtc.register_callback(rtc.CALLBACK_ALARM, cb_alarm)

    # Set period for date and time callback to 5s (5000ms)
    # Note: The date and time callback is only called every 5 seconds
    #       if the date and time has changed since the last call!
    rtc.set_date_time_callback_period(1000)
    #rtc.set_alarm(-1, -1, 13, 17, -1, -1, -1)

    raw_input("Press key to exit\n") # Use input() in Python 3
    ipcon.disconnect()
