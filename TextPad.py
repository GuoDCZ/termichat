import curses
from TextEditor import TextEditor

MAX_LINE = 8

class TextPad(TextEditor):
    def __init__(self, ssize):
        super(TextPad, self).__init__()
        self.ssize = ssize
        self.maxyx = (0,0)
        self.pad: curses.window = curses.newpad(20, ssize[1]-4)
        self.pad.keypad(True)
        self._update_rect_pad()
        self._update_psize()
        self.pminrow = 0

    def _update_rect_pad(self):
        prow = min(self.maxyx[0], MAX_LINE-1)
        rsize = (prow+3, self.ssize[1])
        self.rectpad = curses.newpad(rsize[0]+1,rsize[1])
        self.rectpad.keypad(True)
        for row in range(1,rsize[0]-1):
            self.rectpad.addch(row, 0, '│')
            self.rectpad.addch(row, rsize[1]-1, '│')
        for col in range(1,rsize[1]-1):
            self.rectpad.addch(0, col, '─')
            self.rectpad.addch(rsize[0]-1, col, '─')
        self.rectpad.addch(0, 0, '╭')
        self.rectpad.addch(0, rsize[1]-1, '╮')
        self.rectpad.addch(rsize[0]-1, 0, '╰')
        self.rectpad.addch(rsize[0]-1, rsize[1]-1, '╯')
        smin = (self.ssize[0]-rsize[0], 0)
        smax = (self.ssize[0]-1, self.ssize[1]-1)
        self.rectpad.refresh(0, 0, *smin, *smax)

    def _update_psize(self):
        self.psize = self.pad.getmaxyx()

    def _check_extension(self):
        if self.psize[0] - self.maxyx[0] < 10:
            self.pad.resize(self.psize[0]+10, self.psize[1])
        self._update_psize()

    def _update_pad(self):
        self.pad.clear()
        self.pad.addstr(self.s[:self.i])
        self.curyx = self.pad.getyx()
        self.pad.addstr(self.s[self.i:])
        self.maxyx = self.pad.getyx()
        self.pad.move(*self.curyx)
        self._check_extension()

    def _update_pminrow(self):
        if self.maxyx[0] < MAX_LINE-1:
            self.pminrow = 0
        elif self.curyx[0] < self.pminrow:
            self.pminrow = self.curyx[0]
        elif self.curyx[0] - (MAX_LINE-1) > self.pminrow:
            self.pminrow = self.curyx[0] - (MAX_LINE-1)

    def refresh(self):
        self._update_rect_pad()
        prow = min(self.maxyx[0], MAX_LINE-1)
        self._update_pminrow()
        smin = (self.ssize[0]-prow-2, 2)
        smax = (self.ssize[0]-2, self.ssize[1]-3)
        self.pad.refresh(self.pminrow, 0, *smin, *smax)

    def resize(self, size):
        self.ssize = size
        nlines = self.psize[0] * self.psize[1] // size[1] + 1
        while nlines % 10 != 0:
            nlines += 1
        self.pad.resize(nlines, size[1])
        self._update_psize()

    def set(self, s):
        self.s = s
        self.i = len(s)
        self._update_pad()

    def clear(self):
        self.s = ''
        self.i = 0
        self._update_pad()

    def put_key(self, key):
        if key == 127: # BACK_SPACE
            self.remove_left()
        elif key == 258: # DOWN
            self.move_down()
        elif key == 259: # UP
            self.move_up()
        elif key == 260: # LEFT
            self.move_left()
        elif key == 261: # RIGHT
            self.move_right()
        elif key == 262: # Fn + LEFT
            self.move_left_most()
        elif key == 330: # DELETE 
            self.remove_right()
        elif key == 338: # Fn + DOWN
            self.move_down_most()
        elif key == 339: # Fn + UP
            self.move_up_most()
        elif key == 360: # Fn + RIGHT
            self.move_right_most()
        elif key == 383: # SHIFT + DELETE 
            self.remove_line()
        else: # printable (maybe) character
            self.insert(key)
        self._update_pad()
