# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 12:13:13 2022

@author: 212765608
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 21:14:49 2022

Purpose: Display original, mask, and result video. Allow calibration of HSV values for masks.
"""

# Importing libraries
import numpy as np
import cv2 as cv

#trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass

# Connect to capture device
cap = cv.VideoCapture(0);

# Configures window with 'sliders' to tune HSV bounds for mask
cv.namedWindow("Tracking")
cv.createTrackbar("LH", "Tracking", 0, 255, nothing)
cv.createTrackbar("LS", "Tracking", 0, 255, nothing)
cv.createTrackbar("LV", "Tracking", 0, 255, nothing)
cv.createTrackbar("UH", "Tracking", 255, 255, nothing)
cv.createTrackbar("US", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV", "Tracking", 255, 255, nothing)

# Establishes loop through every frame until webcam is closed
while cap.isOpened():
    
    _, frame = cap.read()
    #frame = cv.fastNlMeansDenoisingColored(frame,None,10,10,7,21)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # create trackbars
    l_h = cv.getTrackbarPos("LH", "Tracking")
    l_s = cv.getTrackbarPos("LS", "Tracking")
    l_v = cv.getTrackbarPos("LV", "Tracking")

    u_h = cv.getTrackbarPos("UH", "Tracking")
    u_s = cv.getTrackbarPos("US", "Tracking")
    u_v = cv.getTrackbarPos("UV", "Tracking")

    # Implement upper and lower bound HSV for masks based on trackbar input
    l_b = np.array([l_h, l_s, l_v])
    u_b = np.array([u_h, u_s, u_v])

    mask = cv.inRange(hsv, l_b, u_b)
    #mask = cv.fastNlMeansDenoising(mask,None,10,10,7,21 )
    res = cv.bitwise_and(frame, frame, mask=mask)

    # find contours in the binary image
    contours, hierarchy = cv.findContours(mask,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv.contourArea(c)
        
        if cv.contourArea(c) > 5000:
            #cv.drawContours(frame,c,-1, (0,255,255),3)
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            #print(area)
            # calculate moments for each contour
            M = cv.moments(c)
             
            # calculate x,y coordinate of center
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
                
            print(cX, ",", cY)
            
            
            cv.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
            cv.putText(frame, "centroid", (cX - 25, cY - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # Create 3 windows (1) original, (2) mask, (3) result
    cv.imshow("frame", frame)
    cv.imshow("mask", mask)
    cv.imshow("res", res)

    # Close webcam feed if q is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()