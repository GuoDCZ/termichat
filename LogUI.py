import curses
from LogPad import *

class LogUI(LogPad):
    def __init__(self, ssize):
        LogPad.__init__(self, ssize[1])
        self.ssize = ssize
        self.pminrow = 0
        self.yshow = self.ssize[0] - 4

    def update_yshow(self, textui_yshow):
        self.yshow = self.ssize[0] - textui_yshow - 4

    def stream_show_cmpl(self, cmpl):
        self._update_pad(up_to_curr=True)
        self.godown = True
        self._print_name({'role':'assistant'})
        content = ''
        for chunk in cmpl:
            chuck_msg = chunk['choices'][0]['delta']
            if 'content' in chuck_msg:
                delta_content = chuck_msg['content']
                content += delta_content
                self.pad.addstr(delta_content, self.attr['assistant'])
                self.yl = self.pad.getyx()[0]
                self._update_pminrow()
                self.refresh()
        return content

    def resize(self, ssize):
        self.ssize = ssize
        self._resize(ssize[1])
        self._update_pad()
        self._update_pminrow()

    def refresh(self):
        pmin = (self.pminrow, 0)
        smin = (0, 0)
        smax = (self.yshow, self.ssize[1]-1)
        try:
            self.pad.refresh(*pmin, *smin, *smax)
        except:
            pass

    def _update_pminrow(self):
        y = self.yl if self.godown else self.yu
        # assert y > 0
        if y < self.pminrow:
            self.pminrow = y
        elif y - self.yshow > self.pminrow:
            self.pminrow = y - self.yshow

    def scroll_down(self):
        if self.pminrow < self.pad.getyx()[0]:
            self.pminrow += 1

    def scroll_up(self):
        if self.pminrow > 0:
            self.pminrow -= 1

    def page_down(self):
        self.scroll_down()
        for i in range(self.ssize[0]):
            self.scroll_down()
    
    def page_up(self):
        for i in range(self.ssize[0]):
            self.scroll_up()

    def put_key(self, key):
        if key == 525: # ALT + SHIFT + DOWN
            self.scroll_down()
        elif key == 545: # ALT + SHIFT + LEFT
            self.page_up()
        elif key == 560: # ALT + SHIFT + RIGHT
            self.page_down()
        elif key == 566: # ALT + SHIFT + UP
            self.scroll_up()
        elif super().put_key(key):
            self._update_pminrow()
            pass
        else:
            return False
        return True
    
