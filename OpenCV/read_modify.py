# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 20:49:54 2022

Purpose: Accessing and modifying picture data using OpenCV
"""

# Importing libraries
import numpy as np
import cv2 as cv

# Saving picture data into array
img = cv.imread(r'C:\Users\bobby\Pictures\games\IMG_3409.jpg')

# Access pixel RGB info by its row and column coordinates
px = img[100,100]
print("RGB [B, G, R] of pixel 100x100: ", px)

# Access only a specific color (B = 0, G = 1, R = 2)
blue = img[100,100,0]
print("BLUE of pixel 100x100: ", blue)

# Modify pixel values
img[100,100] = [255,255,255]
print(img[100,100])

# Better pixel accessing and editing method
print("Original RED of pixel 10x10: ", img.item(10,10,2))
img.itemset((10,10,2),100)
print("Modified RED of pixel 10x10: ", img.item(10,10,2))

# Image properties
print("Image shape: ", img.shape) # returns picture dimensions (rows, cols, channels)
print("Image size: ", img.size) # returns number of pixels accessed
print("Image datatype: ", img.dtype) # returns datatype of array elements
