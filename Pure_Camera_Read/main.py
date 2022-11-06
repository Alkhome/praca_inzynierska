from imutils.video import VideoStream
import imutils  # used to resize
import cv2
from time import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

single_thread = []
multi_thread = []
fig = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for i in range(10):
    fig[i], ax1 = plt.subplots()

    start_time = time()
    prev_frame_time = 0
    new_frame_time = 0
    arr = []
    # created a *threaded *video stream, allow the camera senor to warmup,

    vs = VideoStream(src=0).start()
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, 800)
        cv2.imshow("Frame", cv2.flip(frame, 1))

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

    ax1.plot(np_arr[:, 0], np_arr[:, 1], color="blue", alpha=0.8, label="Multi-threaded")
    ax1.set_title(f"Wykres {i+1}")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("FPS")
    ax1.legend()

    multi_thread.append([f"mode: {m_mode}", f"mean: {m_mean}", f"stddev: {m_stddev}"])

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

        new_frame_time = time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        arr.append([new_frame_time-start_time, fps])

        frame = imutils.resize(frame, 800)
        cv2.imshow("Output", cv2.flip(frame, 1))
        if new_frame_time > start_time+5:
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
    ax2.plot(np_arr[:, 0], np_arr[:, 1], color="red", alpha=0.5, label="Single-threaded")
    ax2.legend()

    single_thread.append([f"mode: {s_mode}", f"mean: {s_mean}", f"stddev: {s_stddev}"])

for i in range(len(single_thread)):
    print(f"Multi thread {i+1}: {multi_thread[i]}")
    print(f"Single thread {i+1}: {single_thread[i]}")
    print()
plt.show()
