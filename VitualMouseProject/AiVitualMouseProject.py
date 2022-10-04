import math

import cv2
import numpy as np
import HandTrackingMoudule as htm
import time
import autopy

#################################
wCam, hCam = 1280, 720
frameR = 100  # Frame Redction
smoothening = 5
#################################


pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
print(wScr, hScr)

while True:
    # 1. Find hand Landmarks
    _, img = cap.read()
    # img = cv2.flip(img, 1)  # 选择镜像
    img = detector.findHands(img, draw=False)
    lmList = detector.findPostion(img, draw=False)

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print((x1,y1,x2,y2))

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:  # 5. Convert Coordinates

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. FInd distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img, draw=False)
            print(length)
            # 10. Click mouser if distance short
            if length < 60:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 255), cv2.FILLED)
                autopy.mouse.click()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 40), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 255, 0), 3)
    # 12. Dispaly
    cv2.imshow("Mouse", img)
    cv2.waitKey(1)