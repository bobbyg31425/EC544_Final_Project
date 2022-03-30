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
plt.imshow(cv.cvtColor(frame,cv.COLOR_BGR2RGB))
cv.imwrite('webcam_photo.jpg',frame)

# Releases camera from being 'in use'
cap.release()