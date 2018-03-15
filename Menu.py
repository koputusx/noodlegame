import libtcodpy as libtcod
import settings
import color


def menu(header, options, width):

    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options')

    header_height = libtcod.console_get_height_rect(settings.con, 0, 0, width,
                                                    settings.SCREEN_HEIGHT,
                                                    header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
    
    window = libtcod.console_new(width, height)
    
    libtcod.console_set_default_foreground(window, color.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, header)
                                  
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, text)
        y += 1
        letter_index += 1
        
    x = settings.SCREEN_WIDTH / 2 - width / 2
    y = settings.SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
    
    #compute x and y offsets to convert console position to menu position
    #x_offset = x #x is the left edge of the menu
    #y_offset = y + header_height #subtract the height of the header from the top edge of the menu
    
    #while True:
        #present the root console to the player and check for input
        #libtcod.console_flush()
        #libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, settings.key, settings.mouse)
        
        #if (settings.mouse.lbutton_pressed):
            #(menu_x, menu_y) = (settings.mouse.cx - x_offset, settings.mouse.cy - y_offset)
            #check if click is within the menu and on a choice
            #if menu_x >= 0 and menu_x < width and menu_y >= 0 and menu_y < height - header_height:
                #return menu_y
            
        #if settings.mouse.rbutton_pressed or settings.key.vk == libtcod.KEY_ESCAPE:
            #return None #cancel if the player right-clicked or pressed Escape
            
        #if settings.key.vk == libtcod.KEY_ENTER and key.lalt:
            #alt+enrter toggles fullscreen
            #libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
            
        #convert the ASCII code to an index: if it corresponds to an option, return it
        #index = settings.key.c - ord('a')
        #if index >= 0 and index < len(options):
            #return index
        #if they pressed a leter that is not an option, return None
        #if index >= 0 and index <= 26:
            #return None


    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def menu_item_add(menu,text):
    menu.append(text)
    return len(menu)-1
    
def optional_menu_item_add(menu,text,test):
    if (test):
        return menu_item_add(menu,text)
    else:
        return -1