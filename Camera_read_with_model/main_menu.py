import subprocess
import sys
import time
import tkinter as tk
import tkinter.font as tkFont

import PIL.Image
from PIL import ImageTk


class MainMenuApp:
    def __init__(self, root):
        root.title("Menu Glowne")
        # setting window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (screenwidth, screenheight, 0, 0)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.image = PIL.Image.open("miscellaneous/main_menu.png")
        resize_image = self.image.resize((int(screenwidth), int(screenheight)))
        self.img = ImageTk.PhotoImage(resize_image)
        label_bg = tk.Label(root, image=self.img)
        label_bg.place(x=0, y=0)

        start_exercise_button = tk.Button(root)
        start_exercise_button["activebackground"] = "#955d5d"
        start_exercise_button["activeforeground"] = "#393d49"
        start_exercise_button["bg"] = "#ff7800"
        start_exercise_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        start_exercise_button["font"] = ft
        start_exercise_button["fg"] = "#000000"
        start_exercise_button["justify"] = "center"
        start_exercise_button["text"] = "Rozpocznij cwiczenia"
        start_exercise_button["relief"] = "groove"
        start_exercise_button.place(x=screenwidth * 0.01, y=screenheight * 0.12, width=screenwidth * 0.32,
                                    height=screenheight * 0.1)
        start_exercise_button["command"] = self.start_exercise_button_command

        calibrate_button = tk.Button(root)
        calibrate_button["activebackground"] = "#955d5d"
        calibrate_button["activeforeground"] = "#393d49"
        calibrate_button["bg"] = "#ff7800"
        calibrate_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        calibrate_button["font"] = ft
        calibrate_button["fg"] = "#000000"
        calibrate_button["justify"] = "center"
        calibrate_button["text"] = "Kalibracja"
        calibrate_button["relief"] = "groove"
        calibrate_button.place(x=screenwidth * 0.01, y=screenheight * 0.32, width=screenwidth * 0.32,
                               height=screenheight * 0.1)
        calibrate_button["command"] = self.calibrate_button_command

        instruction_button = tk.Button(root)
        instruction_button["activebackground"] = "#955d5d"
        instruction_button["activeforeground"] = "#393d49"
        instruction_button["bg"] = "#ff7800"
        instruction_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        instruction_button["font"] = ft
        instruction_button["fg"] = "#000000"
        instruction_button["justify"] = "center"
        instruction_button["text"] = "Instrukcja"
        instruction_button["relief"] = "groove"
        instruction_button.place(x=screenwidth * 0.01, y=screenheight * 0.52, width=screenwidth * 0.32,
                                 height=screenheight * 0.1)
        instruction_button["command"] = self.instruction_button_command

        exit_button = tk.Button(root)
        exit_button["activebackground"] = "#955d5d"
        exit_button["activeforeground"] = "#393d49"
        exit_button["bg"] = "#ff7800"
        exit_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        exit_button["font"] = ft
        exit_button["fg"] = "#000000"
        exit_button["justify"] = "center"
        exit_button["text"] = "Wyjdz z programu"
        exit_button["relief"] = "groove"
        exit_button.place(x=screenwidth * 0.01, y=screenheight * 0.72, width=screenwidth * 0.32,
                          height=screenheight * 0.1)
        exit_button["command"] = self.exit_button_command

    def exit_button_command(self):
        sys.exit(0)

    def calibrate_button_command(self):
        subprocess.Popen(["python", "calibration.py"])
        time.sleep(5)
        sys.exit(0)

    def instruction_button_command(self):
        subprocess.Popen(["python", "instruction.py"])
        time.sleep(5)
        sys.exit(0)

    def start_exercise_button_command(self):
        subprocess.Popen(["python", "app_window.py"])
        time.sleep(5)
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()
