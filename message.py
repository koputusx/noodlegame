#Global message log.
#Call message.message_init() before using.
#Retrieve (message, color) tuples from message.game_msgs[].
#Append them using message.message().


from builtins import object
import textwrap
import settings
import color


class ExplicitMessage(object):
    def __init__(self, message, color, count):
        self.message = message
        self.color = color
        self.count = count
    
    def can_merge(self, other):
        return (self.message == other.message and
                self.color == other.color and
                self.count + other.count < 10)

def message_init():
    global game_msgs

    #The list of game messages and their colors; starts empty.
    game_msgs = []

def message(new_msg, color=color.white):
    #Add a colored string to the end of the log;
    #does wordwrap at MSG_WIDTH-5 characters
    #since a count e.g. " (x3)" can add up to 5.
    global game_msgs
    new_msg_lines = textwrap.wrap(new_msg, settings.MSG_WIDTH-5)

    for line in new_msg_lines:
        #if the buffer is full remove first line to make room for more
        if len(game_msgs) == settings.MSG_HEIGHT:
            del game_msgs[0]
        new_message = ExplicitMessage(line, color, 1)
        if game_msgs and game_msgs[-1].can_merge(new_message):
            game_msgs[-1].count += 1
            return
        game_msgs.append(new_message)