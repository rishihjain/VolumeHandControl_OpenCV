import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Camera dimensions
wCam, hCam = 640, 480

# Set up the camera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Initialize variables
pTime = 0
detector = htm.handDetector(detectionCon=0.6)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
print(volume.GetVolumeRange())
volume.SetMasterVolumeLevel(0, None)

# Get volume range
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    # Read a frame from the camera
    success, img = cap.read()

    # Find hands in the frame
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    # if len(lmList) != 0:
    # Check if lmList has enough elements before accessing indices
    if lmList:
        # print(lmList)
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        # Calculate hand length
        length = math.hypot(x2 - x1, y2 - y1)
        print(length)

        # Interpolate hand length to volume
        # Hand Range 50 to 300
        # Volume Range -63.5 to 0
        vol = np.interp(length, [50, 280], [minVol, maxVol])
        print(vol)
        volBar = np.interp(length, [50, 280], [400, 150])
        volPer = np.interp(length, [50, 280], [0, 100])

        # Set system volume
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    else:
        print("Not enough landmarks detected.")

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Show the image
    cv2.imshow("Img", img)

    # Wait for a key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
