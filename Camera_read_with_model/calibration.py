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
from imutils.video import VideoStream



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


class App:

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
        self.camera_label.place(x=screenwidth * 0.01, y=screenheight * 0.01, width=screenwidth * 0.48,
                                height=screenheight * 0.48)

        self.img_canvas = tk.Canvas(root)
        self.img_canvas["bg"] = "#000000"
        self.img_canvas.place(x=screenwidth * 0.5, y=screenheight * 0.01, width=screenwidth * 0.48,
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

        pb = ttk.Progressbar(root)
        pb["orient"] = tk.VERTICAL
        pb["mode"] = "determinate"
        pb["length"] = screenheight * 0.48
        pb.place(x=screenwidth * 0.983, y=screenheight * 0.01)

        pb["value"] = 70

        self.show_frames()

    def show_frames(self):
        imgtk = self.feed.get_frame()
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)
        # tu przyda sie threading
        self.camera_label.after(20, self.show_frames)
        self.exercise_name = self.feed.current_exercise_name
        self.update_instruction()

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
        if self.exercise_name == "left_arm_bend":
            self.instruction_label["text"] = "Zginanie lewej reki"
        elif self.exercise_name == "right_arm_bend":
            self.instruction_label["text"] = "Zginanie prawej reki"

        elif self.exercise_name == "left_arm_raise":
            self.instruction_label["text"] = "Podnoszenie lewej reki do gory"
        elif self.exercise_name == "right_arm_raise":
            self.instruction_label["text"] = "Podnoszenie prawej reki do gory"

        elif self.exercise_name == "left_arm_level":
            self.instruction_label["text"] = "Podnoszenie lewej ręki do poziomu"
        elif self.exercise_name == "right_arm_level":
            self.instruction_label["text"] = "Podnoszenie prawej ręki do poziomu"

        elif self.exercise_name == "prayer_position":
            self.instruction_label["text"] = "Prayer position"

        elif self.exercise_name == "lean":
            self.instruction_label["text"] = "skłon tułowia"

        elif self.exercise_name == "None":
            self.instruction_label["text"] = "Kalibracja została ukończona"

        else:
            pass

    def return_button_command(self):
        print("back to menu")

    def stop_button_command(self):
        # TODO change from exit to freeze
        exit()
        print("stop/resume")

    def skip_button_command(self):
        print("skip")


class VidCapt:

    def __init__(self, width, height, vid_src=0):
        self.cap = VideoStream(src=vid_src).start()
        self.width = int(width * 0.48)
        self.height = int(height * 0.48)

        self.mp_drawing = mp.solutions.drawing_utils  # wizualizacja wykrywania
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose  # import pose estimation model  (konkretnego)

        self.current_exercise_count = 0
        self.stage = "down"
        self.current_exercise_name = "right_arm_raise"


    def get_frame(self): #TODO CHANGE NAME OF THE METHOD
        frame = cv2.cvtColor(self.cap.read(), cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # make detection
            results = pose.process(frame)

            # Reverse previous so that opencv can read this (RGB to BGR)
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # To do wywalenia pojdzie
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
            # Extract landmarks
            landmarks = None
            try:
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
                landmarks = results.pose_landmarks.landmark

                def left_arm_bend():

                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                    angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    if angle < 90 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle > 90 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "right_arm_bend"
                            self.current_exercise_count = 0
                    else:
                        pass

                def right_arm_bend():
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    if angle < 90 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle > 90 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "left_arm_raise"
                            self.current_exercise_count = 0
                    else:
                        pass

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

                    if angle_left_shoulder < 90 and angle_left_elbow > 90 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_left_shoulder > 90 and left_wrist[1] > left_shoulder[1] and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "right_arm_raise"
                            self.current_exercise_count = 0
                    else:
                        pass

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

                    if angle_right_shoulder < 90 and angle_right_elbow > 90 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_right_shoulder > 90 and right_wrist[1] > right_shoulder[1] and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "left_arm_level"
                            self.current_exercise_count = 0

                def left_arm_level():
                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    left_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].y]

                    angle_left_shoulder = calculate_angle(left_mouth, left_shoulder, left_elbow)
                    angle_left_elbow = calculate_angle(left_shoulder, left_elbow, left_wrist)

                    if 90 < angle_left_shoulder < 110 and angle_left_elbow > 160 and self.stage == "down": #TODO wrong values
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_left_shoulder > 160 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "right_arm_level"
                            self.current_exercise_count = 0
                    else:
                        pass

                def right_arm_level():
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    right_mouth = [landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.MOUTH_RIGHT.value].y]

                    angle_right_shoulder = calculate_angle(right_mouth, right_shoulder, right_elbow)
                    angle_right_elbow = calculate_angle(right_shoulder, right_elbow, right_wrist)

                    if 90 < angle_right_shoulder < 110 and angle_right_elbow > 160 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_right_shoulder > 160 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "prayer_position"
                            self.current_exercise_count = 0
                    else:
                        pass

                def prayer_position():
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    right_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

                    angle_right_elbow = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    angle_right_shoulder = calculate_angle(right_hip, right_shoulder, right_elbow)
                    #UP - kąt pomiędzy łokciami, ramionami i biodrem > 75 i kąt pomiędzy łokieć nadgarstek ramię > 75
                    #DOWN - kąt pomiędzy łokciami, ramionami i biodrem < 30 i kąt pomiędzy łokieć nadgarstek ramię < 90
                    if angle_right_shoulder > 75 and angle_right_elbow > 75 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_right_shoulder < 30 and angle_right_elbow < 90 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "lean"
                            self.current_exercise_count = 0

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
                    print(angle_hands)
                    print(angle_body)

                    if angle_hands > 90 and angle_body < 60 and self.stage == "down":
                        self.stage = "up"
                        self.current_exercise_count += 1
                        print(f"{self.current_exercise_count} udało się wykonać ćwiczenie")
                    elif angle_hands < 90 and angle_body > 60 and self.stage == "up":
                        self.stage = "down"
                        if self.current_exercise_count == 3:
                            self.current_exercise_name = "None"
                            self.current_exercise_count = 0
                    else:
                        pass


                if self.current_exercise_name == "left_arm_raise":
                    left_arm_raise()
                elif self.current_exercise_name == "right_arm_raise":
                    right_arm_raise()

                elif self.current_exercise_name == "left_arm_bend":
                    left_arm_bend()
                elif self.current_exercise_name == "right_arm_bend":
                    right_arm_bend()

                elif self.current_exercise_name == "left_arm_level":
                    left_arm_level()
                elif self.current_exercise_name == "right_arm_level":
                    right_arm_level()

                elif self.current_exercise_name == "prayer_position":
                    prayer_position()

                elif self.current_exercise_name == "lean":
                    lean()

                elif self.current_exercise_name == "None":
                    pass

                else:
                    print("niby jak")

            except:
                print("'try' failed")

        frame = imutils.resize(frame, height=self.height)
        imgtk = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        return imgtk


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
