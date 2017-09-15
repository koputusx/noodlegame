import libtcodpy as libtcod
import textwrap
from constants import *

class ExplicitMessage(object):
    def __init__(self, message, colour, count):
        self.message = message
        self.colour = colour
        self.count = count

    def can_merge(self, other):
        return (self.message == other.message and
                self.colour == other.colour and
                self.count + other.count < 10)

def init():
    global game_messages

    #list of all game messages, starts empty
    game_messages = []

def message(new_msg, colour=libtcod.white):
    #Add a colored string to the end of the log;
    #does wordwrap at MSG_WIDTH-5 characters
    #since a count e.g. " (x3)" can add up to 5.
    global game_messages
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH-5)

    for line in new_msg_lines:
        #if the buffer is full remove first line to make room for more
        if len(game_messages) == MSG_LIMIT:
            del game_messages[0]
        new_message = ExplicitMessage(line, colour, 1)
        if game_messages and game_messages[-1].can_merge(new_message):
            game_messages[-1].count += 1
            return
        game_messages.append(new_message)