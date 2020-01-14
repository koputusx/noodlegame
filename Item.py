import settings
import message
import color
from actions import get_equipped_in_slot
from component import *

class Item(Component):
    def __init__(self, description=None, count=1, use_function=None):
        self.description = description
        self.use_function = use_function
        self.count = count
    
    def can_combine(self, other):
        #returns true if other can stack with self
        return other.item and other.name == self.owner.name
