# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 21:14:49 2022

Purpose: Take a video via the webcam and save file
"""

# Importing libraries
import numpy as np
import cv2 as cv
import os
from matplotlib import pyplot as plt

# Connect to capture device
cap = cv.VideoCapture(0)


# Get video properties
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
fps = cap.get(cv.CAP_PROP_FPS)


# Video writer
video_writer = cv.VideoWriter('output.avi', cv.VideoWriter_fourcc('M','J','P','G'), fps, (width, height)) 

# Establishes loop through every frame until webcam is closed
while cap.isOpened():
    ret, frame = cap.read()
    
    # Show image to user
    cv.imshow('Webcam', frame)
    
    # Write out frame 
    video_writer.write(frame)
    
    # Close webcam feed if q is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()

# Release video writer
video_writer.release()