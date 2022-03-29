# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 21:30:21 2022

Purpose: Splitting and merging color channels in OpenCV
"""

# Importing libraries
import numpy as np
import cv2 as cv

# Saving picture data into array
img = cv.imread(r'C:\Users\bobby\Documents\Education\Boston University\EC544\Project\gameboy_games.jpg')

# Splitting and Merging Channels Method 1
b, g, r = cv.split(img)
img = cv.merge((b,g,r))

# Splitting and Merging Channels Method 2
b = img[:,:,0]
g = img[:,:,1]
r = img[:,:,2]

# Concatenates color channels (in grayscale) into single image
gray_scale = np.concatenate((r, g, b), axis=1)
cv.imwrite('gray_scale.png',gray_scale)


# Concatenates color channels (in color) into single image
zeros = np.zeros(img.shape[:2], dtype = 'uint8')
r1 = cv.merge([zeros, zeros, r])
g1 = cv.merge([zeros, g, zeros])
b1 = cv.merge([b, zeros, zeros])
color_scale = np.concatenate((r1, g1, b1), axis=1)
cv.imwrite('color_scale.png',color_scale)



## Examples of showing color channels individually 

#shows different grayscale images with intensites of R G B
#cv.imshow('Red',r)
#cv.imshow('Green',g)
#cv.imshow('Blue',b)

#cv.imshow('grayscale_channels', gray_scale)
#cv.waitKey(0)
#cv.destroyAllWindows()

#remake merge into original using split channels
#merge_image = cv.merge([b,g,r])
#cv.imshow("Merged",merge_image)
#cv.waitKey(0)
#cv.destroyAllWindows()

#image channels can be amplified by 
#adding values to parameters in merge func
#to get individual colored images 
#create a zero matrix same size as that of input dimensions h x w using numpy

#cv.imshow('Red',cv.merge([zeros, zeros, r]))
#cv.imshow('Blue',cv.merge([b,zeros,zeros]))
#cv.imshow('Green',cv.merge([zeros,g,zeros]))
#cv.waitKey(0)
#cv.destroyAllWindows() 
#cv.imwrite('outputred.jpg',cv.merge([zeros,zeros,r]))
#cv.imwrite('outputblue.jpg',cv.merge([b,zeros,zeros]))
#cv.imwrite('outputgreen.jpg',cv.merge([zeros,g,zeros]))


