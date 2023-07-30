import curses
from TextEditor import TextEditor

MAX_LINE = 8

def get_rect_pad(nlines, ncols):
    rectpad = curses.newpad(nlines+1, ncols)
    for line in range(1, nlines-1):
        rectpad.addch(line, 0, '│')
        rectpad.addch(line, ncols-1, '│')
    for col in range(1, ncols-1):
        rectpad.addch(0, col, '─')
        rectpad.addch(nlines-1, col, '─')
    rectpad.addch(0, 0, '╭')
    rectpad.addch(0, ncols-1, '╮')
    rectpad.addch(nlines-1, 0, '╰')
    rectpad.addch(nlines-1, ncols-1, '╯')
    return rectpad

class TextPad(TextEditor):
    def __init__(self, ssize):
        TextEditor.__init__(self)
        self.ssize = ssize
        self.psize = (20, ssize[1]-4)
        self.pad: curses.window = curses.newpad(*self.psize)
        self.tmaxy = 0
        self.fminy = 0
        self.fnl = 1

    def _check_psize(self):
        if self.psize[0] < self.tmaxy+10 or self.psize[0] > self.tmaxy+20:
            self.pad.resize(self.tmaxy+20, self.psize[1])
            self.psize = self.pad.getmaxyx()
        
    def _update_pad(self):
        self.pad.clear()
        self.pad.addstr(self.s[:self.i])
        cursor_yx = self.pad.getyx()
        self.cury = cursor_yx[0]
        self.pad.addstr(self.s[self.i:])
        self.tmaxy = self.pad.getyx()[0]
        self.pad.move(*cursor_yx)
        self._check_psize()

    def _update_fminy(self):
        if self.tmaxy < MAX_LINE-1:
            self.fminy = 0
        elif self.cury < self.fminy:
            self.fminy = self.cury
        elif self.cury - (MAX_LINE-1) > self.fminy:
            self.fminy = self.cury - (MAX_LINE-1)

    def _refresh_text_pad(self):
        smin = (self.ssize[0]-self.fnl-1, 2)
        smax = (self.ssize[0]-2, self.ssize[1]-3)
        self._update_fminy()
        self.pad.refresh(self.fminy, 0, *smin, *smax)

    def _refresh_rect_pad(self):
        rsize = (self.fnl+2, self.ssize[1])
        rectpad = get_rect_pad(*rsize)
        smin = (self.ssize[0]-rsize[0], 0)
        smax = (self.ssize[0]-1, self.ssize[1]-1)
        rectpad.refresh(0, 0, *smin, *smax)

    def refresh(self):
        self.fnl = min(self.tmaxy+1, MAX_LINE)
        self._refresh_rect_pad()
        self._refresh_text_pad()
        
    def resize(self, size):
        self.ssize = size
        nlines = self.psize[0] * self.psize[1] // size[1] + 1
        while nlines % 10 != 0:
            nlines += 1
        self.pad.resize(nlines, size[1])
        self.psize = self.pad.getmaxyx()

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
