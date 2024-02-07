import cv2

# MediaPipe is a Framework developed by Google for building machine learning pipelines for processing time-series data like video, audio, etc
import mediapipe as mp 
import time # To check the frame rate

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

capture = cv2.VideoCapture(0)

while True:
    ret,frame = capture.read()

    frameRGB = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = hands.process(frameRGB)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id,lm in enumerate(handLms.landmark):
                # print(id,lm)
                h,w,c = frame.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                print(id,cx,cy)
                if id == 4:         #for tip of thumb id = 4
                    cv2.circle(frame,(cx,cy),15,(255,0,255),cv2.FILLED)
            mpDraw.draw_landmarks(frame,handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(frame,str(int(fps)),(10,70),cv2.FONT_HERSHEY_COMPLEX,3,(255,0,255),2)


    if cv2.waitKey(20) & 0xFF==ord('q'):
        break


    cv2.imshow("Image",frame)

    cv2.waitKey(1)

