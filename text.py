
class TextBox:
    def __init__(self):
        self.s: str = ''
        self.i: int = 0

    def clear(self):
        self.s = ''
        self.i = 0

    def is_newline(self, i):
        return i == self.up_most() - 1 or i == self.down_most() or self.s[i] == '\n'

    def left(self, i):
        return i - 1 if i > self.up_most() else i

    def right(self, i):
        return i + 1 if i < self.down_most() else i

    def left_most(self, i):
        while not self.is_newline(i - 1):
            i -= 1
        return i

    def right_most(self, i):
        while not self.is_newline(i):
            i += 1
        return i

    def up(self, i):
        left_most = self.left_most(i)
        up_right_most = max(left_most - 1, self.up_most())
        up_left_most = self.left_most(up_right_most)
        return min(up_right_most, i + up_left_most - left_most)

    def down(self, i):
        left_most = self.left_most(i)
        right_most = self.right_most(i)
        down_left_most = min(right_most + 1, self.down_most())
        down_right_most = self.right_most(down_left_most)
        return min(down_right_most, i + down_left_most - left_most)

    def up_most(self):
        return 0
    
    def down_most(self):
        return len(self.s)

    def remove_right(self):
        if self.i == self.down_most():
            self.move_left()
        self.s = self.s[:self.i] + self.s[self.right(self.i):]

    def remove_left(self):
        self.move_left()
        self.remove_right()

    def remove_line(self):
        right_most = self.right_most(self.i)
        self.move_left_most()
        self.move_left()
        self.s = self.s[:self.i] + self.s[right_most:]

    def move_left(self):
        self.i = self.left(self.i)

    def move_right(self):
        self.i = self.right(self.i)

    def move_up(self):
        self.i = self.up(self.i)

    def move_down(self):
        self.i = self.down(self.i)

    def move_left_most(self):
        self.i = self.left_most(self.i)

    def move_right_most(self):
        self.i = self.right_most(self.i)

    def move_up_most(self):
        self.i = self.up_most()

    def move_down_most(self):
        self.i = self.down_most()

    def insert(self, key):
        self.s = self.s[:self.i] + chr(key) + self.s[self.i:]
        self.i += 1

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

