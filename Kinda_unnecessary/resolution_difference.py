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

multi_thread_2= []
multi_thread_1 = []
fig = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    for i in range(3):
        fig[i], ax1 = plt.subplots()

        start_time = time()
        prev_frame_time = 0
        new_frame_time = 0
        arr = []
        # created a *threaded *video stream, allow the camera senor to warmup,

        vs = VideoStream(src=0).start()
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, 400)
            cv2.imshow("Frame", cv2.flip(frame, 1))

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

            # check to see if the frame should be displayed to our screen
            if cv2.waitKey(1) == ord('q'):  # closes if q is pressed
                break
            if new_frame_time > start_time+5:
                break

        cv2.destroyAllWindows()
        vs.stop()
        np_arr = np.array(arr)

        m_mode = stats.mode(np_arr[:, 1])
        m_mean = np.mean(np_arr[:, 1])
        m_stddev = np.std(np_arr[:, 1])

        ax1.plot(np_arr[:, 0], np_arr[:, 1], color="blue", alpha=0.8, label="Lower-resolution")
        ax1.set_title(f"Wykres {i+1}")
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("FPS")
        ax1.legend()

        multi_thread_1.append([f"mode: {m_mode}", f"mean: {m_mean}", f"stddev: {m_stddev}"])

# END OF 1st READ
        cap = cv2.VideoCapture(0)

        start_time = time()
        prev_frame_time = 0
        new_frame_time = 0
        fps = 0
        arr = []

        vs = VideoStream(src=0).start()
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, 1200)
            cv2.imshow("Frame", cv2.flip(frame, 1))

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
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            arr.append([new_frame_time - start_time, fps])

            # check to see if the frame should be displayed to our screen
            if cv2.waitKey(1) == ord('q'):  # closes if q is pressed
                break
            if new_frame_time > start_time + 5:
                break

        cv2.destroyAllWindows()
        vs.stop()
        np_arr = np.array(arr)

        s_mode = stats.mode(np_arr[:, 1])
        s_mean = np.mean(np_arr[:, 1])
        s_stddev = np.std(np_arr[:, 1])

        ax2 = ax1
        ax2.plot(np_arr[:, 0], np_arr[:, 1], color="red", alpha=0.5, label="High_resolution")
        ax2.legend()

        multi_thread_2.append([f"mode: {s_mode}", f"mean: {s_mean}", f"stddev: {s_stddev}"])

    for i in range(len(multi_thread_2)):
        print(f"Lower_resolution thread {i+1}: {multi_thread_1[i]}")
        print(f"High_resolution thread {i+1}: {multi_thread_2[i]}")
        print()
    plt.show()
