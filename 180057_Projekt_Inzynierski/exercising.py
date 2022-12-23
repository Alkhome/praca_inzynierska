import os
import sys
import subprocess
import time

import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import ttk

import PIL.Image
import PIL.ImageTk
import cv2
import imutils
import mediapipe as mp
import numpy as np
from PIL import ImageTk

import file_mod as fm

FILE_PATH = "miscellaneous/exercises_params.txt"

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


class App:

    def __init__(self, root):
        root.title("Sesja ćwiczeniowa")
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
        self.instruction_label.place(x=self.screenwidth * 0.01, y=self.screenheight * 0.5,
                                     width=self.screenwidth * 0.98, height=self.screenheight * 0.35)

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

        self.stop_button = tk.Button(root)
        self.stop_button["activebackground"] = "#b46161"
        self.stop_button["activeforeground"] = "#4a3333"
        self.stop_button["bg"] = "#ffd700"
        self.stop_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(self.screenheight * 0.03))
        self.stop_button["font"] = ft
        self.stop_button["fg"] = "#000000"
        self.stop_button["justify"] = "center"
        self.stop_button["text"] = "Zatrzymaj trening"
        self.stop_button["relief"] = "groove"
        self.stop_button.place(x=self.screenwidth * 0.34, y=self.screenheight * 0.87, width=self.screenwidth * 0.32,
                          height=self.screenheight * 0.05)
        self.stop_button["command"] = self.stop_button_command

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
                f"Zginanie lewej reki w łokciu aż do kąta {self.feed.params[0]}.\n" \
                f"Na ten moment zginasz rękę w łokciu pod kątem: {int(self.feed.current_angle_1)}\n" \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć lewym bokiem w stronę kamery" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/hand_curl_left.png")
        elif self.exercise_name == EXERCISES[1]:
            self.instruction_label["text"] = \
                f"Zginanie prawej reki w łokciu aż do kąta {self.feed.params[1]}.\n" \
                f"Na ten moment zginasz rękę w łokciu pod kątem: {int(self.feed.current_angle_1)}\n" \
                f"Ilość powtórzeń tego ćwiczenia, żeby je zaliczyć, to: {3 - self.feed.current_exercise_count % 3}" \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć prawym bokiem w stronę kamery" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/hand_curl_right.png")

        elif self.exercise_name == EXERCISES[2]:
            self.instruction_label["text"] = \
                f"Podnoszenie lewej reki do gory. Należy podnosić rękę tak, żeby kąt przy barku wynosił " \
                f"{self.feed.params[2]}, a w łokciu {self.feed.params[3]}.\n " \
                f"Na ten moment, kąt przy barku wynosi {int(self.feed.current_angle_1)}, " \
                f"a przy łokciu {int(self.feed.current_angle_2)}.\n" \
                f"Rękę należy podnosić, mając jak najbardziej wyprostowaną. Rękę wyciągamy przed siebię, a nie w bok." \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć lewym bokiem w stronę kamery" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/hand_rise_left.png")
        elif self.exercise_name == EXERCISES[3]:
            self.instruction_label["text"] = \
                f"Podnoszenie prawej reki do gory. Należy podnosić rękę tak, żeby kąt przy barku wynosił " \
                f"{self.feed.params[4]}, a w łokciu {self.feed.params[5]}.\n " \
                f"Na ten moment, kąt przy barku wynosi {int(self.feed.current_angle_1)}, " \
                f"a przy łokciu {int(self.feed.current_angle_2)}.\n" \
                f"Rękę należy podnosić, mając jak najbardziej wyprostowaną. Rękę wyciągamy przed siebię, a nie w bok." \
                f"\nW celu jak najdokładniejszego weryfikowania ćwiczenia, " \
                f"zalecane jest stanąć prawym bokiem w stronę kamery" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/hand_rise_right.png")

        elif self.exercise_name == EXERCISES[4]:
            self.instruction_label["text"] = \
                f"Podnoszenie lewej ręki do poziomu, starając się mieć jak najbardziej " \
                f"wyprostowane ręce w łokciach. \n" \
                f"Należy podnieść rękę tak, żeby kąt w barku wynosił: " \
                f"{self.feed.params[6]} a w łokciu: {self.feed.params[7]}.\n " \
                f"Obecnie kąt w barku wynosi: {int(self.feed.current_angle_1)}, " \
                f"a w łokciu: {int(self.feed.current_angle_2)}.\n" \
                f"W celu jak najdokładniejszego weryfikowania poprawności wykonywanego " \
                f"ćwiczenia,\n zalecane jest stanie frontem do kamery." \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/left_hand_level.png")
        elif self.exercise_name == EXERCISES[5]:
            self.instruction_label["text"] = \
                f"Podnoszenie prawej ręki do poziomu, starając się mieć jak najbardziej " \
                f"wyprostowane ręce w łokciach. \n" \
                f"Należy podnieść rękę tak, żeby kąt w barku wynosił: " \
                f"{self.feed.params[8]} a w łokciu: {self.feed.params[9]}.\n " \
                f"Obecnie kąt w barku wynosi: {int(self.feed.current_angle_1)}, " \
                f"a w łokciu: {int(self.feed.current_angle_2)}.\n" \
                f"W celu jak najdokładniejszego weryfikowania poprawności wykonywanego " \
                f"ćwiczenia, \nzalecane jest stanie frontem do kamery." \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/right_hand_level.png")

        elif self.exercise_name == EXERCISES[6]:
            self.instruction_label["text"] = \
                f"Łokcie należy mieć w okolicy brzuchu, a złożone ręce należy mieć jak nabliżej klatki piersiowej.\n" \
                f"Następnie wyciągamy je przed siebie tak, żeby kąt w barkamch wyniósł {self.feed.params[10]}, " \
                f"a w łokciach {self.feed.params[11]}.\n Obecnie kąt w barkach wynosi {int(self.feed.current_angle_1)}"\
                f" a w łokciach {int(self.feed.current_angle_2)}." \
                f"\nW celu jak najdokładniejszego weryfikowania poprawności wykonywanego ćwiczenia, \n" \
                f"zalecane jest stanąć prawym bokiem w stronę kamery" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/praise_position.png")

        elif self.exercise_name == EXERCISES[7]:
            self.instruction_label["text"] = \
                f"Należy usiąść tak, żeby kamerka widziała dobrze prawą stronę ciała od " \
                f"kolan, aż po barki.\n Nie należy zapomnieć o zapasie, na wykonywanie ćwiczenia.\n" \
                f"Pochylamy się do przodu, tak, żeby przy zginiaiu się, kąt między kolanami, biodrem a barkiem wyniósł"\
                f" {self.feed.params[13]},\n a w łokciach {self.feed.params[12]}.\nNa ten moment, kąt przy biodrze " \
                f"wynosi {int(self.feed.current_angle_2)}, a w łokciach {int(self.feed.current_angle_1)}" \
                f"\nIlość powtórzeń, które należy wykonać, żeby zaliczyć to ćwiczenie, to: " \
                f"{3 - self.feed.current_exercise_count % 3}"
            self.update_canvas(path="exercises_images_instruction/lean.png")

        elif self.exercise_name == EXERCISES[8]:
            self.instruction_label["text"] = "Cwiczenia zostaly ukończone. Możesz teraz wrócić do menu i zakończyć " \
                                             "działanie programu."
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

        self.skipped = False
        self.stopped = 0
        self.current_exercise_temp = None

        self.params = []
        self.is_done = False
        self.is_stopped = False

        self.current_angle_1 = 0
        self.current_angle_2 = 0

        self.total_exercises_done = 0

        try:
            file = open(file=FILE_PATH, mode="r")
            for line in file:
                self.params.append(int(line.rstrip()))
            file.close()
        except:
            messagebox.showwarning(title="Nie znaleziono pliku po kalibracji",
                                   message="Upewnij się, że wykonałeś kalibrację, zanim rozpoczniesz ćwiczenia.\n"
                                           "Zostaniesz teraz przeniesiony do menu głównego")
            os.system("python main_menu.py")

        self.sslff = self.params[14] #  Sessions Since Last Fully Finished

    def update_pbar(self):
        return int((self.total_exercises_done / 24) * 100)


    def update_sslff(self):
        self.sslff += 1
        self.params[14] = self.sslff
        if self.sslff == 3 and self.skipped == False:
            self.update_file()
        else:
            fm.save_to_file(self.params)

    def update_file(self):

        if self.params[0] > 37:
            self.params[0] -= 3

        if self.params[1] > 37:
            self.params[1] -= 3

        if self.params[2] > 52:
            self.params[2] -= 3

        if self.params[3] < 173:
            self.params[3] += 3

        if self.params[4] > 52:
            self.params[4] -= 3

        if self.params[5] < 173:
            self.params[5] += 3

        if self.params[6] < 88:
            self.params[6] += 3

        if self.params[7] < 173:
            self.params[7] += 3

        if self.params[8] < 88:
            self.params[8] += 3

        if self.params[9] < 173:
            self.params[9] += 3

        if self.params[10] < 78:
            self.params[10] += 3

        if self.params[11] < 173:
            self.params[11] += 3

        if self.params[12] < 173:
            self.params[12] += 3

        if self.params[13] > 32:
            self.params[13] -= 3

        self.params[14] = 0

        fm.save_to_file(self.params)


    def skip_exercise(self):
        if self.current_exercise_name != EXERCISES[8]:
            new_index = EXERCISES.index(self.current_exercise_name) + 1
            self.current_exercise_name = EXERCISES[new_index]
            self.current_exercise_count = 0
            self.skipped = True
            x = self.total_exercises_done
            self.total_exercises_done = x + (3 - x % 3)
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

                    if self.params[0] == 255:
                        self.current_exercise_name = EXERCISES[1]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 3
                        return None


                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                    angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    self.current_angle_1 = angle

                    if angle < self.params[0] and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle > 160 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[1]
                            self.current_exercise_count = 0
                    else:
                        pass

                def right_arm_bend():

                    if self.params[1] == 255:
                        self.current_exercise_name = EXERCISES[2]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 6
                        return None

                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    self.current_angle_1 = angle

                    if angle < self.params[1] and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle > 160 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[2]
                            self.current_exercise_count = 0
                    else:
                        pass

                def left_arm_raise():

                    if self.params[2] == 255 or self.params[3] == 255:
                        self.current_exercise_name = EXERCISES[3]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 9
                        return None

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

                    self.current_angle_1 = angle_left_shoulder
                    self.current_angle_2 = angle_left_elbow

                    if angle_left_shoulder < self.params[2] and angle_left_elbow > self.params[3] and \
                            self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_left_shoulder > self.params[2] and left_wrist[1] > left_shoulder[1] and \
                            self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[3]
                            self.current_exercise_count = 0
                    else:
                        pass

                def right_arm_raise():

                    if self.params[4] == 255 or self.params[5] == 255:
                        self.current_exercise_name = EXERCISES[4]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 12
                        return None

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if angle_right_shoulder < self.params[4] and angle_right_elbow > self.params[5] and \
                            self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_right_shoulder > self.params[4] and right_wrist[1] > right_shoulder[1] and \
                            self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[4]
                            self.current_exercise_count = 0

                def left_arm_level():

                    if self.params[6] == 255 or self.params[7] == 255:
                        self.current_exercise_name = EXERCISES[5]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 15
                        return None

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

                    self.current_angle_1 = angle_left_shoulder
                    self.current_angle_2 = angle_left_elbow

                    if self.params[6] - 5 < angle_left_shoulder < self.params[6] + 5 and \
                            angle_left_elbow > self.params[7] and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_left_shoulder < 30 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[5]
                            self.current_exercise_count = 0
                    else:
                        pass

                def right_arm_level():

                    if self.params[8] == 255 or self.params[9] == 255:
                        self.current_exercise_name = EXERCISES[6]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 18
                        return None

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if self.params[8] - 5 < angle_right_shoulder < self.params[8] + 5 and \
                            angle_right_elbow > self.params[9] and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_right_shoulder < 30 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[6]
                            self.current_exercise_count = 0
                    else:
                        pass

                def prayer_position():

                    if self.params[10] == 255 or self.params[11] == 255:
                        self.current_exercise_name = EXERCISES[7]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 21
                        return None

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

                    self.current_angle_1 = angle_right_shoulder
                    self.current_angle_2 = angle_right_elbow

                    if angle_right_shoulder > self.params[10] and angle_right_elbow > self.params[11] and \
                            self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_right_shoulder < 30 and angle_right_elbow < 90 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[7]
                            self.current_exercise_count = 0

                def lean():

                    if self.params[12] == 255 or self.params[13] == 255:
                        self.current_exercise_name = EXERCISES[8]
                        self.current_exercise_count = 0
                        self.total_exercises_done = 24
                        return None

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

                    self.current_angle_1 = angle_hands
                    self.current_angle_2 = angle_body

                    if angle_hands > self.params[12] and angle_body < self.params[13] and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        self.total_exercises_done += 1
                    elif angle_hands < 90 and angle_body > 80 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = EXERCISES[8]
                            self.current_exercise_count = 0
                    else:
                        pass


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

                    if self.is_done:
                        pass
                    else:
                        self.is_done = True
                        if not self.skipped:
                            self.update_sslff()

                else:
                    pass

            except Exception:
                pass

        frame = imutils.resize(frame, height=self.height)
        imgtk = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        return imgtk


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
