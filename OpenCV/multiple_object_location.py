# -*- coding: utf-8 -*-
"""
Created on Mon April 11 2022
Purpose: track multiple color objects at the same time
"""

# Importing libraries
import numpy as np
import cv2 as cv

#trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass

# Connect to capture device
cap = cv.VideoCapture(0);

# Configures window with 'sliders' to tune HSV bounds for masks of object 1 and object 2
cv.namedWindow("Tracking",cv.WINDOW_NORMAL)

cv.createTrackbar("LH_1", "Tracking", 0, 255, nothing) # object 1
cv.createTrackbar("LS_1", "Tracking", 0, 255, nothing)
cv.createTrackbar("LV_1", "Tracking", 0, 255, nothing)
cv.createTrackbar("UH_1", "Tracking", 255, 255, nothing)
cv.createTrackbar("US_1", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV_1", "Tracking", 255, 255, nothing)

cv.createTrackbar("LH_2", "Tracking", 0, 255, nothing) # object 2
cv.createTrackbar("LS_2", "Tracking", 0, 255, nothing)
cv.createTrackbar("LV_2", "Tracking", 0, 255, nothing)
cv.createTrackbar("UH_2", "Tracking", 255, 255, nothing)
cv.createTrackbar("US_2", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV_2", "Tracking", 255, 255, nothing)

# Establishes loop through every frame until webcam is closed
while cap.isOpened():
    
    _, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # create trackbars
    l_h_one = cv.getTrackbarPos("LH_1", "Tracking") # object 1
    l_s_one = cv.getTrackbarPos("LS_1", "Tracking")
    l_v_one = cv.getTrackbarPos("LV_1", "Tracking")

    u_h_one = cv.getTrackbarPos("UH_1", "Tracking")
    u_s_one = cv.getTrackbarPos("US_1", "Tracking")
    u_v_one = cv.getTrackbarPos("UV_1", "Tracking")
    
    l_h_two = cv.getTrackbarPos("LH_2", "Tracking") # object 2
    l_s_two = cv.getTrackbarPos("LS_2", "Tracking")
    l_v_two = cv.getTrackbarPos("LV_2", "Tracking")

    u_h_two = cv.getTrackbarPos("UH_2", "Tracking")
    u_s_two = cv.getTrackbarPos("US_2", "Tracking")
    u_v_two = cv.getTrackbarPos("UV_2", "Tracking")

    # Implement upper and lower bound HSV for masks based on trackbar input
    l_b_one = np.array([l_h_one, l_s_one, l_v_one]) # object 1
    u_b_one = np.array([u_h_one, u_s_one, u_v_one]) 
    
    l_b_two = np.array([l_h_two, l_s_two, l_v_two]) # object 2
    u_b_two = np.array([u_h_two, u_s_two, u_v_two])
    
    # create masks and resulting image
    mask_one = cv.inRange(hsv, l_b_one, u_b_one)
    mask_two = cv.inRange(hsv, l_b_two, u_b_two)
    mask = mask_one + mask_two
    # res1 = cv.bitwise_and(frame, frame, mask=mask_one)
    # res2 = cv.bitwise_and(frame, frame, mask=mask_two)
    res = cv.bitwise_and(frame, frame, mask=mask)

    # find contours in the object 1 mask
    contours, hierarchy = cv.findContours(mask_one,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv.contourArea(c)
        
        if cv.contourArea(c) > 7000:
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
                
            print("Object 1 Pos: ", cX, ",", cY)
            
            
            cv.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
            cv.putText(frame, "object 1", (cX - 25, cY - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # find contours in the object 2 mask
    contours, hierarchy = cv.findContours(mask_two,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv.contourArea(c)
        
        if cv.contourArea(c) > 7000:
            #cv.drawContours(frame,c,-1, (0,255,255),3)
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            #print(area)
            # calculate moments for each contour
            M = cv.moments(c)
             
            # calculate x,y coordinate of center
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
                
            print("Object 2 Pos: ", cX, ",", cY)
            
            
            cv.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
            cv.putText(frame, "object 2", (cX - 25, cY - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # Create 4 windows (1) original, (2) mask 1, (3) mask 2, (4) result
    cv.imshow("frame", frame)
    cv.imshow("mask 1", mask_one)
    cv.imshow("mask 2", mask_two)
    cv.imshow("res", res)

    # Close webcam feed if q is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()
