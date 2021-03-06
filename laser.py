import cv2
import numpy as np
import subprocess

subprocess.check_call("v4l2-ctl -d /dev/video0 -c auto_exposure=1",shell=True)

subprocess.check_call("v4l2-ctl -d /dev/video0 -c exposure_time_absolute=355",shell=True)

def nothing(x):
    pass

cap = cv2.VideoCapture(0)

# Create a black image, a window
img = np.zeros((240,320,3), np.uint8)
res = np.zeros((240,320,3), np.uint8)
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('Hmin','image',0,255,nothing)
cv2.createTrackbar('Hmax','image',255,255,nothing)
cv2.createTrackbar('Smin','image',0,255,nothing)
cv2.createTrackbar('Smax','image',255,255,nothing)
cv2.createTrackbar('Vmin','image',30,255,nothing)
cv2.createTrackbar('Vmax','image',255,255,nothing)

# create switch for ON/OFF functionality
switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'image',0,1,nothing)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
cap.set(cv2.CAP_PROP_FPS,60)

while(1):

    # get current positions of four trackbars
    hmin = cv2.getTrackbarPos('Hmin','image')
    hmax = cv2.getTrackbarPos('Hmax','image')
    smin = cv2.getTrackbarPos('Smin','image')
    smax = cv2.getTrackbarPos('Smax','image')
    vmin = cv2.getTrackbarPos('Vmin','image')
    vmax = cv2.getTrackbarPos('Vmax','image')
    s = cv2.getTrackbarPos(switch,'image')
    
    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # define range of blue color in HSV
    lower_blue = np.array([hmin, smin, vmin])
    upper_blue = np.array([hmax, smax, vmax])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # morph
    if s == 1:
        kernel = np.ones((5,5),np.uint8)
        dilation = cv2.dilate(mask,kernel,iterations = 2)
        kernel = np.ones((15,15),np.uint8)
        opening = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    # Bitwise-AND mask and original image
    #res = cv2.bitwise_and(frame,frame, mask= mask)


    #Contour -----------------
    _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        cnt = max(contours, key = cv2.contourArea)
        #cnt = contours[0]
        M = cv2.moments(cnt)
        if M['m00'] ==0:
            M['m00']=0.001
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        z= 28.99 - 0.1222*cx + 0.00199* (cx**2)
        
        x,y,w,h = cv2.boundingRect(cnt)
        
        h11 = 245.75 - 6.09*z  + 0.05* z**2
        objH = h / h11 * 11
        
        print(cx,z, h , objH)
        res = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        

    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    cv2.imshow('image',frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()


'''
calib measurements:
height(cm)  pixel(x direction)

30    69
35    93
40    112
45    125
50    138

height = 28.99 - 0.1222*x + 0.00199* x**2

-------
h,z calib for 11cm obj:

108 30
94 35
82 40
73 45

h = 245.75 - 6.09*z  + 0.05* z**2
'''
