import sys
import time
import keyboard
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

import PIL.Image
import PIL.ImageTk
import cv2
import imutils  # used to resize
import mediapipe as mp
import numpy as np
import os
import file_mod as fm
from imutils.video import VideoStream

EXERCISES = [
    "left_arm_bend",
    "right_arm_bend",
    "left_arm_raise",
    "right_arm_raise",
    "left_arm_level",
    "right_arm_level",
    "prayer_position",
    "lean",
    "done"
]

nose = None
left_eye_inner = None
left_eye = None
left_eye_outer = None

right_eye_inner = None
right_eye = None
right_eye_outer = None

left_ear = None
right_ear = None

left_mouth = None
right_mouth = None

left_shoulder = None
right_shoulder = None

left_elbow = None
right_elbow = None

left_wrist = None
right_wrist = None

left_pinky = None
right_pinky = None
left_index = None
right_index = None
left_thumb = None
right_thumb = None

left_hip = None
right_hip = None


def calculate_angle(a=None, b=None, c=None):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


class ExerciseApp:

    def __init__(self, root, vid_src=0):
        # setting title
        root.title("program z kamerka")
        # setting window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (screenwidth, screenheight, 0, 0)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.feed = VidCapt(screenwidth, screenheight)
        self.exercise_count = self.feed.current_exercise_count
        self.camera_label = tk.Label(root)
        self.camera_label["bg"] = "#d65ac3"
        self.camera_label.place(x=screenwidth * 0.01, y=screenheight * 0.01, width=screenwidth * 0.49,
                                height=screenheight * 0.48)

        self.img_canvas = tk.Canvas(root)
        self.img_canvas["bg"] = "#000000"
        self.img_canvas.place(x=screenwidth * 0.501, y=screenheight * 0.01, width=screenwidth * 0.49,
                              height=screenheight * 0.48)

        self.instruction_label = tk.Label(root)
        self.instruction_label["bg"] = "#b5b5b5"
        self.instruction_label["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        self.instruction_label["font"] = ft
        self.instruction_label["fg"] = "#333333"
        self.instruction_label["justify"] = "center"
        self.instruction_label["text"] = "Instrukcje"
        self.instruction_label["relief"] = "groove"
        self.instruction_label.place(x=screenwidth * 0.01, y=screenheight * 0.5, width=screenwidth * 0.98,
                                     height=screenheight * 0.35)

        return_button = tk.Button(root)
        return_button["activebackground"] = "#955d5d"
        return_button["activeforeground"] = "#393d49"
        return_button["bg"] = "#ff7800"
        return_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        return_button["font"] = ft
        return_button["fg"] = "#000000"
        return_button["justify"] = "center"
        return_button["text"] = "Powrot do menu"
        return_button["relief"] = "groove"
        return_button.place(x=screenwidth * 0.01, y=screenheight * 0.87, width=screenwidth * 0.32,
                            height=screenheight * 0.05)
        return_button["command"] = self.return_button_command

        stop_button = tk.Button(root)
        stop_button["activebackground"] = "#b46161"
        stop_button["activeforeground"] = "#4a3333"
        stop_button["bg"] = "#ffd700"
        stop_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        stop_button["font"] = ft
        stop_button["fg"] = "#000000"
        stop_button["justify"] = "center"
        stop_button["text"] = "Zatrzymaj trening"
        stop_button["relief"] = "groove"
        stop_button.place(x=screenwidth * 0.34, y=screenheight * 0.87, width=screenwidth * 0.32,
                          height=screenheight * 0.05)
        stop_button["command"] = self.stop_button_command

        skip_button = tk.Button(root)
        skip_button["activebackground"] = "#b46161"
        skip_button["activeforeground"] = "#4a3333"
        skip_button["bg"] = "#ffd700"
        skip_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        skip_button["font"] = ft
        skip_button["fg"] = "#000000"
        skip_button["justify"] = "center"
        skip_button["text"] = "Pomin cwiczenie"
        skip_button["relief"] = "groove"
        skip_button.place(x=screenwidth * 0.67, y=screenheight * 0.87, width=screenwidth * 0.32,
                          height=screenheight * 0.05)
        skip_button["command"] = self.skip_button_command

        self.pb = ttk.Progressbar(root)
        self.pb["orient"] = tk.HORIZONTAL
        self.pb["mode"] = "determinate"
        self.pb["length"] = screenwidth * 0.32
        self.pb.place(x=screenwidth * 0.34, y=screenheight * 0.92)

        self.pb["value"] = 0

        self.show_frames()

    def show_frames(self):
        imgtk = self.feed.get_frame()
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)
        # tu przyda sie threading
        self.camera_label.after(20, self.show_frames)
        self.exercise_name = self.feed.current_exercise_name
        self.update_instruction()
        self.pb["value"] = self.feed.update_pbar()

    """
    1. zginanie lewej ręki
    2. zginanie prawej ręki
    3. Podnoszenie lewej reki do góry
    4. Podnoszenie prawej ręki do góry
    5. Podnoszenie lewej ręki do poziomu
    6. Podnoszenie prawej ręki do poziomu
    7. Prayer postion (breaststroke)
    8. Skłon tułowia
    """

    def update_instruction(self):
        if self.exercise_name == EXERCISES[0]:
            self.instruction_label["text"] = "Zginanie lewej reki"
        elif self.exercise_name == EXERCISES[1]:
            self.instruction_label["text"] = "Zginanie prawej reki"

        elif self.exercise_name == EXERCISES[2]:
            self.instruction_label["text"] = "Podnoszenie lewej reki do gory"
        elif self.exercise_name == EXERCISES[3]:
            self.instruction_label["text"] = "Podnoszenie prawej reki do gory"

        elif self.exercise_name == EXERCISES[4]:
            self.instruction_label["text"] = "Podnoszenie lewej ręki do poziomu"
        elif self.exercise_name == EXERCISES[5]:
            self.instruction_label["text"] = "Podnoszenie prawej ręki do poziomu"

        elif self.exercise_name == EXERCISES[6]:
            self.instruction_label["text"] = "Prayer position"

        elif self.exercise_name == EXERCISES[7]:
            self.instruction_label["text"] = "skłon tułowia"

        elif self.exercise_name == EXERCISES[8]:
            self.instruction_label["text"] = "Cwiczenia zostaly ukonczone"

        else:
            pass

    def return_button_command(self):
        print("back to menu")
        self.feed.release_feed()
        os.system("python main_menu.py")
        sys.exit()

    def stop_button_command(self):
        # TODO change from exit to freeze
        self.feed.stop_exercises()
        print("stop/resume")

    def skip_button_command(self):
        self.feed.skip_exercise()
        print("Skipped")


class VidCapt:

    def __init__(self, width, height, vid_src=0):
        # self.cap = VideoStream(src=vid_src).start()
        self.vid = cv2.VideoCapture(0)
        _, self.cap = self.vid.read()
        self.width = int(width * 0.48)
        self.height = int(height * 0.48)

        self.mp_drawing = mp.solutions.drawing_utils  # wizualizacja wykrywania
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose  # import pose estimation model  (konkretnego)

        self.current_exercise_count = 0
        self.stage = "down"
        self.current_exercise_name = EXERCISES[0]

        self.left_arm_bend_calibration_results = []
        self.right_arm_bend_calibration_results = []
        self.left_arm_raise_shoulder_calibration_results = []
        self.left_arm_raise_elbow_calibration_results = []
        self.right_arm_raise_shoulder_calibration_results = []
        self.right_arm_raise_elbow_calibration_results = []
        self.left_arm_level_shoulder_calibration_results = []
        self.left_arm_level_elbow_calibration_results = []
        self.right_arm_level_shoulder_calibration_results = []
        self.right_arm_level_elbow_calibration_results = []
        self.prayer_position_shoulder_calibration_results = []
        self.prayer_position_elbow_calibration_results = []
        self.lean_hands_calibration_results = []
        self.lean_body_calibration_results = []

        self.skipped_exercises = [False] * 8

        self.stopped = 0
        self.current_exercise_temp = None
        self.total_execrises_done = 0

        self.is_done = False

    def skip_exercise(self):
        if self.current_exercise_name != EXERCISES[8]:
            self.skipped_exercises[EXERCISES.index(self.current_exercise_name)] = True
            new_index = EXERCISES.index(self.current_exercise_name) + 1
            self.current_exercise_name = EXERCISES[new_index]
            self.current_exercise_count = 0
            self.total_execrises_done += 1

            # TODO dodac ze jak skipped gdzies poszlo ,to wynik jest 255 w zapisie
            print("Skipped")
        else:
            pass

    def stop_exercises(self):
        self.stopped += 1
        if self.stopped % 2 != 0:
            self.current_exercise_temp = EXERCISES.index(self.current_exercise_name)
            self.current_exercise_name = None
            print("Stopped")
        else:
            self.current_exercise_name = EXERCISES[self.current_exercise_temp]
            print("Resumed")

    def release_feed(self):
        self.vid.release()

    def update_pbar(self):
        return int((self.total_execrises_done / 8) * 100)

    def calculate_mean(self, list, reversed=False):
        list.sort(reverse=reversed)
        list = list[-10:-5]
        mean = sum(list) / len(list)
        return int(mean)

    def save_to_file(self):
        # TODO save to file
        val0 = self.calculate_mean(self.left_arm_bend_calibration_results, reversed=True)
        if self.skipped_exercises[0]:
            val0 = 255
        elif val0 < 40:
            val0 = 40

        val1 = self.calculate_mean(self.right_arm_bend_calibration_results, reversed=True)
        if self.skipped_exercises[1]:
            val1 = 255
        elif val1 < 40:
            val1 = 40

        val2 = self.calculate_mean(self.left_arm_raise_shoulder_calibration_results, reversed=True)
        if self.skipped_exercises[2]:
            val2 = 255
        elif val2 < 50:
            val2 = 50

        val3 = self.calculate_mean(self.left_arm_raise_elbow_calibration_results, reversed=False)
        if self.skipped_exercises[2]:
            val3 = 255
        elif val3 > 175:
            val3 = 175

        val4 = self.calculate_mean(self.right_arm_raise_shoulder_calibration_results, reversed=True)
        if self.skipped_exercises[3]:
            val4 = 255
        elif val4 < 50:
            val4 = 50

        val5 = self.calculate_mean(self.right_arm_raise_elbow_calibration_results, reversed=False)
        if self.skipped_exercises[3]:
            val5 = 255
        elif val5 > 175:
            val5 = 175

        val6 = self.calculate_mean(self.left_arm_level_shoulder_calibration_results, reversed=False)
        if self.skipped_exercises[4]:
            val6 = 255
        elif val6 > 90:
            val6 = 90

        val7 = self.calculate_mean(self.left_arm_level_elbow_calibration_results, reversed=False)
        if self.skipped_exercises[4]:
            val7 = 255
        elif val7 > 175:
            val7 = 175

        val8 = self.calculate_mean(self.right_arm_level_shoulder_calibration_results, reversed=False)
        if self.skipped_exercises[5]:
            val8 = 255
        elif val8 > 90:
            val8 = 90

        val9 = self.calculate_mean(self.right_arm_level_elbow_calibration_results, reversed=False)
        if self.skipped_exercises[5]:
            val9 = 255
        elif val9 > 175:
            val9 = 175

        val10 = self.calculate_mean(self.prayer_position_shoulder_calibration_results, reversed=False)  # max 80
        if self.skipped_exercises[6]:
            val10 = 255
        elif val10 > 80:
            val10 = 80

        val11 = self.calculate_mean(self.prayer_position_elbow_calibration_results, reversed=False)  # max 175
        if self.skipped_exercises[6]:
            val11 = 255
        elif val11 > 175:
            val11 = 175

        val12 = self.calculate_mean(self.lean_hands_calibration_results, reversed=True)
        val12 = 255  # TODO CHANGE
        val13 = self.calculate_mean(self.lean_body_calibration_results, reversed=True)
        val13 = 255  # TODO CHANGE
        val14 = 0

        new_vals_list = [val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14]
        fm.save_to_file(new_vals_list)

    def get_frame(self):  # TODO CHANGE NAME OF THE METHOD
        _, self.cap = self.vid.read()
        frame = cv2.cvtColor(self.cap, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # make detection
            results = pose.process(frame)

            # Reverse previous so that opencv can read this (RGB to BGR)
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
            # Extract landmarks
            landmarks = None
            try:
                landmarks = results.pose_landmarks.landmark

                def left_arm_bend():

                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                    angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    self.left_arm_bend_calibration_results.append(int(angle))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[1]
                        self.total_execrises_done += 1

                    # if len(self.left_arm_bend_calibration_results) > 50:
                    #     self.left_arm_bend_calibration_results.sort(reverse=True)
                    #     self.left_arm_bend_calibration_results = self.left_arm_bend_calibration_results[30:]

                def right_arm_bend():

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    self.right_arm_bend_calibration_results.append(int(angle))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[2]
                        self.total_execrises_done += 1

                    # if len(self.right_arm_bend_calibration_results) > 50:
                    #     self.right_arm_bend_calibration_results.sort(reverse=True)
                    #     self.right_arm_bend_calibration_results = self.right_arm_bend_calibration_results[30:]

                def left_arm_raise():

                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    left_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].y]

                    angle_left_shoulder = calculate_angle(left_mouth, left_shoulder, left_elbow)
                    angle_left_elbow = calculate_angle(left_shoulder, left_elbow, left_wrist)

                    self.left_arm_raise_shoulder_calibration_results.append(int(angle_left_shoulder))
                    self.left_arm_raise_elbow_calibration_results.append(int(angle_left_elbow))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[3]
                        self.total_execrises_done += 1

                    # if len(self.left_arm_raise_shoulder_calibration_results) > 50:
                    #     self.left_arm_raise_shoulder_calibration_results.sort(reverse=True) #TODO sprawdzic reversed wszedzie
                    #     self.left_arm_raise_elbow_calibration_results = self.left_arm_raise_elbow_calibration_results[
                    #                                                     30:]
                    #
                    #     self.left_arm_raise_shoulder_calibration_results.sort(reverse=True)
                    #     self.left_arm_raise_elbow_calibration_results = self.left_arm_raise_elbow_calibration_results[
                    #                                                     30:]

                def right_arm_raise():

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    right_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_LEFT.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.MOUTH_LEFT.value].y]

                    angle_right_shoulder = calculate_angle(right_mouth, right_shoulder, right_elbow)
                    angle_right_elbow = calculate_angle(right_shoulder, right_elbow, right_wrist)

                    self.right_arm_raise_shoulder_calibration_results.append(int(angle_right_shoulder))
                    self.right_arm_raise_elbow_calibration_results.append(int(angle_right_elbow))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[4]
                        self.total_execrises_done += 1

                    # if len(self.right_arm_raise_shoulder_calibration_results) > 50:
                    #     self.right_arm_raise_shoulder_calibration_results.sort(
                    #         reverse=True)  # TODO sprawdzic reversed wszedzie
                    #     self.right_arm_raise_elbow_calibration_results = self.right_arm_raise_elbow_calibration_results[
                    #                                                     30:]
                    #
                    #     self.right_arm_raise_shoulder_calibration_results.sort(reverse=True)
                    #     self.right_arm_raise_elbow_calibration_results = self.right_arm_raise_elbow_calibration_results[
                    #                                                     30:]

                def left_arm_level():

                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    left_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                    angle_left_shoulder = calculate_angle(left_hip, left_shoulder, left_elbow)
                    angle_left_elbow = calculate_angle(left_shoulder, left_elbow, left_wrist)

                    self.left_arm_level_shoulder_calibration_results.append(int(angle_left_shoulder))
                    self.left_arm_level_elbow_calibration_results.append(int(angle_left_elbow))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[5]
                        self.total_execrises_done += 1

                    # if len(self.left_arm_level_shoulder_calibration_results) > 50:
                    #     self.left_arm_level_shoulder_calibration_results.sort(
                    #         reverse=True)  # TODO sprawdzic reversed wszedzie
                    #     self.left_arm_level_elbow_calibration_results = self.left_arm_level_elbow_calibration_results[
                    #                                                     30:]
                    #
                    #     self.left_arm_level_shoulder_calibration_results.sort(reverse=True)
                    #     self.left_arm_level_elbow_calibration_results = self.left_arm_level_elbow_calibration_results[
                    #                                                     30:]

                def right_arm_level():

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    right_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

                    angle_right_shoulder = calculate_angle(right_hip, right_shoulder, right_elbow)
                    angle_right_elbow = calculate_angle(right_shoulder, right_elbow, right_wrist)

                    self.right_arm_level_shoulder_calibration_results.append(int(angle_right_shoulder))
                    self.right_arm_level_elbow_calibration_results.append(int(angle_right_elbow))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[6]
                        self.total_execrises_done += 1

                    # if len(self.right_arm_level_shoulder_calibration_results) > 50:
                    #     self.right_arm_level_shoulder_calibration_results.sort(
                    #         reverse=True)  # TODO sprawdzic reversed wszedzie
                    #     self.right_arm_level_elbow_calibration_results = self.right_arm_level_elbow_calibration_results[
                    #                                                     30:]
                    #
                    #     self.right_arm_level_shoulder_calibration_results.sort(reverse=True)
                    #     self.right_arm_level_elbow_calibration_results = self.right_arm_level_elbow_calibration_results[
                    #                                                     30:]

                def prayer_position():

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    right_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

                    angle_right_shoulder = calculate_angle(right_hip, right_shoulder, right_elbow)
                    angle_right_elbow = calculate_angle(right_shoulder, right_elbow, right_wrist)

                    self.prayer_position_shoulder_calibration_results.append(int(angle_right_shoulder))
                    self.prayer_position_elbow_calibration_results.append(int(angle_right_elbow))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[7]
                        self.total_execrises_done += 1

                    # if len(self.prayer_position_shoulder_calibration_results) > 50:
                    #     self.prayer_position_shoulder_calibration_results.sort(
                    #         reverse=True)  # TODO sprawdzic reversed wszedzie
                    #     self.prayer_position_elbow_calibration_results = self.prayer_position_elbow_calibration_results[
                    #                                                      30:]
                    #
                    #     self.prayer_position_shoulder_calibration_results.sort(reverse=True)
                    #     self.prayer_position_elbow_calibration_results = self.prayer_position_elbow_calibration_results[
                    #                                                      30:]

                def lean():

                    right_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    right_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]

                    angle_hands = calculate_angle(right_hip, right_shoulder, right_wrist)
                    angle_body = calculate_angle(right_knee, right_hip, right_shoulder)

                    self.lean_hands_calibration_results.append(int(angle_hands))
                    self.lean_body_calibration_results.append(int(angle_body))

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[8]
                        self.total_execrises_done += 1

                    # if len(self.lean_hands_calibration_results) > 50:
                    #     self.lean_hands_calibration_results.sort(
                    #         reverse=True)  # TODO sprawdzic reversed wszedzie
                    #     self.lean_hands_calibration_results = self.lean_hands_calibration_results[
                    #                                                      30:]
                    #
                    #     self.lean_body_calibration_results.sort(reverse=True)
                    #     self.lean_body_calibration_results = self.lean_body_calibration_results[
                    #                                                      30:]

                if self.current_exercise_name == EXERCISES[2]:
                    left_arm_raise()
                elif self.current_exercise_name == EXERCISES[3]:
                    right_arm_raise()

                elif self.current_exercise_name == EXERCISES[0]:
                    left_arm_bend()
                elif self.current_exercise_name == EXERCISES[1]:
                    right_arm_bend()

                elif self.current_exercise_name == EXERCISES[4]:
                    left_arm_level()
                elif self.current_exercise_name == EXERCISES[5]:
                    right_arm_level()

                elif self.current_exercise_name == EXERCISES[6]:
                    prayer_position()

                elif self.current_exercise_name == EXERCISES[7]:
                    lean()

                elif self.current_exercise_name == EXERCISES[8]:

                    if self.is_done != True:
                        self.is_done = True
                        self.save_to_file()
                    else:
                        pass

                else:
                    pass

            except:
                print("'try' failed")

        frame = imutils.resize(frame, height=self.height)
        imgtk = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        return imgtk


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
