# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:37:36 2023

@author: francis.gagne
"""

import win32api #, win32con
#import datetime as dt
#import numpy as np
import time
import vgamepad as vg

#Parameters
polling_rate = 100
#Key Numbers are ASCII Values
KEY_GAS = 38 #UP ARROW
KEY_BRAKE1 = 40 #DOWN ARROW
KEY_BRAKE2 = 32 #SPACE
KEY_LEFT = 37 #LEFT ARROW
KEY_RIGHT = 39 #RIGHT ARROW
KEY_SMOOTH_SENSITIVE = 69 #E
KEY_SMOOTH_PRECISE = 70 #F

#CREATE Values
acceleration_press = [0,0,0]
acceleration_release = [0,0,0]
velocity_min_press = [0,0,0]
velocity_min_release = [0,0,0]
spring_force = [0,0,0]
damping_force = [0,0,0]
output_limit = [0,0,0]


#SENSITIVE Values
#acceleration_press[1] = 0.8
#acceleration_release[1] = 0.3
#spring_force[1] = 0.002
#damping_force[1] = 0.05
acceleration_press[1] = 0.5
acceleration_release[1] = 2.0
velocity_min_press[1] = 8
velocity_min_release[1] = 8
spring_force[1] = 0.002
damping_force[1] = 0.02
output_limit[1] = 80

#PRECISE Values
acceleration_press[2] = 0.4
acceleration_release[2] = 0.25
velocity_min_press[2] = 2
velocity_min_release[2] = 2
spring_force[2] = 0.005
damping_force[2] = 0.07
output_limit[2] = 100

#DIRECT Values
acceleration_press[0] = 100
acceleration_release[0] = 100
velocity_min_press[0] = 30
velocity_min_release[0] = 30
spring_force[0] = 0
damping_force[0] = 0
output_limit[0] = 100

#INITIALIZE VALUES
gamepad = vg.VX360Gamepad()
output_value = 0
output_velocity = 0
currentside = 1
NotBreak = True
gas = False
brake = False
last_index = 0

while NotBreak:  
    #Check if Smooth SEN or PRC key is pressed down. Always use the first pressed key
    if win32api.GetAsyncKeyState(KEY_SMOOTH_SENSITIVE)&0x8000 and last_index != 2: index=1
    elif win32api.GetAsyncKeyState(KEY_SMOOTH_PRECISE)&0x8000 and last_index != 1: index=2
    else: index = 0
    #print(index)
    
    acceleration = -acceleration_release[index]
    velocity_min = -velocity_min_release[index]
    if currentside == -1: acceleration = -acceleration
    if currentside == -1: velocity_min = -velocity_min
    
    # if win32api.GetAsyncKeyState(27)&0x8000:
    #     #print("Escape")
    #     NotBreak = False #Exit the loop
    #     acceleration = acceleration_press[index]
        
    if win32api.GetAsyncKeyState(KEY_LEFT)&0x8000:
        #print("<- LEFT")    
        acceleration = acceleration_press[index]
        if output_velocity < velocity_min_press[index]: output_velocity = velocity_min_press[index]
        if currentside == -1:
           output_value = 0
           output_velocity = velocity_min_press[index]         
        currentside = 1      
    elif win32api.GetAsyncKeyState(KEY_RIGHT)&0x8000:
        #print("RIGHT->")       
        acceleration = -acceleration_press[index]
        if output_velocity > -velocity_min_press[index]: output_velocity = -velocity_min_press[index]
        if currentside == 1:
           output_value = 0
           output_velocity = velocity_min_press[index]
        currentside = -1
    else:
        acceleration = acceleration #Do nothing for now
        if output_velocity*currentside < velocity_min_release[index]: output_velocity = -velocity_min_release[index]*currentside 
        

    #print(output_velocity)
    output_velocity = output_velocity + acceleration - output_value*spring_force[index] - output_velocity*damping_force[index]
    output_value = output_value + output_velocity
    if output_value*currentside >= output_limit[index] :
        output_value = output_limit[index]*currentside
        output_velocity = 0
    if output_value*currentside <= 0:
        output_value = 0
        output_velocity = 0
        
    #Check for GAS
    if not gas and win32api.GetAsyncKeyState(KEY_GAS)&0x8000:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gas = True
        #print("GAS")
    elif gas and not win32api.GetAsyncKeyState(KEY_GAS)&0x8000:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gas = False
        
    #Check for BRAKE (UP or SPACE)
    if not brake and (win32api.GetAsyncKeyState(KEY_BRAKE1)&0x8000 or win32api.GetAsyncKeyState(KEY_BRAKE2)&0x8000) :
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        brake = True
        #print("BRAKE")
    elif brake and not (win32api.GetAsyncKeyState(KEY_BRAKE1)&0x8000 or win32api.GetAsyncKeyState(KEY_BRAKE2)&0x8000) :
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        brake = False
        
     
    #print(output_value)
    #bars = int(abs(output_value)/10)
    #print("▮"*bars+"▯"*(10-bars))
    gamepad.left_joystick(x_value=int(output_value*-327.67), y_value=0)
    
    #Update Game Pad Value
    gamepad.update()   
    
    time.sleep(1/polling_rate)
    
del gamepad