import curses
from TextEditor import *

class TextPad(TextEditor):
    def __init__(self, ncols):
        TextEditor.__init__(self)
        self.psize = (20, ncols-4)
        self.pad: curses.window = curses.newpad(*self.psize)
        self.ymax = 0
        self.ycur = 0
        self.saved = False

    def _check_size(self):
        if self.psize[0] < self.ymax+10 or self.psize[0] > self.ymax+20:
            self.pad.resize(self.ymax+20, self.psize[1])
            self.psize = self.pad.getmaxyx()
        
    def _update_pad(self):
        self.pad.clear()
        self.pad.addstr(self.s[:self.i])
        yxcur = self.pad.getyx()
        self.ycur = yxcur[0]
        self.pad.addstr(self.s[self.i:])
        self.ymax = self.pad.getyx()[0]
        self.pad.move(*yxcur)
        self._check_size()
        
    def _resize(self, ncols):
        nlines = self.psize[0] * self.psize[1] // ncols + 1
        while nlines % 10 != 0:
            nlines += 1
        self.pad.resize(nlines, ncols)
        self.psize = self.pad.getmaxyx()

    def set(self, s):
        self.s = s
        self.i = len(s)
        self._update_pad()

    def clear(self):
        self.s = ''
        self.i = 0
        self._update_pad()

    def save(self):
        assert not self.saved
        self.s_saved = self.s
        self.i_saved = self.i
        self.saved = True

    def load(self):
        assert self.saved
        self.s = self.s_saved
        self.i = self.i_saved
        self._update_pad()
        self.saved = False

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
