#Importing libraries
from re import M
from robot_hat import PWM
from robot_hat.utils import reset_mcu
from time import sleep
from piarm import PiArm
import numpy as np
import cv2 as cv
import keyboard
from threading import Thread

#trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass

def pixel_to_mm(pixel):
    mm = pixel / 1.5
    return int(mm)

def robot_move(x1,y1):
    print("d")
    #x1 = 238 - pixel_to_mm(cX)
    #y1 = pixel_to_mm(cY)
    height = 30
    #print("x: ", x1, "y: ", y1)
    if (x1 > 80): x1 = 80
    if (x1 < -80): x1 = -80
    if (y1 > 100): y1 = 100
    
    start_coord = [x1, y1, height] # x,y,z
    end_coord = [100, 40, height] # x,y,z
    
    
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
cv.namedWindow("Tracking")
cv.createTrackbar("LH", "Tracking", 64, 255, nothing)
cv.createTrackbar("LS", "Tracking", 51, 255, nothing)
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

x_pos = 50
y_pos = 50

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
        
        if cv.contourArea(c) > 1500:
            #cv.drawContours(frame,c,-1, (0,255,255),3)
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            #print(area)
            # calculate moments for each contour
            Mo = cv.moments(c)
             
            # calculate x,y coordinate of center
            if Mo["m00"] != 0:
                cX = int(Mo["m10"] / Mo["m00"])
                cY = int(Mo["m01"] / Mo["m00"])
            else:
                cX, cY = 0, 0
            
            x_pos = 238 - pixel_to_mm(cX)
            y_pos = pixel_to_mm(cY)
            print("pixel: ", cX, ",", cY)
            print("command: ", x_pos,",",y_pos)
            print("\n")
            
            cv.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
            cv.putText(frame, "centroid", (cX - 25, cY - 25),cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # Create 3 windows (1) original, (2) mask, (3) result
    cv.imshow("frame", frame)
    cv.imshow("mask", mask)
    #cv.imshow("res", res)

    t1 = Thread(target = robot_move, args=(x_pos,y_pos),)

    # command robot to move if d is pressed
    if cv.waitKey(10) & 0xFF == ord('d'):
        print("d")
        t1.start()
        '''
        print("d")
        #x1 = 238 - pixel_to_mm(cX)
        #y1 = pixel_to_mm(cY)
        height = 30
        #print("x: ", x1, "y: ", y1)
        if (x1 > 80): x1 = 80
        if (x1 < -80): x1 = -80
        if (y1 > 100): y1 = 100
        
        start_coord = [x1, y1, height] # x,y,z
        end_coord = [-x1, y1, height] # x,y,z
        
        
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
        '''
    
    # Close webcam feed if q is pressed
    if cv.waitKey(10) & 0xFF == ord('q'):
        print("quit")
        break

# Releases webcam and closes frame
cap.release()
cv.destroyAllWindows()





