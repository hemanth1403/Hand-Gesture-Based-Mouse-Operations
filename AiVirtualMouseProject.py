import cv2
import numpy as np
import autopy                     #For mouse controls
import HandTrackingModule as htm
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import mouse as m
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

wCam, hCam = 640, 480
frameR = 100
smoothening = 7

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
cTime = 0
detector = htm.HandDetector(maxHands=1, detectionCon=0.6)
wScr, hScr = autopy.screen.size()
#hScr -= 25
#print(wScr, hScr)

while True:

    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList)!= 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        #print(x1, y1, x2, y2)

        fingers = detector.fingersUp()
       # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:

            x3 = np.interp(x1, (frameR, wCam-frameR), (0,wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            clocX = ( plocX + (x3 - plocX) / smoothening )
            clocY = ( plocY + (y3 - plocY) / smoothening )
            try:
                autopy.mouse.move(wScr-clocX, clocY)
                print(wScr-clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY
            except : pass

        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            #print(length)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                # autopy.mouse.click()
                #print("Click")
        # if (any(fingers[:2]) and any(fingers[2:])==False):
        #    print("Volume")
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            indxpos, indypos = lmList[20][1], lmList[20][2]
            thumbxpos, thumbypos = lmList[4][1], lmList[4][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            length = math.hypot((x2 - x1) + 30, (y2 - y1) + 30)
            vol = np.interp(length, [50, 250], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)
            #volBar = np.interp(length, [50, 250], [400, 150])
            #volPer = np.interp(length, [50, 250], [0, 100])

            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            #print("VOLUME")"""

    try:
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    except:
        pass
    cv2.imshow("Image", img)
    cv2.waitKey(1)
