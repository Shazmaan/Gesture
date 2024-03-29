import cv2
import math
import numpy as np
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Listener
import wx
mouse=Controller()

sqrt = 0

app=wx.App(False)
(sx,sy)=wx.GetDisplaySize()
(camx,camy)=(640,480)

lowerBound=np.array([80,80,100])
upperBound=np.array([102,255,255])

cam= cv2.VideoCapture(0)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

mlocOld= np.array([0,0])
mouseLoc= np.array([0,0])
DampingFac=4
#mouseloc= mlocOld+(targetLoc-mlocOld)/DampingFac

pinchFlag=0

openx,openy,openw,openh= (0,0,0,0)

check = False
Text = "Press 'A' once to calibrate"
color = (255, 255, 255)

def pressed(key):
    print key

while True:
    # with Listener(on_press=pressed) as listener:
    #     listener.join()
    # k= cv2.waitKey(10)
    # if (k==97):
    #     print "Hallaluejah"
    ret, img=cam.read()
    img=cv2.resize(img,(640,480))

    #convert BGR to HSV
    imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # create the Mask
    mask=cv2.inRange(imgHSV,lowerBound,upperBound)
    #morphology
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    maskFinal=maskClose
    conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    if(len(conts)==2):
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)
        x1,y1,w1,h1=cv2.boundingRect(conts[0])
        x2,y2,w2,h2=cv2.boundingRect(conts[1])

        # font = cv2.FONT_HERSHEY_SIMPLEX
        # bottomLeftCornerOfText = (10, 500)
        # fontScale = 1
        # fontColor = (255, 255, 255)
        # lineType = 2

        # cv2.putText(img, 'Press A to calibrate.' , bottomLeftCornerOfText , font , fontScale , fontColor , lineType)

        # Display the image
        # cv2.imshow("img", img)

        cx1=x1+w1/2
        cy1=y1+h1/2
        cx2=x2+w2/2
        cy2=y2+h2/2

        Dx2 = (cx2 - cx1) ** 2
        Dy2 = (cy2 - cy1) ** 2
        sqrt2 = math.sqrt(Dx2 + Dy2)

        # cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
        # cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)
        #
        # cx = (cx1 + cx2) / 2
        # cy = (cy1 + cy2) / 2
        # cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
        # cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)

        if(check):
            Text = "Calibrated"
            color = (10,255,255)
            if(sqrt2<=(sqrt+100)):
                cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
                cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)

                cx = (cx1 + cx2) / 2
                cy = (cy1 + cy2) / 2
                cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
                cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)

                mouseLoc = mlocOld + ((cx,cy) - mlocOld) / DampingFac
                mouseLoc2 = (sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy)
                mouse.position=mouseLoc2
                while mouse.position!=mouseLoc2:
                    pass
                mlocOld=mouseLoc
                openx,openy,openw,openh = cv2.boundingRect(np.array([[[x1,y1],[x1+w1,y1+h1],[x2,y2],[x2+w2,y2+h2]]]))
        else:
            cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
            cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)

            cx = (cx1 + cx2) / 2
            cy = (cy1 + cy2) / 2
            cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
            cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)
        # cv2.rectangle(img,(openx,openy),(openx+openw,openy+openh),(255,0,0),2)
    elif((len(conts)==1) and check):
        Text = "Calibrated"
        color = (10, 255, 255)
        x,y,w,h=cv2.boundingRect(conts[0])
        if(pinchFlag==0):
            if((abs((w*h-openw*openh)*100)/(w*h))<30):
                # print ((abs((w*h-openw*openh)*100)/(w*h)))
                pinchFlag = 1
                mouse.press(Button.left)
                openx, openy, openw, openh = (0, 0, 0, 0)
        else:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            cx=x+w/2
            cy=y+h/2
            cv2.circle(img,(cx,cy),(w+h)/4,(0,0,255),2)
            mouseLoc = mlocOld + ((cx, cy) - mlocOld) / DampingFac
            mouseLoc2 = (sx - (mouseLoc[0] * sx / camx), mouseLoc[1] * sy / camy)
            mouse.position = mouseLoc2
            while mouse.position != mouseLoc2:
                pass
            mlocOld = mouseLoc
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, Text,(5, 50), font, 0.7, color, 2, cv2.LINE_AA)
    cv2.imshow("cam",img)
    key = cv2.waitKey(10)
    if key == 97:
        Dx=(cx2-cx1)**2
        Dy=(cy2-cy1)**2
        sqrt=math.sqrt(Dx+Dy)
        check = True