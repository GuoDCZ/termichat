class TextEditor:
    def __init__(self):
        self.s: str = ''
        self.i: int = 0

    def _is_newline(self, i):
        return i == self._up_most() - 1 or i == self._down_most() or self.s[i] == '\n'

    def _left(self, i):
        return i - 1 if i > self._up_most() else i

    def _right(self, i):
        return i + 1 if i < self._down_most() else i

    def _left_most(self, i):
        while not self._is_newline(i - 1):
            i -= 1
        return i

    def _right_most(self, i):
        while not self._is_newline(i):
            i += 1
        return i

    def _up(self, i):
        left_most = self._left_most(i)
        up_right_most = max(left_most - 1, self._up_most())
        up_left_most = self._left_most(up_right_most)
        return min(up_right_most, i + up_left_most - left_most)

    def _down(self, i):
        left_most = self._left_most(i)
        right_most = self._right_most(i)
        down_left_most = min(right_most + 1, self._down_most())
        down_right_most = self._right_most(down_left_most)
        return min(down_right_most, i + down_left_most - left_most)

    def _up_most(self):
        return 0
    
    def _down_most(self):
        return len(self.s)

    def remove_right(self):
        if self.i == self._down_most():
            self.move_left()
        self.s = self.s[:self.i] + self.s[self._right(self.i):]

    def remove_left(self):
        if self.i != self._up_most():
            self.move_left()
            self.remove_right()

    def remove_line(self):
        right_most = self._right_most(self.i)
        self.move_left_most()
        self.move_left()
        self.s = self.s[:self.i] + self.s[right_most:]

    def move_left(self):
        self.i = self._left(self.i)

    def move_right(self):
        self.i = self._right(self.i)

    def move_up(self):
        self.i = self._up(self.i)

    def move_down(self):
        self.i = self._down(self.i)

    def move_left_most(self):
        self.i = self._left_most(self.i)

    def move_right_most(self):
        self.i = self._right_most(self.i)

    def move_up_most(self):
        self.i = self._up_most()

    def move_down_most(self):
        self.i = self._down_most()

    def insert(self, ch):
        self.s = self.s[:self.i] + chr(ch) + self.s[self.i:]
        self.i += 1

    def replace(self, ch):
        if self.i == self._down_most():
            self.insert(ch)
        else:
            self.s[self.i] = chr(ch)
