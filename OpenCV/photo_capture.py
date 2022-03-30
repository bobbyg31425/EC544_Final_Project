# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 20:35:02 2022

Purpose: Take a photo via the webcam
"""

# Importing libraries
import numpy as np
import cv2 as cv
import os
from matplotlib import pyplot as plt

# Connect to capture device
cap = cv.VideoCapture(0)
ret, frame = cap.read()

# Show and save capture
# Note: plt.imshow flips R and B color channels since
# capture is in RGB format, but OpenCV looks for BGR format 
plt.imshow(frame)
cv.imwrite('webcam_photo.jpg',frame)

# Releases camera from being 'in use'
cap.release()