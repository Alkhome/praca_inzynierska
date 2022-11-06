import mediapipe as mp
import cv2
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

mp_drawing = mp.solutions.drawing_utils #wizualizacja wykrywania
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose #import pose estimation model  (konkretnego)

#checking video feed

cap = cv2.VideoCapture(0)

start_time = time()
prev_frame_time = 0
new_frame_time = 0
fps = 0

arr = []
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Empty Frame Detected")
            continue

        #Recoloring from BGR to RGB
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #make detection
        results = pose.process(frame)

        #Reverse previous so that opencv can read this (RGB to BGR)
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        new_frame_time = time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        arr.append([new_frame_time-start_time, fps])

        frame = cv2.flip(frame, 1)
        cv2.putText(frame, str(fps), (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Output", frame)
        if new_frame_time > start_time+5:
            break
        if cv2.waitKey(1) == ord('q'): # closes if q is pressed
            break


# releases cap object
cap.release()
# Closes all the frames
cv2.destroyAllWindows()

print(arr)
np_arr = np.array(arr)
plt.plot(np_arr[2:, 0], np_arr[2:, 1])
plt.show()



