from imutils.video import VideoStream
import imutils  # used to resize
import cv2
from time import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils #wizualizacja wykrywania
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose #import pose estimation model  (konkretnego)

single_thread = []
multi_thread = []
fig = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    for i in range(1):
        fig[i], ax1 = plt.subplots()

        start_time = time()
        prev_frame_time = 0
        new_frame_time = 0
        arr = []


        cap = cv2.VideoCapture(0)

        start_time = time()
        prev_frame_time = 0
        new_frame_time = 0
        fps = 0
        arr = []

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Empty Frame Detected")
                continue

            # Recoloring from BGR to RGB
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # make detection
            results = pose.process(frame)

            # Reverse previous so that opencv can read this (RGB to BGR)
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

            frame = imutils.resize(frame, 600)
            cv2.imshow("Output", cv2.flip(frame, 1))
            if new_frame_time > start_time+60:
                break
            if cv2.waitKey(1) == ord('q'):  # closes if q is pressed
                break

        # releases cap object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
        np_arr = np.array(arr)

        s_mode = stats.mode(np_arr[:, 1])
        s_mean = np.mean(np_arr[:, 1])
        s_stddev = np.std(np_arr[:, 1])

        ax2 = ax1
        ax2.plot(np_arr[30:, 0], np_arr[30:, 1], color="red", alpha=0.5, label="Lenovo - i7 vPro")
        ax2.legend()

        single_thread.append([f"mode: {s_mode}", f"mean: {s_mean}", f"stddev: {s_stddev}"])

    for i in range(len(single_thread)):
        print(f"Lenovo i7 vPro: {single_thread[i]}")
        print()
    plt.show()
