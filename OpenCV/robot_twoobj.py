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
    start_coord = [x, y, 15] # x,y,z
    end_coord = [100, 40, 40] # x,y,z
    
    
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

# Configures window with 'sliders' to tune HSV bounds for masks of object 1 and object 2
cv.namedWindow("Tracking",cv.WINDOW_NORMAL)

cv.createTrackbar("LH_1", "Tracking", 64, 255, nothing) # object 1
cv.createTrackbar("LS_1", "Tracking", 114, 255, nothing)
cv.createTrackbar("LV_1", "Tracking", 53, 255, nothing)
cv.createTrackbar("UH_1", "Tracking", 102, 255, nothing)
cv.createTrackbar("US_1", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV_1", "Tracking", 255, 255, nothing)

cv.createTrackbar("LH_2", "Tracking", 160, 255, nothing) # object 2
cv.createTrackbar("LS_2", "Tracking", 89, 255, nothing)
cv.createTrackbar("LV_2", "Tracking", 119, 255, nothing)
cv.createTrackbar("UH_2", "Tracking", 255, 255, nothing)
cv.createTrackbar("US_2", "Tracking", 255, 255, nothing)
cv.createTrackbar("UV_2", "Tracking", 255, 255, nothing)

# set up robot
reset_mcu()
sleep(0.01)
arm = PiArm([1,2,3])
arm.set_offset([0,0,0])
arm.hanging_clip_init(PWM('P3'))

# Initializes arguments for threads to avoid error
x1_cmd = 50
y1_cmd = 50
x2_cmd = 50
y2_cmd = 50

# Establishes loop through every frame until webcam is closed
while cap.isOpened():
    
    _, frame = cap.read() # set up frame
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV) # convert from RBG t HSV color space

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
    res = cv.bitwise_and(frame, frame, mask=mask)

    # find contours in the object 1 mask
    contours, hierarchy = cv.findContours(mask_one,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
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
                cX1 = int(Mo["m10"] / Mo["m00"])
                cY1 = int(Mo["m01"] / Mo["m00"])
            else:
                cX1, cY1 = 0, 0
            
            # Put a cicle and text on the center of the detected object
            cv.circle(frame, (cX1, cY1), 5, (255, 255, 255), -1)
            cv.putText(frame, "obj 1", (cX1 - 25, cY1 - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Convert pixel location to millimeter location
            x1_mm = 238 - pixel_to_mm(cX1) # x coord is subtracted from 238 since robot arm is not at (0,0) of video feed
            y1_mm = pixel_to_mm(cY1)
            x1_cmd = x1_mm
            y1_cmd = y1_mm
            
            # Limits x and y command values if exceeding arm mechanical limits
            if (x1_cmd > 80): x1_cmd = 80
            if (x1_cmd < -80): x1_cmd = -80
            if (y1_cmd > 100): y1_cmd = 100
            
            # Print pixel location, millimeter location, and corrected command
            print("pixel #1: ", cX1, ",", cY1)
            print("millimeter #1: ", x1_mm, "," ,y1_mm)
            print("command #1: ", x1_cmd, "," ,y1_cmd)
            #print("\n")
  
    # find contours in the object 2 mask
    contours, hierarchy = cv.findContours(mask_two,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv.contourArea(c)
        
        if cv.contourArea(c) > 1500:

            # draw bounding rectangle box on video feed
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    
            # calculate moments for each contour
            Mo = cv.moments(c)
             
            # calculate x,y coordinate of center
            if Mo["m00"] != 0:
                cX2 = int(Mo["m10"] / Mo["m00"])
                cY2 = int(Mo["m01"] / Mo["m00"])
            else:
                cX2, cY2 = 0, 0
            
            # Put a cicle and text on the center of the detected object
            cv.circle(frame, (cX2, cY2), 5, (255, 255, 255), -1)
            cv.putText(frame, "obj 2", (cX2 - 25, cY2 - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Convert pixel location to millimeter location
            x2_mm = 238 - pixel_to_mm(cX2) # x coord is subtracted from 238 since robot arm is not at (0,0) of video feed
            y2_mm = pixel_to_mm(cY2)
            x2_cmd = x2_mm
            y2_cmd = y2_mm
            
            # Limits x and y command values if exceeding arm mechanical limits
            if (x2_cmd > 80): x2_cmd = 80
            if (x2_cmd < -80): x2_cmd = -80
            if (y2_cmd > 100): y2_cmd = 100
            
            # Print pixel location, millimeter location, and corrected command
            print("pixel #2: ", cX2, ",", cY2)
            print("millimeter #2: ", x2_mm, "," ,y2_mm)
            print("command #2: ", x2_cmd, "," ,y2_cmd)
            print("\n")

    # Create 4 windows (1) original, (2) mask 1, (3) mask 2, (4) result
    cv.imshow("frame", frame)
    cv.imshow("mask 1", mask_one)
    cv.imshow("mask 2", mask_two)
    #cv.imshow("res", res)

    t1 = Thread(target = robot_move, args=(x1_cmd,y1_cmd),) # Create thread for robot movement to allow continuation of video stream
    t2 = Thread(target = robot_move, args=(x2_cmd,y2_cmd),) # Create thread for robot movement to allow continuation of video stream
    
    # command robot to move to object 1 if a is pressed
    if cv.waitKey(5) & 0xFF == ord('a'):
        #t1 = Thread(target = robot_move, args=(x1_cmd,y1_cmd),) # Create thread for robot movement to allow continuation of video stream
        t1.start() # start thread
        
    # command robot to move to object 2 if b is pressed
    if cv.waitKey(5) & 0xFF == ord('d'):
        #t2 = Thread(target = robot_move, args=(x2_cmd,y2_cmd),) # Create thread for robot movement to allow continuation of video stream
        t2.start() # start thread
    
    # Close webcam feed if q is pressed
    if cv.waitKey(5) & 0xFF == ord('q'):
        print("quit")
        break

# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()