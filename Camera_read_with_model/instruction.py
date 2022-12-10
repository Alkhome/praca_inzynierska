import tkinter as tk
import tkinter.font as tkFont
import tkinter.scrolledtext as st

import os
from tkinter import messagebox


class InstructionApp:
    def __init__(self, root):
        root.title("Instrukcja")
        # setting window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (screenwidth, screenheight, 0, 0)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        back_to_menu_button = tk.Button(root)
        back_to_menu_button["activebackground"] = "#955d5d"
        back_to_menu_button["activeforeground"] = "#393d49"
        back_to_menu_button["bg"] = "#ff7800"
        back_to_menu_button["borderwidth"] = "2px"
        ft = tkFont.Font(family='Times', size=int(screenheight * 0.03))
        back_to_menu_button["font"] = ft
        back_to_menu_button["fg"] = "#000000"
        back_to_menu_button["justify"] = "center"
        back_to_menu_button["text"] = "Powrot do menu"
        back_to_menu_button["relief"] = "groove"
        back_to_menu_button.place(x=screenwidth * 0.01, y=screenheight * 0.87, width=screenwidth * 0.32,
                                  height=screenheight * 0.05)
        back_to_menu_button["command"] = self.back_to_menu_button_command

        self.instruction = ""
        try:
            with open("instruction.txt", "r", encoding="utf-8") as file:
                self.instruction = file.read()
        except:
            messagebox.showerror(title="Nie znaleziono pliku z instrukcją",
                                 message="Program napotkał błąd krytyczny i nie może znaleźć pliku z instrukcją.\n"
                                         "W celu naprawienia tego błędu, zalecamy ponowną instalację oprogramowania\n"
                                         "Nastąpi teraz wyjście z aplikacji")
            exit()

        tk.Label(root, text="Instrukcja obsługi programu oraz wskazówki dotyczące ćwiczeń",
                 font=("Times New Roman", 32), background='#393d49',
                 foreground="white").place(x=screenwidth * 0.01, y=screenheight * 0.01, width=screenwidth * 0.98,
                                           height=screenheight * 0.05)

        text_area = st.ScrolledText(root, width=30, height=8, font=("Times New Roman", 13))
        text_area.place(x=screenwidth * 0.01, y=screenheight * 0.07, width=screenwidth * 0.98,
                        height=screenheight * 0.78)
        text_area.insert(tk.INSERT, self.instruction)
        text_area.configure(state='disabled')

    @staticmethod
    def back_to_menu_button_command():
        os.system("python main_menu.py")


if __name__ == "__main__":
    root = tk.Tk()
    app = InstructionApp(root)
    root.mainloop()
