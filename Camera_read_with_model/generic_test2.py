import os
import sys
import subprocess
import time
import keyboard
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

import PIL.Image
import PIL.ImageTk
import cv2
import imutils
import mediapipe as mp
import numpy as np

from PIL import ImageTk

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
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


class ExerciseApp:

    def __init__(self, root, vid_src=0):
        # setting title
        root.title("Sesja kalibracyjna")
        # setting window size
        self.screenwidth = root.winfo_screenwidth()
        self.screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (self.screenwidth, self.screenheight, 0, 0)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.feed = VidCapt(self.screenwidth, self.screenheight)
        self.exercise_count = self.feed.current_exercise_count
        self.camera_label = tk.Label(root)
        self.camera_label["bg"] = "#d65ac3"
        self.camera_label.place(x=self.screenwidth * 0.01, y=self.screenheight * 0.01, width=self.screenwidth * 0.49,
                                height=self.screenheight * 0.48)

        self.img_canvas = tk.Canvas(root)
        self.img_canvas["bg"] = "#000000"
        self.img_canvas.place(x=self.screenwidth * 0.501, y=self.screenheight * 0.01, width=self.screenwidth * 0.49,
                              height=self.screenheight * 0.48)

        self.instruction_label = tk.Label(root)
        self.instruction_label["bg"] = "#b5b5b5"
        self.instruction_label["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(self.screenheight * 0.03))
        self.instruction_label["font"] = ft
        self.instruction_label["fg"] = "#333333"
        self.instruction_label["justify"] = "center"
        self.instruction_label["text"] = "Instrukcje"
        self.instruction_label["relief"] = "groove"
        self.instruction_label.place(x=self.screenwidth * 0.01, y=self.screenheight * 0.5, width=self.screenwidth * 0.98,
                                height=self.screenheight * 0.35)

        return_button = tk.Button(root)
        return_button["activebackground"] = "#955d5d"
        return_button["activeforeground"] = "#393d49"
        return_button["bg"] = "#ff7800"
        return_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(self.screenheight * 0.03))
        return_button["font"] = ft
        return_button["fg"] = "#000000"
        return_button["justify"] = "center"
        return_button["text"] = "Powrot do menu"
        return_button["relief"] = "groove"
        return_button.place(x=self.screenwidth * 0.01, y=self.screenheight * 0.87, width=self.screenwidth * 0.32,
                            height=self.screenheight * 0.05)
        return_button["command"] = self.return_button_command

        stop_button = tk.Button(root)
        stop_button["activebackground"] = "#b46161"
        stop_button["activeforeground"] = "#4a3333"
        stop_button["bg"] = "#ffd700"
        stop_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(self.screenheight * 0.03))
        stop_button["font"] = ft
        stop_button["fg"] = "#000000"
        stop_button["justify"] = "center"
        stop_button["text"] = "Zatrzymaj trening"
        stop_button["relief"] = "groove"
        stop_button.place(x=self.screenwidth * 0.34, y=self.screenheight * 0.87, width=self.screenwidth * 0.32,
                          height=self.screenheight * 0.05)
        stop_button["command"] = self.stop_button_command

        skip_button = tk.Button(root)
        skip_button["activebackground"] = "#b46161"
        skip_button["activeforeground"] = "#4a3333"
        skip_button["bg"] = "#ffd700"
        skip_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(self.screenheight * 0.03))
        skip_button["font"] = ft
        skip_button["fg"] = "#000000"
        skip_button["justify"] = "center"
        skip_button["text"] = "Pomin cwiczenie"
        skip_button["relief"] = "groove"
        skip_button.place(x=self.screenwidth * 0.67, y=self.screenheight * 0.87, width=self.screenwidth * 0.32,
                          height=self.screenheight * 0.05)
        skip_button["command"] = self.skip_button_command

        self.pb = ttk.Progressbar(root)
        self.pb["orient"] = tk.HORIZONTAL
        self.pb["mode"] = "determinate"
        self.pb["length"] = self.screenwidth * 0.32
        self.pb.place(x=self.screenwidth * 0.34, y=self.screenheight * 0.92)

        self.pb["value"] = 0

        self.show_frames()

    def update_canvas(self, path="exercises_images_instruction/hand_curl_left.png"):
        self.image = PIL.Image.open(path)
        resize_image = self.image.resize((int(self.screenwidth * 0.49), int(self.screenheight * 0.48)))
        self.img = ImageTk.PhotoImage(resize_image)
        self.item_id = self.img_canvas.create_image((0, 0), image=self.img, anchor=tk.NW)


    def show_frames(self):
        imgtk = self.feed.get_frame()
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)
        self.camera_label.after(20, self.show_frames)
        self.exercise_name = self.feed.current_exercise_name
        self.update_instruction()
        self.pb["value"] = self.feed.update_pbar()

    def update_instruction(self):
        if self.exercise_name == EXERCISES[0]:
            self.instruction_label["text"] = \
                f"Zginanie lewej reki w łokciu.\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć lewym bokiem w stronę kamery\n" \
                f"Na ten moment zginasz rękę w łokciu pod kątem: {int(self.feed.current_angle_1)}\n"
            self.update_canvas(path="exercises_images_instruction/hand_curl_left.png")
        elif self.exercise_name == EXERCISES[1]:
            self.instruction_label["text"] = \
                f"Zginanie prawej reki w łokciu.\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć prawym bokiem w stronę kamery\n" \
                f"Na ten moment zginasz rękę w łokciu pod kątem: {int(self.feed.current_angle_1)}\n"
            self.update_canvas(path="exercises_images_instruction/hand_curl_right.png")

        elif self.exercise_name == EXERCISES[2]:
            self.instruction_label["text"] = \
                f"Podnoszenie lewej reki do gory. " \
                f"Rękę należy podnosić, mając jak najbardziej wyprostowaną. \n" \
                f"Rękę wyciągamy przed siebię, a nie w bok." \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć lewym bokiem w stronę kamery\n" \
                f"Na ten moment, kąt przy barku wynosi {int(self.feed.current_angle_1)}"
            self.update_canvas(path="exercises_images_instruction/hand_rise_left.png")
        elif self.exercise_name == EXERCISES[3]:
            self.instruction_label["text"] = \
                f"Podnoszenie prawej reki do gory. " \
                f"Rękę należy podnosić, mając jak najbardziej wyprostowaną. \n" \
                f"Rękę wyciągamy przed siebię, a nie w bok." \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć prawym bokiem w stronę kamery\n" \
                f"Na ten moment, kąt przy barku wynosi {int(self.feed.current_angle_1)}"
            self.update_canvas(path="exercises_images_instruction/hand_rise_right.png")

        elif self.exercise_name == EXERCISES[4]:
            self.instruction_label["text"] = \
                f"Podnoszenie lewej ręki do poziomu, starając się mieć jak najbardziej " \
                f"wyprostowane ręce w łokciach.\n" \
                f"W celu jak najdokładniejszego weryfikowania poprawności wykonywanego " \
                f"ćwiczenia,\n zalecane jest stanie frontem do kamery.\n" \
                f"Obecnie kąt w barku wynosi: {int(self.feed.current_angle_1)}, " \
                f"a w łokciu: {int(self.feed.current_angle_2)}.\n"
            self.update_canvas(path="exercises_images_instruction/left_hand_level.png")
        elif self.exercise_name == EXERCISES[5]:
            self.instruction_label["text"] = \
                f"Podnoszenie prawej ręki do poziomu, starając się mieć jak najbardziej " \
                f"wyprostowane ręce w łokciach.\n" \
                f"W celu jak najdokładniejszego weryfikowania poprawności wykonywanego " \
                f"ćwiczenia,\n zalecane jest stanie frontem do kamery.\n" \
                f"Obecnie kąt w barku wynosi: {int(self.feed.current_angle_1)}, " \
                f"a w łokciu: {int(self.feed.current_angle_2)}.\n"
            self.update_canvas(path="exercises_images_instruction/right_hand_level.png")

        elif self.exercise_name == EXERCISES[6]:
            self.instruction_label["text"] = \
                f"Łokcie należy mieć w okolicy brzuchu, a złożone ręce należy mieć jak nabliżej klatki piersiowej.\n" \
                f"Następnie wyciągamy je przed siebie, starając się mieć wyprostowane łokcie, " \
                f"\na kąt w barkach zbliżony do 90 stopni." \
                f"\nW celu jak najdokładniejszego weryfikowania poprawności wykonywanego ćwiczenia, \n" \
                f"zalecane jest stanąć prawym bokiem w stronę kamery\n" \
                f"Obecnie kąt w barkach wynosi {int(self.feed.current_angle_1)}, "\
                f"a w łokciach {int(self.feed.current_angle_2)}."
            self.update_canvas(path="exercises_images_instruction/praise_position.png")

        elif self.exercise_name == EXERCISES[7]:
            self.instruction_label["text"] = \
                f"Należy usiąść tak, żeby kamerka widziała dobrze prawą stronę ciała od " \
                f"kolan, aż po barki.\n Nie należy zapomnieć o zapasie, na wykonywanie ćwiczenia.\n" \
                f"Pochylamy się do przodu, tak, żeby przy zginiaiu się, kąt między kolanami, biodrem a barkiem \n" \
                f"był jak najmniejszy, a ręcę zachowywały się jak przy ćwiczeniu z podnoszeniem ich do góry.\n" \
                f"Na ten moment, kąt przy biodrze " \
                f"wynosi {int(self.feed.current_angle_2)}, a w łokciach {int(self.feed.current_angle_1)}"
            self.update_canvas(path="exercises_images_instruction/lean.png")

        elif self.exercise_name == EXERCISES[8]:
            self.instruction_label["text"] = "Cwiczenia zostaly ukonczone. Możesz teraz wrócić do menu i rozpocząć " \
                                             "sesję ćwiczeniową"
            self.update_canvas(path="exercises_images_instruction/done.png")

        else:
            pass

    def return_button_command(self):
        self.feed.release_feed()
        subprocess.Popen(["python", "main_menu.py"])
        time.sleep(5)
        sys.exit(0)

    def stop_button_command(self):
        self.feed.stop_exercises()
        if self.feed.is_stopped:
            self.stop_button["text"] = "Wznów trening"
        else:
            self.stop_button["text"] = "Zatrzymaj trening"

    def skip_button_command(self):
        self.feed.skip_exercise()


class VidCapt:

    def __init__(self, width, height, vid_src=0):
        self.vid = cv2.VideoCapture(vid_src)
        _, self.cap = self.vid.read()
        self.width = int(width * 0.48)
        self.height = int(height * 0.48)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose

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
        self.total_exercises_done = 0

        self.current_angle_1 = 0
        self.current_angle_2 = 0

        self.is_done = False
        self.is_stopped = False

    def skip_exercise(self):
        if self.current_exercise_name != EXERCISES[8]:
            self.skipped_exercises[EXERCISES.index(self.current_exercise_name)] = True
            new_index = EXERCISES.index(self.current_exercise_name) + 1
            self.current_exercise_name = EXERCISES[new_index]
            self.current_exercise_count = 0
            self.total_exercises_done += 1
        else:
            pass

    def stop_exercises(self):
        self.stopped += 1
        if self.stopped % 2 != 0:
            self.current_exercise_temp = EXERCISES.index(self.current_exercise_name)
            self.current_exercise_name = None
            self.is_stopped = True
        else:
            self.current_exercise_name = EXERCISES[self.current_exercise_temp]
            self.is_stopped = False

    def release_feed(self):
        self.vid.release()

    def update_pbar(self):
        return int((self.total_exercises_done / 8) * 100)

    def calculate_mean(self, results, reversed=False):
        results.sort(reverse=reversed)
        result = results[5:10]
        mean = sum(result)/len(result)
        return int(mean)

    def save_to_file(self): #TODO sprawdzic reversed czy nie trzeba odwrocic
        val0 = self.calculate_mean(self.left_arm_bend_calibration_results, reversed=False)
        if self.skipped_exercises[0]:
            val0 = 255
        elif val0 < 35:
            val0 = 35
        print(val0)

        val1 = self.calculate_mean(self.right_arm_bend_calibration_results, reversed=False)
        if self.skipped_exercises[1]:
            val1 = 255
        elif val1 < 35:
            val1 = 35
        print(val1)

        val2 = self.calculate_mean(self.left_arm_raise_shoulder_calibration_results, reversed=False)
        if self.skipped_exercises[2]:
            val2 = 255
        elif val2 < 50:
            val2 = 50
        print(val2)

        val3 = self.calculate_mean(self.left_arm_raise_elbow_calibration_results, reversed=True)
        if self.skipped_exercises[2]:
            val3 = 255
        elif val3 > 175:
            val3 = 175
        print(val3)

        val4 = self.calculate_mean(self.right_arm_raise_shoulder_calibration_results, reversed=False)
        if self.skipped_exercises[3]:
            val4 = 255
        elif val4 < 50:
            val4 = 50
        print(val4)

        val5 = self.calculate_mean(self.right_arm_raise_elbow_calibration_results, reversed=True)
        if self.skipped_exercises[3]:
            val5 = 255
        elif val5 > 175:
            val5 = 175
        print(val5)
        
        val6 = self.calculate_mean(self.left_arm_level_shoulder_calibration_results, reversed=True)
        if self.skipped_exercises[4]:
            val6 = 255
        elif val6 > 90:
            val6 = 90
        print(val6)

        val7 = self.calculate_mean(self.left_arm_level_elbow_calibration_results, reversed=True)
        if self.skipped_exercises[4]:
            val7 = 255
        elif val7 > 175:
            val7 = 175
        print(val7)
        
        val8 = self.calculate_mean(self.right_arm_level_shoulder_calibration_results, reversed=True)
        if self.skipped_exercises[5]:
            val8 = 255
        elif val8 > 90:
            val8 = 90
        print(val8)

        val9 = self.calculate_mean(self.right_arm_level_elbow_calibration_results, reversed=True)
        if self.skipped_exercises[5]:
            val9 = 255
        elif val9 > 175:
            val9 = 175
        print(val9)
        
        val10 = self.calculate_mean(self.prayer_position_shoulder_calibration_results, reversed=True)
        if self.skipped_exercises[6]:
            val10 = 255
        elif val10 > 80:
            val10 = 80
        print(val10)

        val11 = self.calculate_mean(self.prayer_position_elbow_calibration_results, reversed=True)
        if self.skipped_exercises[6]:
            val11 = 255
        elif val11 > 175:
            val11 = 175
        print(val11)

        val12 = self.calculate_mean(self.lean_hands_calibration_results, reversed=True)  #TODO max ???
        if self.skipped_exercises[7]:
            val12 = 255
        elif val12 > 175:
            val12 = 175
        print(val12)

        val13 = self.calculate_mean(self.lean_body_calibration_results, reversed=False)  # TODO max ???
        if self.skipped_exercises[7]:
            val13 = 255
        elif val13 > 175:
            val13 = 175

        print(val13)

        val14= 0

        new_vals_list = [val0, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, val14]
        fm.save_to_file(new_vals_list)

    def get_frame(self):
        _, self.cap = self.vid.read()
        frame = cv2.cvtColor(self.cap, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = pose.process(frame)

            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
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
                    self.current_angle_1 = angle

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[1]
                        self.total_exercises_done += 1

                    if len(self.left_arm_bend_calibration_results) == 50:
                        self.left_arm_bend_calibration_results.sort(reverse=False)
                        self.left_arm_bend_calibration_results = self.left_arm_bend_calibration_results[:20]

                def right_arm_bend():

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    self.right_arm_bend_calibration_results.append(int(angle))
                    self.current_angle_1 = angle

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[2]
                        self.total_exercises_done += 1

                    if len(self.right_arm_bend_calibration_results) == 50:
                        self.right_arm_bend_calibration_results.sort(reverse=False)
                        self.right_arm_bend_calibration_results = self.right_arm_bend_calibration_results[:20]

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

                    self.current_angle_1 = angle_left_shoulder
                    self.current_angle_2 = angle_left_elbow

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[3]
                        self.total_exercises_done += 1

                    if len(self.left_arm_raise_shoulder_calibration_results) == 50:
                        self.left_arm_raise_shoulder_calibration_results.sort(reverse=False)
                        self.left_arm_raise_elbow_calibration_results.sort(reverse=True)
                        self.left_arm_raise_shoulder_calibration_results = \
                            self.left_arm_raise_shoulder_calibration_results[:20]
                        self.left_arm_raise_elbow_calibration_results = \
                            self.left_arm_raise_elbow_calibration_results[:20]

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[4]
                        self.total_exercises_done += 1

                    if len(self.right_arm_raise_shoulder_calibration_results) == 50:
                        self.right_arm_raise_shoulder_calibration_results.sort(reverse=False)
                        self.right_arm_raise_elbow_calibration_results.sort(reverse=True)
                        self.right_arm_raise_shoulder_calibration_results = \
                            self.right_arm_raise_shoulder_calibration_results[:20]
                        self.right_arm_raise_elbow_calibration_results = \
                            self.right_arm_raise_elbow_calibration_results[:20]

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

                    self.current_angle_1 = angle_left_shoulder
                    self.current_angle_2 = angle_left_elbow

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[5]
                        self.total_exercises_done += 1

                    if len(self.left_arm_level_shoulder_calibration_results) == 50:
                        self.left_arm_level_shoulder_calibration_results.sort(reverse=True)
                        self.left_arm_level_elbow_calibration_results.sort(reverse=True)
                        self.left_arm_level_shoulder_calibration_results = \
                            self.left_arm_level_shoulder_calibration_results[:20]
                        self.left_arm_level_elbow_calibration_results = \
                            self.left_arm_level_elbow_calibration_results[:20]

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[6]
                        self.total_exercises_done += 1

                    if len(self.right_arm_level_shoulder_calibration_results) == 50:
                        self.right_arm_level_shoulder_calibration_results.sort(reverse=True)
                        self.right_arm_level_elbow_calibration_results.sort(reverse=True)
                        self.right_arm_level_shoulder_calibration_results = \
                            self.right_arm_level_shoulder_calibration_results[:20]
                        self.right_arm_level_elbow_calibration_results = \
                            self.right_arm_level_elbow_calibration_results[:20]

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[7]
                        self.total_exercises_done += 1

                    if len(self.prayer_position_shoulder_calibration_results) == 50:
                        self.prayer_position_shoulder_calibration_results.sort(reverse=True)
                        self.prayer_position_elbow_calibration_results.sort(reverse=True)
                        self.prayer_position_shoulder_calibration_results = \
                            self.prayer_position_shoulder_calibration_results[:20]
                        self.prayer_position_elbow_calibration_results = \
                            self.prayer_position_elbow_calibration_results[:20]

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

                    self.current_angle_1 = angle_hands
                    self.current_angle_2 = angle_body

                    if keyboard.is_pressed('space'):
                        time.sleep(2)
                        self.current_exercise_name = EXERCISES[8]
                        self.total_exercises_done += 1

                    if len(self.lean_hands_calibration_results) == 50:
                        self.lean_hands_calibration_results.sort(reverse=True)
                        self.lean_hands_calibration_results = self.lean_hands_calibration_results[:20]

                        self.lean_body_calibration_results.sort(reverse=False)
                        self.lean_body_calibration_results = self.lean_body_calibration_results[:20]

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

                    if not self.is_done:
                        self.is_done = True
                        self.save_to_file()
                    else:
                        pass

                else:
                    pass

            except:
                pass

        frame = imutils.resize(frame, height=self.height)
        imgtk = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        return imgtk


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
