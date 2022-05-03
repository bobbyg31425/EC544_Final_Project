#Importing libraries
from re import M
from robot_hat import PWM
from robot_hat.utils import reset_mcu
from time import sleep
from piarm import PiArm
import numpy as np
import cv2 as cv
#import keyboard
from threading import Thread

# trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass

# Convert location of object from pixels to millimeters 
def pixel_to_mm(pixel):
    mm = pixel / 1.5
    return int(mm)

# Move arm from start location, pick up object, mvoe to end location,
# drop object, then finally return to home position [0,80,80]
# x range: -80 to 80 mm
# y range: 30 to 130 mm
# z range: 0 to 80 mm
# hanging clip: 20 = open, 90 = closed
def robot_move(x,y):
    
    # Define start and end coordinates
    start_coord = [x, y, 30] # x,y,z
    end_coord = [100, 40, 30] # x,y,z
    
    
    arm.set_speed(60)
    arm.set_hanging_clip(20)
    start_coord_up = [start_coord[0], start_coord[1], 80]
    arm.do_by_coord(start_coord_up)
    arm.do_by_coord(start_coord)
    arm.set_hanging_clip(90)
    arm.do_by_coord(start_coord_up)
    
    end_coord_up = [end_coord[0], end_coord[1], 80]
    arm.do_by_coord(end_coord_up)
    
    arm.do_by_coord(end_coord)
    arm.set_hanging_clip(20)
    arm.do_by_coord(end_coord_up)
    
    arm.do_by_coord([0,80,80])
    arm.set_hanging_clip(90)

# Connect to capture device 640x480
cap = cv.VideoCapture(0);

# Configures window with 'sliders' to tune HSV bounds for mask
# Default values for trackbars based on GREEN object
cv.namedWindow("Tracking")
cv.createTrackbar("LH", "Tracking", 64, 255, nothing)
cv.createTrackbar("LS", "Tracking", 125, 255, nothing)
cv.createTrackbar("LV", "Tracking", 53, 255, nothing)
cv.createTrackbar("UH", "Tracking", 102, 255, nothing)
cv.createTrackbar("US", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV", "Tracking", 255, 255, nothing)

# set up robot
reset_mcu()
sleep(0.01)
arm = PiArm([1,2,3])
arm.set_offset([0,0,0])
arm.hanging_clip_init(PWM('P3'))

# Initializes arguments for threads to avoid error
x_cmd = 50
y_cmd = 50

# Establishes loop through every frame until webcam is closed
while cap.isOpened():
    
    _, frame = cap.read() # set up frame
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV) # convert from RBG t HSV color space

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

    mask = cv.inRange(hsv, l_b, u_b) # create mask based on bounds
    res = cv.bitwise_and(frame, frame, mask=mask) # create result imaging by combining mask and original image

    # find contours in the binary image
    contours, hierarchy = cv.findContours(mask,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv.contourArea(c)
        
        if cv.contourArea(c) > 1500:

            # draw bounding rectangle box on video feed
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    
            # calculate moments for each contour
            Mo = cv.moments(c)
             
            # calculate x,y coordinate of center
            if Mo["m00"] != 0:
                cX = int(Mo["m10"] / Mo["m00"])
                cY = int(Mo["m01"] / Mo["m00"])
            else:
                cX, cY = 0, 0
            
            # Put a cicle and text on the center of the detected object
            cv.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
            cv.putText(frame, "centroid", (cX - 25, cY - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Convert pixel location to millimeter location
            x_mm = 238 - pixel_to_mm(cX) # x coord is subtracted from 238 since robot arm is not at (0,0) of video feed
            y_mm = pixel_to_mm(cY)
            x_cmd = x_mm
            y_cmd = y_mm
            
            # Limits x and y command values if exceeding arm mechanical limits
            if (x_cmd > 80): x_cmd = 80
            if (x_cmd < -80): x_cmd = -80
            if (y_cmd > 100): y_cmd = 100
            
            # Print pixel location, millimeter location, and corrected command
            print("pixel: ", cX, ",", cY)
            print("millimeter: ", x_mm, "," ,y_mm)
            print("command: ", x_cmd, "," ,y_cmd)
            print("\n")
            

    # Create 3 windows (1) original, (2) mask, (3) result
    cv.imshow("frame", frame)
    cv.imshow("mask", mask)
    #cv.imshow("res", res)

    # Create thread for robot movement to allow continuation of video stream
    t1 = Thread(target = robot_move, args=(x_cmd,y_cmd),)

    # command robot to move if d is pressed
    if cv.waitKey(5) & 0xFF == ord('d'):
        t1.start() # start thread
    
    # Close webcam feed if q is pressed
    if cv.waitKey(5) & 0xFF == ord('q'):
        print("quit")
        break

# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()