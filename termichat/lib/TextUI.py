import curses
from .TextPad import *

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

class TextUI(TextPad):
    def __init__(self, ssize):
        TextPad.__init__(self, ssize[1])
        self.ssize = ssize
        self.pminrow = 0

    def _update_pminrow(self):
        if self.ycur < self.pminrow:
            self.pminrow = self.ycur
        elif self.ycur - self.yshow > self.pminrow:
            self.pminrow = self.ycur - self.yshow

    def _refresh_text_pad(self):
        self._update_pminrow()
        pmin = (self.pminrow, 0)
        smin = (self.ssize[0]-self.yshow-2, 2)
        smax = (self.ssize[0]-2, self.ssize[1]-3)
        try:
            self.pad.refresh(*pmin, *smin, *smax)
        except:
            pass

    def _refresh_rect_pad(self):
        rsize = (self.yshow+3, self.ssize[1])
        rectpad = get_rect_pad(*rsize)
        pmin = (0, 0)
        smin = (self.ssize[0]-self.yshow-3, 0)
        smax = (self.ssize[0]-1, self.ssize[1]-1)
        try:
            rectpad.refresh(*pmin, *smin, *smax)
        except:
            pass

    def resize(self, ssize):
        self.ssize = ssize
        self._resize(ssize[1])
        self._update_pad()
        self._refresh_text_pad()
        self._refresh_rect_pad()

    def refresh(self):
        self.yshow = min(self.ymax, MAX_LINE-1)
        self._refresh_rect_pad()
        self._refresh_text_pad()
