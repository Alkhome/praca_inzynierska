import tkinter as tk
import tkinter.font as tkFont

class App:
    def __init__(self, root):
        root.title("Menu Glowne")
        # setting window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (screenwidth, screenheight, 0, 0)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

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
        start_exercise_button.place(x=screenwidth * 0.01, y=screenheight * 0.87, width=screenwidth * 0.32,
                                    height=screenheight * 0.05)
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
        calibrate_button.place(x=screenwidth * 0.01, y=screenheight * 0.47, width=screenwidth * 0.32,
                          height=screenheight * 0.05)
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
        instruction_button.place(x=screenwidth * 0.01, y=screenheight * 0.67, width=screenwidth * 0.32,
                               height=screenheight * 0.05)
        instruction_button["command"] = self.instruction_button_command

        back_to_menu_button = tk.Button(root)
        back_to_menu_button["activebackground"] = "#955d5d"
        back_to_menu_button["activeforeground"] = "#393d49"
        back_to_menu_button["bg"] = "#ff7800"
        back_to_menu_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        back_to_menu_button["font"] = ft
        back_to_menu_button["fg"] = "#000000"
        back_to_menu_button["justify"] = "center"
        back_to_menu_button["text"] = "Wyjdz z programu"
        back_to_menu_button["relief"] = "groove"
        back_to_menu_button.place(x=screenwidth * 0.01, y=screenheight * 0.17, width=screenwidth * 0.32,
                          height=screenheight * 0.05)
        back_to_menu_button["command"] = self.back_to_menu_button_command

    def back_to_menu_button_command(self):
        print("EXIT")
        exit()

    def calibrate_button_command(self):
        print("CALIBRATE")

    def instruction_button_command(self):
        print("INSTRUCTION")

    def start_exercise_button_command(self):
        print("START EXERCISES")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
