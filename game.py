from __future__ import division
from past.utils import old_div
import libtcodpy as libtcod
import settings
import color
from load_game import load_game
from play_game import play_game
from new_game import new_game
#from character_creation import char_creation
from Menu import menu
settings.init()


if __name__ == '__main__':
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        libtcod.image_blit_2x(img, 0, 0, 0)

        libtcod.console_set_default_foreground(0, color.light_yellow)
        libtcod.console_print_ex(0, old_div(settings.SCREEN_WIDTH, 2),
                                 old_div(settings.SCREEN_HEIGHT, 2) - 4,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'INFINITE CAVERNS OF NOODLES')
        libtcod.console_print_ex(0, old_div(settings.SCREEN_WIDTH, 2),
                                 settings.SCREEN_HEIGHT - 2,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'by kopu, with help of hkas, roguelike tutorial and tutmut')

        choice = menu('', ['Play a new game',
                           'Continue last game', 'Quit'], 24)

        if choice == 0:
            #char_creation()
            new_game()
            play_game()
        if choice == 1:
            try:
                load_game()
            except:
                menu('\n No saved game to load. \n', [], 24)
                continue
            play_game()
        elif choice == 2:
            break