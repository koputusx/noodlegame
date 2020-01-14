from __future__ import division
from builtins import str
from builtins import object
from past.utils import old_div
class Rect(object):
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.w = w
        self.h = h

    @property
    def x2(self):
        return self.x1 + self.w

    @property
    def y2(self):
        return self.y1 + self.h

    @property
    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def move(self, x, y):
        self.x1 = x
        self.y1 = y

    def move_by_center(self, x, y):
        self.x1 = x - self.w // 2
        self.y1 = y - self.h // 2

class Location(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.x == other.x and self.y == other.y)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return Location(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Location(self.x - other.x, self.y - other.y)

    def set(self, x, y):
        self.x = x
        self.y = y

    def bound(self, rect):
        if (self.x > rect.x2):
            self.x = rect.x2
        if (self.y > rect.y2):
            self.y = rect.y2
        if (self.x < rect.x1):
            self.x = rect.x1
        if (self.y < rect.y1):
            self.y = rect.y1

    def to_string(self):
        return str(self.x) + ', ' + str(self.y)