"""
A Seven-Segment Display in a GUI.py

Created by Jas Lau on 7/30/19.
Copyright © 2019 Jas Lau. All rights reserved.
"""
import tkinter as tk
import tkinter.messagebox as tkmb
import seven_segment_logic as ssl


# ================================ Client (As a Function) ================================

def main():
    root_win = tk.Tk()
    demo_cls_ref = SevenSegmentGUI(root_win)
    demo_cls_ref.get_root().title("Seven Segment Display")
    demo_cls_ref.get_root().mainloop()


# ============================== End of Client (As a Function) ==============================

# =================================== SevenSegmentGUI Class =================================

class SevenSegmentGUI:
    INITIAL_DIG = 0
    INITIAL_CAN_WIDTH = 250
    INITIAL_CAN_HEIGHT = 300
    HILITE_PAD = 0
    # add
    BAD_USER_INPUT = -1
    MIN_NUM = 0
    MAX_NUM = 15

    # constructor
    def __init__(self, master_root=None):
        # our member to support the ssl
        self.sev_seg_logic = ssl.SevenSegmentLogic()
        # define digit to display that can be overwritten by user
        self.digit_to_show = self.INITIAL_DIG

        # set up mutable width and height for resizing
        self.canvas_width = self.INITIAL_CAN_WIDTH
        self.canvas_height = self.INITIAL_CAN_HEIGHT

        # -------------- store root reference locally --------------
        if not self.set_root(master_root):
            stand_in = tk.Tk()
            self.set_root(stand_in)

        # --------- a container frame and subframes ----------------
        self.container = tk.Frame(self.root, bg="ghostwhite", padx=10, pady=10)
        self.title_frame = tk.Frame(self.container, bg="ghostwhite")
        self.work_frame = tk.Frame(self.container, bg="ghostwhite")
        self.canvas_frame = tk.Frame(self.container, bg="gray3", padx=3, pady=3)

        # -------------- one message widget ------------------------
        header = "Enter a hex digit to display (0-9, A-F)"
        self.msg_head = tk.Message(self.title_frame, text=header)
        self.msg_head.config(font=("Helvetica Neue", 11), bg="ghostwhite",
                             width=300)

        # ----------------- some label widgets ------------------
        self.lab_digit = tk.Label(self.work_frame, text="Digit:", padx=20,
                                  pady=10, bg="ghostwhite")

        # ----------------- some entry widgets ------------------
        self.enter_digit = tk.Entry(self.work_frame)
        self.enter_digit.insert(0, str(self.digit_to_show))
        # add
        # Binding the self.update_canvas event handler to a <Return> event in
        # the entry field.
        self.enter_digit.bind("<Return>", self.update_canvas)

        # ----------------- the canvas widget ------------------
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width,
                                height=self.canvas_height, bg="gray3",
                                highlightthickness=self.HILITE_PAD)

        # ------- place widgets using pack and grid layout ---------
        self.container.pack(expand=True, fill=tk.BOTH)
        self.canvas_frame.pack(side="right", expand=True, fill=tk.BOTH)
        self.title_frame.pack(expand=True, fill=tk.BOTH)
        self.work_frame.pack(expand=True, fill=tk.BOTH)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.msg_head.pack(expand=True, fill=tk.BOTH)

        self.lab_digit.grid(row=0, column=0, sticky=tk.E)
        self.enter_digit.grid(row=0, column=1, sticky=tk.W)

        # -- update dimensions when resized (including 1st time)  --
        self.canvas.bind("<Configure>", self.resize_can)

    # mutators
    def set_root(self, rt):
        if self.valid_tk_root(rt):
            self.root = rt
            return True
        # else
        return False

    def set_title(self, title):
        if type(title) == str:
            self.root.title = title
            return True
        # else
        return False

    # accessor
    def get_root(self):
        return self.root

    # static helper
    @staticmethod
    def valid_tk_root(am_i_a_root):
        if type(am_i_a_root) == tk.Tk:
            return True
        # else
        return False

    # bound event handler gets new dimensions and redraws when resized
    def resize_can(self, event):
        # without 2 * hi-light pad, get runaway window
        self.canvas_width = float(event.width) - (2 * self.HILITE_PAD)
        self.canvas_height = float(event.height) - (2 * self.HILITE_PAD)

        # change the size, then redraw everything (alt: Canvas's scale())
        self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
        self.update_canvas()

    @classmethod
    def convert_hex_char_to_int(cls, input_val):
        try:
            if type(input_val) is not str or len(input_val) != 1:
                return cls.BAD_USER_INPUT
            ret_int = int(input_val, 16)
        except ValueError:
            return cls.BAD_USER_INPUT
        else:
            return ret_int

    @classmethod
    def valid_input(cls, input_val):
        if not (cls.MIN_NUM <= input_val <= cls.MAX_NUM):
            return False
        return True

    # canvas updater
    def update_canvas(self, *args):
        self.canvas.delete("all")
        CLICK = .02
        CAP = .0175
        LEN = .3
        TL_X = .35
        TL_Y = .15
        SLANT = .04  # range that looks fair: 0.0 - 0.07)

        # for a shorter xy_func_list[] definition
        vert_func = self.draw_vert_seg
        horiz_func = self.draw_horiz_seg

        # list consisting of (x, y, function) for each segment a - g
        xy_func_list = [
            # seg a
            (TL_X + CLICK, TL_Y, horiz_func),
            # seg b
            (TL_X + LEN + 2 * CAP + 2 * CLICK, TL_Y, vert_func),
            # seg c
            (TL_X - SLANT + LEN + (2. * CAP) + (2. * CLICK),
             TL_Y + LEN + (2. * CAP), vert_func),
            # seg d
            (TL_X - (2 * SLANT) + CLICK, TL_Y + (2 * LEN) + (4 *
                                                             CAP), horiz_func),
            # seg e
            (TL_X - SLANT, TL_Y + LEN + (2. * CAP), vert_func),
            # seg f
            (TL_X, TL_Y, vert_func),
            # seg g
            (TL_X - SLANT + CLICK, TL_Y + LEN + (2. * CAP), horiz_func)
        ]

        simulated_user_str = self.enter_digit.get()
        # convert from hex to int
        user_int = self.convert_hex_char_to_int(simulated_user_str)

        # SSL turns any error/exception into "E" for display,
        # so out-of-range ints that pass above will be displayed as "E"
        if not self.valid_input(user_int):
            # Show Error Message
            tkmb.showerror("Input Error", "Single (Hex) Digits (as a string) "
                                          "Only, Please.")
            self.sev_seg_logic.eval(14)

        # else if it is in range
        elif self.valid_input(user_int):
            self.sev_seg_logic.eval(user_int)

        # draw each segment using draw() method in xy_func_list[k][2]()
        for k in range(7):
            if self.sev_seg_logic.get_val_of_seg(k):
                xy_func_list[k][2](xy_func_list[k][0], xy_func_list[k][1], LEN,
                                   CAP, SLANT)

    def draw_vert_seg(self, x, y, length, end, slant):
        # tall, narrow hexagon
        points = [x * self.canvas_width, y * self.canvas_height, (x - end) * self.canvas_width,
                  (y + end) * self.canvas_height, (x - end - slant) * self.canvas_width,
                  (y + end + length) * self.canvas_height, (x - slant) * self.canvas_width,
                  (y + length + (2 * end)) * self.canvas_height,
                  (x + end - slant) * self.canvas_width, (y + end + length) * self.canvas_height,
                  (x + end) * self.canvas_width, (y + end) * self.canvas_height]
        self.canvas.create_polygon(points, fill="orange red", width=0)

    def draw_horiz_seg(self, x, y, length, end, dummy=None):
        """ last param is to make signature match draw_vert_seg()
        for next phase -- horiz segs don"t have slants """
        # long, thin hexagon
        points = [x * self.canvas_width, y * self.canvas_height, (x + end) * self.canvas_width,
                  (y + end) * self.canvas_height, (x + end + length) * self.canvas_width,
                  (y + end) * self.canvas_height, (x + length + (2 * end)) * self.canvas_width,
                  y * self.canvas_height, (x + end + length) * self.canvas_width,
                  (y - end) * self.canvas_height, (x + end) * self.canvas_width,
                  (y - end) * self.canvas_height]
        self.canvas.create_polygon(points, fill="orange red", width=0)


# ============================== End Of SevenSegmentGUI Class ==============================

# ====================================== Main Program ======================================

if __name__ == "__main__":
    main()
