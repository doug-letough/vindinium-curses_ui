#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import curses.panel
import curses.textpad
import re
import urlparse
import os

# Minimal terminal size
MIN_LINES = 48
MIN_COLS = 150


class tui:
    """The Terminal User Interface for Vindimium bot"""
    def __init__(self):
        self.running = True
        self.paused = False
        self.DATA_Y = 1
        self.DATA_X = 0
        self.DATA_H = 29
        self.DATA_W = 32
        self.PLAYERS_Y = 1
        self.PLAYERS_X = self.DATA_X + self.DATA_W + 2
        self.PLAYERS_H = 21
        self.PLAYERS_W = 66
        self.MAP_Y = 1
        self.MAP_X = self.PLAYERS_X + self.PLAYERS_W + 2
        self.MAP_H = 0
        self.MAP_W = 0
        self.PATH_Y = self.PLAYERS_Y + self.PLAYERS_H + 3
        self.PATH_X = self.DATA_X + self.DATA_W + 2
        self.PATH_H = 5
        self.PATH_W = 66
        self.LOG_Y = self.DATA_Y + self.DATA_H + 2
        self.LOG_X = 0
        self.LOG_H = 12
        self.LOG_W = self.DATA_W + self.PLAYERS_W + 2
        self.HELP_Y = self.LOG_Y + self.LOG_H - 2
        self.HELP_X = 1
        self.HELP_H = 1
        self.HELP_W = self.LOG_W - 2
        self.TIME_Y = self.LOG_Y + self.LOG_H + 2
        self.TIME_X = 0
        self.TIME_H = 0
        self.TIME_W = 0
        self.MENU_Y = 0
        self.MENU_X = 0
        self.MENU_H = 24
        self.MENU_W = 0
        self.SUMMARY_Y = self.LOG_Y + 5
        self.SUMMARY_X = self.LOG_X + self.LOG_W + 2
        self.SUMMARY_H = 7
        self.SUMMARY_W = 20
        self.data_win = None
        self.map_win = None
        self.path_win = None
        self.log_win = None
        self.help_win = None
        self.players_win = None
        self.time_win = None
        self.menu_win = None
        self.time_win = None
        self.summary_win = None
        self.log_entries = []
        self.stdscr = curses.initscr()
        curses.start_color()
        # Basic color set
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        # check for minimal screen size
        screen_y, screen_x = self.stdscr.getmaxyx()
        if screen_y < MIN_LINES or screen_x < MIN_COLS:
            # Try resizing terminal
            curses.resizeterm(MIN_LINES, MIN_COLS)
            if not curses.is_term_resized(MIN_LINES, MIN_COLS):
                self.quit_ui()
                print "Unable to change your terminal size. Your terminal must be at least", \
                        MIN_LINES, "lines and", MIN_COLS, "columns and it actually has", \
                        screen_y, "lines and", screen_x, "columns."
                quit(1)
        # Screen is up
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)
        # - /screen init ----

# - /init ---------------------------------------------------------------

    def clear(self):
        """Refresh all windows"""
        self.stdscr.erase()
        if self.data_win:
            self.data_win.erase()
        if self.map_win:
            self.map_win.erase()
        if self.path_win:
            self.path_win.erase()
        if self.log_win:
            self.log_win.erase()
        if self.help_win:
            self.help_win.erase()
        if self.players_win:
            self.players_win.erase()
        if self.time_win:
            self.time_win.erase()
        if self.summary_win:
            self.summary_win.erase()
        if self.menu_win:
            self.menu_win.erase()
        curses.doupdate()

    def refresh(self):
        """Refresh all windows"""
        self.stdscr.addstr(self.DATA_Y - 1, self.DATA_X + 1, "Game", curses.A_BOLD)
        self.stdscr.addstr(self.PLAYERS_Y - 1, self.PLAYERS_X + 1, "Players", curses.A_BOLD)
        self.stdscr.addstr(self.SUMMARY_Y - 1, self.SUMMARY_X + 1, "Games summary", curses.A_BOLD)
        self.stdscr.noutrefresh()
        self.data_win.noutrefresh()
        if self.map_win:
            self.map_win.noutrefresh()
        if self.path_win:
            self.path_win.noutrefresh()
        if self.log_win:
            self.log_win.noutrefresh()
        if self.help_win:
            self.help_win.noutrefresh()
        if self.players_win:
            self.players_win.noutrefresh()
        if self.time_win:
            self.time_win.noutrefresh()
        if self.summary_win:
            self.summary_win.noutrefresh()
        if self.menu_win:
            self.menu_win.noutrefresh()
        curses.doupdate()


# - Draw game windows --------------------------------------------------

    def draw_game_windows(self):
        """Draw the windows needed for the game"""
        if self.menu_win:
            self.menu_win.erase()
        self.draw_data_win()
        self.draw_path_win()
        self.draw_log_win()
        self.draw_help_win()
        self.draw_players_win()
        self.draw_summary_win()
        curses.panel.update_panels()
        curses.doupdate()

    def draw_data_win(self):
        """Draw main data window"""
        self.data_win = curses.newwin(self.DATA_H, self.DATA_W, self.DATA_Y, self.DATA_X)
        self.data_win.box()
        self.data_pan = curses.panel.new_panel(self.data_win)
        self.stdscr.addstr(self.DATA_Y - 1, self.DATA_X + 1, "Game", curses.A_BOLD)
        data_lines = ["Playing",
                        "Bot name",
                        "Elo",
                        "Elapsed time",
                        "Turn",
                        "Position",
                        "Life",
                        "Mine count",
                        "Gold",
                        "Move",
                        "Action",
                        "Nearest hero",
                        "Nearest bar",
                        "Nearest mine"]
        self.data_win.vline(1, 13, curses.ACS_VLINE, self.DATA_H)
        self.data_win.addch(0, 13, curses.ACS_TTEE)
        self.data_win.addch(self.DATA_H-1, 13, curses.ACS_BTEE)
        self.data_win.vline(9, 22, curses.ACS_VLINE, self.DATA_H-9)
        self.data_win.addch(self.DATA_H-1, 22, curses.ACS_BTEE)
        y = 0
        for line in data_lines:
            self.data_win.addstr(y + 1, 1, line, curses.A_BOLD)
            if y < len(data_lines) * 2 - 2:
                self.data_win.hline(y + 2, 1, curses.ACS_HLINE, 30)
                self.data_win.addch(y + 2, 0, curses.ACS_LTEE)
                self.data_win.addch(y + 2, 31, curses.ACS_RTEE)
                self.data_win.addch(y + 2, 13, curses.ACS_PLUS)
                if y * 2 - 7 > 7:
                    self.data_win.addch(y + 2, 22, curses.ACS_PLUS)
            y += 2
        self.data_win.addch(8, 22, curses.ACS_TTEE)

    def draw_log_win(self):
        """Draw log window"""
        self.stdscr.addstr(self.LOG_Y - 1, self.LOG_X + 1, "Log", curses.A_BOLD)
        self.log_win = curses.newwin(self.LOG_H, self.LOG_W, self.LOG_Y, self.LOG_X)
        self.log_win.box()
        self.log_pan = curses.panel.new_panel(self.log_win)

    def draw_path_win(self):
        """Draw path & heuristic window"""
        self.stdscr.addstr(self.PATH_Y - 1, self.PATH_X + 1, "Path and heuristic", curses.A_BOLD)
        self.path_win = curses.newwin(self.PATH_H, self.PATH_W, self.PATH_Y, self.PATH_X)
        self.path_win.box()
        self.path_pan = curses.panel.new_panel(self.path_win)
        self.path_win.addstr(1, 1, "Heuristic", curses.A_BOLD)
        self.path_win.addstr(3, 1, "Path to goal", curses.A_BOLD)
        self.path_win.hline(2, 1, curses.ACS_HLINE, 64)
        self.path_win.vline(1, 13, curses.ACS_VLINE, 4)
        self.path_win.addch(2, 0, curses.ACS_LTEE)
        self.path_win.addch(2, 65, curses.ACS_RTEE)
        self.path_win.addch(0, 13, curses.ACS_TTEE)
        self.path_win.addch(2, 13, curses.ACS_PLUS)
        self.path_win.addch(4, 13, curses.ACS_BTEE)

    def draw_help_win(self):
        """Draw help window"""
        self.help_win = curses.newwin(self.HELP_H, self.HELP_W, self.HELP_Y, self.HELP_X)
        self.help_pan = curses.panel.new_panel(self.help_win)
        self.help_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        self.help_win.addstr(0, 1, "Q", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 2, "uit")
        self.help_win.addstr(0, 8, "P", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 9, "ause")
        self.help_win.addstr(0, 16, "S", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 17, "ave")

    def draw_players_win(self):
        """Draw players window"""
        self.stdscr.addstr(self.PLAYERS_Y - 1, self.PLAYERS_X + 1, "Players", curses.A_BOLD)
        self.players_win = curses.newwin(self.PLAYERS_H, self.PLAYERS_W, self.PLAYERS_Y, self.PLAYERS_X)
        self.players_win.box()
        self.players_pan = curses.panel.new_panel(self.players_win)
        players_lines = ["Name",
                        "User ID",
                        "Bot ID",
                        "Elo",
                        "Position",
                        "Life",
                        "Mine count",
                        "Gold",
                        "Spawn pos",
                        "Crashed"]

        self.players_win.vline(1, 11, curses.ACS_VLINE, self.PLAYERS_H-2)
        self.players_win.vline(1, 29, curses.ACS_VLINE, self.PLAYERS_H-2)
        self.players_win.vline(1, 47, curses.ACS_VLINE, self.PLAYERS_H-2)
        self.players_win.addch(0, 11, curses.ACS_TTEE)
        self.players_win.addch(0, 29, curses.ACS_TTEE)
        self.players_win.addch(0, 47, curses.ACS_TTEE)
        self.players_win.addch(self.PLAYERS_H-1, 11, curses.ACS_BTEE)
        self.players_win.addch(self.PLAYERS_H-1, 29, curses.ACS_BTEE)
        self.players_win.addch(self.PLAYERS_H-1, 47, curses.ACS_BTEE)
        y = 0
        for line in players_lines:
            self.players_win.addstr(y+1, 1, line, curses.A_BOLD)
            if y < len(players_lines)*2 - 2:
                self.players_win.hline(y + 2, 1, curses.ACS_HLINE, self.PLAYERS_W - 2)
                self.players_win.addch(y + 2, 0, curses.ACS_LTEE)
                self.players_win.addch(y + 2, 11, curses.ACS_PLUS)
                self.players_win.addch(y + 2, 29, curses.ACS_PLUS)
                self.players_win.addch(y + 2, 47, curses.ACS_PLUS)
                self.players_win.addch(y + 2, self.PLAYERS_W-1, curses.ACS_RTEE)
            y += 2

    def draw_time_win(self):
        """Draw time line"""
        self.TIME_W = self.LOG_W + self.MAP_W + 4
        self.stdscr.addstr(self.TIME_Y - 1, self.TIME_X + 1, "Time line", curses.A_BOLD)
        self.time_win = curses.newwin(3, self.TIME_W, self.TIME_Y, self.TIME_X)
        self.time_pan = curses.panel.new_panel(self.time_win)
        self.time_win.box()
        self.time_win.addstr(1, 1, " ", curses.color_pair(4) + curses.A_REVERSE)

    def draw_summary_win(self):
        """Draw sumary window"""
        self.stdscr.addstr(self.SUMMARY_Y - 1, self.SUMMARY_X + 1, "Games summary", curses.A_BOLD)
        self.summary_win = curses.newwin(self.SUMMARY_H, self.SUMMARY_W, self.SUMMARY_Y, self.SUMMARY_X)
        self.summary_pan = curses.panel.new_panel(self.summary_win)
        self.summary_win.box()
        self.summary_win.vline(1, 10, curses.ACS_VLINE, self.SUMMARY_H - 2)
        self.summary_win.addch(0, 10, curses.ACS_TTEE)
        self.summary_win.addch(self.SUMMARY_H - 1, 10, curses.ACS_BTEE)
        for i in range(2, self.SUMMARY_H - 1, 2):
            self.summary_win.hline(i, 1, curses.ACS_HLINE, self.SUMMARY_W - 2)
            self.summary_win.addch(i, 0, curses.ACS_LTEE)
            self.summary_win.addch(i, 10, curses.ACS_PLUS)
            self.summary_win.addch(i, self.SUMMARY_W - 1, curses.ACS_RTEE)
        self.summary_win.addstr(1, 1, "Played", curses.A_BOLD)
        self.summary_win.addstr(3, 1, "Won", curses.A_BOLD)
        self.summary_win.addstr(5, 1, "Timed out", curses.A_BOLD)

# MAP ------------------------------------------------------------------

    def draw_map(self, board_map, path, heroes):
        """Draw the map"""
        board_size = len(board_map)
        self.MAP_H = board_size
        self.MAP_W = board_size
        self.stdscr.addstr(self.MAP_Y - 1, self.MAP_X + 1, "Map ("+str(board_size)+"X"+str(board_size)+")", curses.A_BOLD)
        self.stdscr.noutrefresh()
        if self.map_win:
            x, y = self.map_win.getmaxyx()
            if x != board_size + 2 or y != board_size + 2:
                # resize the window as needed
                self.map_win.erase()
                curses.panel.update_panels()
                self.map_win.resize(board_size + 2, board_size + 2)
                # Time line (Cost cpu time)
                self.draw_time_win()
                self.map_win.noutrefresh()
            else:
                self.map_win.erase()
                self.map_win.noutrefresh()
        else:
            # map doesn't exist
            self.map_win = curses.newwin(board_size + 2, board_size + 2, self.MAP_Y, self.MAP_X)
            self.map_pan = curses.panel.new_panel(self.map_win)
            # Time line (Cost cpu time)
            self.draw_time_win()
            curses.panel.update_panels()
        self.map_win.box()
        # highlight choosen path
        if path is None:
            path = []
        for cell in path:
            self.map_win.addch(cell[0]+1, cell[1] + 1, curses.ACS_BULLET, curses.color_pair(3) + curses.A_BOLD)
        # Draw map content
        y = 0
        for line in board_map:
            x = 0
            for char in line:
                attr = 0
                if char == "#":
                    attr = 0
                    char = curses.ACS_CKBOARD
                elif char == "$":
                    attr = curses.A_BOLD + curses.color_pair(4)
                elif char == "T":
                    attr = curses.A_BOLD + curses.color_pair(5)
                elif char == "H":
                    # default bot color is BLUE
                    attr = curses.A_BOLD + curses.color_pair(6)
                    for hero in heroes:
                        # Select color for bot (cost cpu time)
                        if hero.pos == (y, x):
                            if hero.bot_id == 1:
                                attr = curses.A_BOLD + curses.color_pair(6)
                            elif hero.bot_id == 2:
                                attr = curses.A_BOLD + curses.color_pair(8)
                            elif hero.bot_id == 3:
                                attr = curses.A_BOLD + curses.color_pair(9)
                            elif hero.bot_id == 4:
                                attr = curses.A_BOLD + curses.color_pair(10)
                elif char == "@":
                    attr = curses.A_BOLD + curses.color_pair(2)
                elif char == "X":
                    attr = curses.A_BOLD + curses.color_pair(7)
                if not (char == " " and (y, x in path)):
                    self.map_win.addch(y + 1, x + 1, char, attr)
                x = x + 1
            y = y + 1


# / Draw window --------------------------------------------------------

# Diplay functions -----------------------------------------------------

    # Following methods are used to display data at
    # the good place. Names are explicit.

    def display_heroes(self, heroes, bot_id):
        x = 12
        gold_winner = ""
        max_gold = 0
        gold_pos = 0
        mine_winner = ""
        max_mine = 0
        mine_pos = 0
        for hero in heroes:
            if hero.bot_id != bot_id:
                for i in range(1, 21, 2):
                    # Clear player tab
                    self.players_win.hline(i, x, " ", 17)
                if hero.bot_id == 1:
                    attr = curses.A_BOLD + curses.color_pair(6)
                elif hero.bot_id == 2:
                    attr = curses.A_BOLD + curses.color_pair(8)
                elif hero.bot_id == 3:
                    attr = curses.A_BOLD + curses.color_pair(9)
                elif hero.bot_id == 4:
                    attr = curses.A_BOLD + curses.color_pair(10)
                self.players_win.addstr(1, x, str(hero.name[0:17]), attr)
                self.players_win.addstr(3, x, str(hero.user_id))
                self.players_win.addstr(5, x, str(hero.bot_id))
                self.players_win.addstr(7, x, str(hero.elo))
                self.players_win.addstr(9, x, str(hero.pos))
                self.players_win.addstr(11, x, str(hero.life))
                self.players_win.addstr(13, x, str(hero.mine_count))
                self.players_win.addstr(15, x, str(hero.gold))
                self.players_win.addstr(17, x, str(hero.spawn_pos))
                self.players_win.addstr(19, x, str(hero.crashed))
                x += 18 #  player horizontal offset
            if int(hero.gold) > max_gold:
                max_gold = int(hero.gold)
                gold_winner =  str(hero.bot_id)
                gold_pos = x - 2
            if int(hero.mine_count) > max_mine:
                max_mine = int(hero.mine_count)
                mine_winner = str(hero.bot_id)
                mine_pos = x - 2
        if gold_winner == str(bot_id):
            self.data_win.addstr(17, 21, "$", curses.A_BOLD + curses.color_pair(4))
        elif gold_pos > 0:
            self.players_win.addstr(15, gold_pos, "$", curses.A_BOLD + curses.color_pair(4))
        if mine_winner == str(bot_id):
            self.data_win.addstr(15, 21, "*", curses.A_BOLD + curses.color_pair(4))
        elif mine_pos > 0:
            self.players_win.addstr(13, mine_pos, "*", curses.A_BOLD + curses.color_pair(4))

    def display_url(self, url):
        url = url[url.rfind("/")+1:]
        self.data_win.addstr(1, 14, str(url))

    def display_bot_name(self, name):
        self.data_win.addstr(3, 14, str(name[0:15]))

    def display_turn(self, turn, max_turns):
        self.clear_data_cell((9, 14), 8)
        self.clear_data_cell((9, 23), 8)
        self.data_win.addstr(9, 23, str(turn)+"/"+str(max_turns), curses.A_BOLD)
        self.data_win.addstr(9, 14, str(turn+1)+"/"+str(max_turns), curses.A_BOLD)

    def display_elapsed(self, elapsed):
        self.clear_data_cell((7, 14), 17)
        attr = 0
        if elapsed > 0.5:
            attr = curses.color_pair(3) + curses.A_BOLD
        self.data_win.addstr(7, 20, str(elapsed), attr)

    def display_pos(self, pos):
        self.clear_data_cell((11, 14), 8)
        self.data_win.addstr(11, 14, str(pos))

    def display_last_pos(self, pos):
        self.clear_data_cell((11, 23), 8)
        self.data_win.addstr(11, 23, str(pos))

    def display_action(self, action):
        attr = 0
        if action == "wait":
            # Display "wait" in bold red
            attr = attr = curses.color_pair(3) + curses.A_BOLD
        self.clear_data_cell((21, 14), 8)
        self.data_win.addstr(21, 14, str(action), attr)

    def display_last_action(self, action):
        attr = 0
        if action == "wait":
            # Display "wait" in bold red
            attr = attr = curses.color_pair(3) + curses.A_BOLD
        self.clear_data_cell((21, 14), 8)
        self.clear_data_cell((21, 23), 8)
        self.data_win.addstr(21, 23, str(action), attr)

    def display_move(self, move):
        attr = 0
        if move == "Stay":
            # Display "Stay" in bold red
            attr = attr = curses.color_pair(3) + curses.A_BOLD
        self.clear_data_cell((19, 14), 8)
        self.data_win.addstr(19, 14, str(move))

    def display_last_move(self, move):
        attr = 0
        if move == "Stay":
            # Display "Stay" in bold red
            attr = attr = curses.color_pair(3) + curses.A_BOLD
        self.clear_data_cell((19, 23), 8)
        self.data_win.addstr(19, 23, str(move))

    def display_life(self, life):
        self.clear_data_cell((13, 14), 8)
        attr = 0
        if life < 20:
            attr = curses.color_pair(3) + curses.A_BOLD
        self.data_win.addstr(13, 14, str(life), attr)

    def display_last_life(self, life):
        self.clear_data_cell((13, 23), 8)
        attr = 0
        if life < 20:
            attr = curses.color_pair(3) + curses.A_BOLD
        self.data_win.addstr(13, 23, str(life), attr)

    def display_mine_count(self, mine_count):
        self.clear_data_cell((15, 14), 8)
        attr = 0
        if mine_count[0] == "0":
            attr = curses.color_pair(3) + curses.A_BOLD
        self.data_win.addstr(15, 14, str(mine_count), attr)

    def display_last_mine_count(self, mine_count):
        self.clear_data_cell((15, 23), 8)
        attr = 0
        if mine_count[0] == "0":
            attr = curses.color_pair(3) + curses.A_BOLD
        self.data_win.addstr(15, 23, str(mine_count), attr)

    def display_gold(self, gold):
        self.clear_data_cell((17, 14), 8)
        self.data_win.addstr(17, 14, str(gold))

    def display_last_gold(self, gold):
        self.clear_data_cell((17, 23), 8)
        self.data_win.addstr(17, 23, str(gold))

    def display_elo(self, elo):
        self.data_win.addstr(5, 20, str(elo))

    def display_nearest_mine(self, mine):
        self.clear_data_cell((27, 14), 8)
        self.data_win.addstr(27, 14, str(mine))

    def display_last_nearest_mine(self, mine):
        self.clear_data_cell((27, 23), 8)
        self.data_win.addstr(27, 23, str(mine))

    def display_nearest_tavern(self, tavern):
        self.clear_data_cell((25, 14), 8)
        self.data_win.addstr(25, 14, str(tavern))

    def display_last_nearest_tavern(self, tavern):
        self.clear_data_cell((25, 23), 8)
        self.data_win.addstr(25, 23, str(tavern))

    def display_nearest_hero(self, hero):
        self.clear_data_cell((23, 14), 8)
        self.data_win.addstr(23, 14, str(hero))

    def display_last_nearest_hero(self, hero):
        self.clear_data_cell((23, 23), 8)
        self.data_win.addstr(23, 23, str(hero))

    def display_decision(self, decision):
        self.path_win.hline(1, 14, " ", 51)
        d = ""
        for h in decision:
            d += str(h[0])+": "+str(h[1])+" | "
        self.path_win.addstr(1, 14, d)

    def display_summary(self, played, won, timed_out):
        data = ['', played, '', won, '', timed_out]
        for i in range(1, 7, 2):
            self.summary_win.hline(i, 11, " ", 8)
            self.summary_win.addstr(i, 11, data[i])

    def display_path(self, path):
        self.path_win.hline(3, 14, " ", 51)
        path = str(path).strip('[').strip(']')[0:48]+"..."
        self.path_win.addstr(3, 14, path)

    def clear_data_cell(self, pos, length):
        self.data_win.hline(pos[0], pos[1], " ", length)

# TIME CURSOR ----------------------------------------------------------

    def move_time_cursor(self, pos):
        self.time_win.box()
        self.time_win.hline(1, 1, curses.ACS_BLOCK, self.TIME_W - 2)
        if pos < 1:
            pos = 1
        if pos > self.TIME_W - 2:
            pos = self.TIME_W - 2
        if pos > 1:
            self.time_win.addch(0, pos - 1, curses.ACS_TTEE)
            self.time_win.addch(1, pos - 1, curses.ACS_VLINE)
            self.time_win.addch(2, pos - 1, curses.ACS_BTEE)
        if pos < self.TIME_W - 2:
            self.time_win.addch(0, pos + 1, curses.ACS_TTEE)
            self.time_win.addch(1, pos + 1, curses.ACS_VLINE)
            self.time_win.addch(2, pos + 1, curses.ACS_BTEE)
        self.time_win.addstr(1, pos, " ", curses.color_pair(4) + curses.A_REVERSE)


# LOG ------------------------------------------------------------------

    def append_log(self, data):
        """Append log with new data """
        for i in range(0, len(str(data)), self.LOG_W - 2):
            """Cut string to parts with appropriate length"""
            self.log_entries.append(str(data)[i:i+self.LOG_W - 2])
        self.purge_log()
        self.display_log()

    def purge_log(self):
        """Purge log of oldest entries"""
        diff = len(self.log_entries) - (self.LOG_H - self.HELP_H - 2)
        if diff > 0:
            self.log_entries = self.log_entries[diff - 1:len(self.log_entries)]

    def display_log(self):
        """Display log entries"""
        if self.log_win:
            for i in range(1, self.LOG_H - 2):
                self.log_win.hline(i, 1, " ", self.LOG_W - 2)
                try:
                    attr = 0
                    regexp = re.compile('Error')
                    if regexp.search(self.log_entries[i]) is not None:
                        attr = curses.color_pair(3) + curses.A_BOLD
                    self.log_win.addstr(i, 1, self.log_entries[i], attr)
                except IndexError:
                    # No more entries in log_entries
                    pass
                except Exception as e:
                    self.quit_ui()
                    print e
                    print "Error at display_log. i=", i, \
                            "log entry:", self.log_entries[i], \
                            "attr:", attr, \
                            "LOG_H:", self.LOG_H
                    quit(1)
# Setup windows --------------------------------------------------------
    def ask_action(self):
        """Return the inputed value"""
        k = self.menu_win.getkey()
        return k

    def is_int(self, num):
        """Return True if num is int and if num > 0
        Print error message and return false otherwise"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        if num is not None:
            try:
                num = int(str(num).strip(chr(0)))
                if num > 0:
                    return True
            except (ValueError, TypeError):
                self.menu_win.addstr(15, offset + 7, "Please, input an integer greater than 0.", curses.color_pair(3))
                self.menu_win.refresh()
        return False

    def check_input(self, char):
        """Manage backspace input"""
        if char < 256:
            if char == 127:
                # manage backspace
                self.del_char()
        return char

    def del_char(self):
        """With the self.input_win,
        delete the previous char and move cursor back"""
        y, x = self.input_win.getyx()
        if x > 0:
            self.input_win.delch(y, x - 1)
            self.input_win.move(y, x - 1)

    def check_url(self, url):
        """Return True if url is a valid url"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        url = url.strip(chr(0)).strip()
        if len(url) > 0:
            # text_box.edit return a null char at start:(
            check = urlparse.urlparse(url)
            if len(check.scheme) > 0 and len(check.netloc) > 0:
                return True
            self.menu_win.addstr(15, offset + 12, "Please, input a valid URL.", curses.color_pair(3))
            self.menu_win.refresh()
        return False

    def check_file_url(self, url):
        """Return True if url is a valid url with 'file path'"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        url = url.strip(chr(0)).strip()
        if len(url) > 0:
            # text_box.edit return a null char at start:(
            check = urlparse.urlparse(url)
            if len(check.scheme) > 0 and \
                    len(check.netloc) > 0 and \
                    len(check.path) > 0:
                return True
            self.menu_win.addstr(15, offset + 12, "Please, input a valid URL.", curses.color_pair(3))
            self.menu_win.refresh()
        return False

    def check_file_path(self, path):
        """Return True if path is an existant file name"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        path = path.strip(chr(0)).strip()
        if len(path) > 0:
            # text_box.edit return a null char at start
            if os.path.exists(path):
                return True
            self.menu_win.addstr(15, offset + 12, "Please, input a valid path.", curses.color_pair(3))
            self.menu_win.refresh()
        return False

    def check_key(self, player_key):
        """Check the player key format"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x / 2 - 25
        player_key = player_key.strip(chr(0)).strip()
        if len(player_key) > 0:
            pattern = "^([0-9]|[a-z]){8}"
            f = re.search(pattern, player_key)
            try:
                if len(f.group(0)) == 8 and len(player_key) == 8:
                    return True
            except (TypeError, AttributeError):
                pass
            self.menu_win.addstr(15, offset + 12, "Please, input a a valid key.", curses.color_pair(3))
            self.menu_win.refresh()
        return False

    def draw_banner(self):
        """Draw the Vindinium banner on self.menu_win"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        self.menu_win.clear()
        self.menu_win.box()
        self.menu_pan = curses.panel.new_panel(self.menu_win)
        title1 = "__     ___           _ _       _"
        title2 = "\ \   / (_)_ __   __| (_)_ __ (_)_   _ _ __ ___"
        title3 = " \ \ / /| | '_ \ / _` | | '_ \| | | | | '_ ` _ \\"
        title4 = "  \ V / | | | | | (_| | | | | | | |_| | | | | | |"
        title5 = "   \_/  |_|_| |_|\__,_|_|_| |_|_|\__,_|_| |_| |_|"
        self.menu_win.addstr(1, offset, title1, curses.A_BOLD + curses.color_pair(4))
        self.menu_win.addstr(2, offset, title2, curses.A_BOLD + curses.color_pair(4))
        self.menu_win.addstr(3, offset, title3, curses.A_BOLD + curses.color_pair(4))
        self.menu_win.addstr(4, offset, title4, curses.A_BOLD + curses.color_pair(4))
        self.menu_win.addstr(5, offset, title5, curses.A_BOLD + curses.color_pair(4))
        self.menu_win.addstr(7, offset + 8, "Welcome to the Vindinium curses client", curses.A_BOLD + curses.A_UNDERLINE)

    def ask_main_menu(self):
        """Display main menu window and ask for choice"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        choice = "0"
        options = ["1", "2", "3", "4", "5"]
        self.menu_win = curses.newwin(self.MENU_H, self.MENU_W, self.MENU_Y, self.MENU_X)
        self.draw_banner()
        self.menu_win.addstr(9, offset + 8, "Please, choose an option:", curses.A_BOLD)
        self.menu_win.addstr(11, offset + 10, "1", curses.A_BOLD)
        self.menu_win.addstr(11, offset + 12, "- Play game")
        self.menu_win.addstr(13, offset + 10, "2", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 12, "- Setup game")
        self.menu_win.addstr(15, offset + 10, "3", curses.A_BOLD)
        self.menu_win.addstr(15, offset + 12, "- Load game from file")
        self.menu_win.addstr(17, offset + 10, "4", curses.A_BOLD)
        self.menu_win.addstr(17, offset + 12, "- Load game from URL")
        self.menu_win.addstr(19, offset + 10, "5", curses.A_BOLD)
        self.menu_win.addstr(19, offset + 12, "- Quit")
        while choice not in options:
            choice = self.ask_action()
        return choice

    def ask_game_mode(self):
        """Display game mode menu and ask for choice"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        choice = "0"
        options = ["1", "2"]
        self.draw_banner()
        self.menu_win.addstr(9, offset - 15, "Please, choose a game mode:", curses.A_BOLD)
        self.menu_win.addstr(11, offset - 15, "1", curses.A_BOLD)
        self.menu_win.addstr(11, offset - 13, "- Arena mode:", curses.A_BOLD)
        self.menu_win.addstr(12, offset - 11, "In this mode you will fight against 3 heroes as greedy and thirsty as you are.")
        self.menu_win.addstr(13, offset - 11, "There can be only one !")
        self.menu_win.addstr(15, offset - 15, "2", curses.A_BOLD)
        self.menu_win.addstr(15, offset - 13, "- Training mode:", curses.A_BOLD)
        self.menu_win.addstr(16, offset - 11, "In this mode you will fight against 3 dummy heroes as useless and stupid as yo^W random A.I bots are.")
        self.menu_win.addstr(17, offset - 11, "Thus, you will earn no glory, no fame nor shame. Your Elo score will not be impacted by your victories or defeats.")
        while choice not in options:
            choice = self.ask_action()
        return choice

    def ask_number_games(self):
        """Ask for number_of_games"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        num_game = None
        self.draw_banner()
        self.menu_win.addstr(10, offset + 19, "ARENA MODE", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 8, "Number of games to play:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 33, 14, offset + 42)
        self.input_win = self.menu_win.subwin(1, 8, 13, offset + 34)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.is_int(num_game):
            curses.curs_set(1)
            num_game = text_box.edit(self.check_input)
            curses.curs_set(0)
        return int(str(num_game).strip(chr(0)).strip())

    def ask_number_turns(self):
        """Ask for number_of_turns"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        num_turns = None
        self.draw_banner()
        self.menu_win.addstr(10, offset + 17, "TRAINING MODE", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 8, "Number of turns:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 25, 14, offset + 34)
        self.input_win = self.menu_win.subwin(1, 8, 13, offset + 26)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.is_int(num_turns):
            curses.curs_set(1)
            num_turns = text_box.edit(self.check_input)
            curses.curs_set(0)
        return int(str(num_turns).strip(chr(0)).strip())

    def ask_server_url(self, game_mode):
        """Ask for server url"""
        server_url = ""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        offset_2 = 19
        self.draw_banner()
        if game_mode == "training":
            # Manage display offset according to len(game_mode)
            offset_2 = 17
        self.menu_win.addstr(10, offset + offset_2, game_mode.upper()+" MODE", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 6, "Server URL:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 18, 14, offset + 48)
        self.input_win = self.menu_win.subwin(1, 29, 13, offset + 19)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        self.input_win.addstr(0, 0, server_url)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.check_url(server_url):
            curses.curs_set(1)
            server_url = text_box.edit(self.check_input)
            curses.curs_set(0)
        return str(server_url).strip(chr(0)).strip()

    def ask_key(self, game_mode):
        """Ask for player key"""
        player_key = ""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        offset_2 = 19
        self.draw_banner()
        if game_mode == "training":
            # Manage display offset according to len(game_mode)
            offset_2 = 17
        self.menu_win.addstr(10, offset + offset_2, game_mode.upper()+" MODE", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 6, "Player key:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 18, 14, offset + 48)
        self.input_win = self.menu_win.subwin(1, 29, 13, offset + 19)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.check_key(player_key):
            curses.curs_set(1)
            player_key = text_box.edit(self.check_input)
            curses.curs_set(0)
        return str(player_key).strip(chr(0)).strip()

    def ask_game_file_url(self):
        """Ask for game file url"""
        file_url = ""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x / 2 - 25
        self.draw_banner()
        self.menu_win.addstr(13, offset - 6, "File URL:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 5, 14, offset + 55)
        self.input_win = self.menu_win.subwin(1, 49, 13, offset + 6)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        self.input_win.addstr(0, 0, file_url)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.check_file_url(file_url):
            curses.curs_set(1)
            file_url = text_box.edit(self.check_input)
            curses.curs_set(0)
        return str(file_url).strip(chr(0)).strip()

    def ask_game_file_path(self):
        """Ask for game file path"""
        file_path = ""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x / 2 - 25
        self.draw_banner()
        self.menu_win.addstr(13, offset - 6, "File path:", curses.A_BOLD)
        curses.textpad.rectangle(self.menu_win, 12, offset + 5, 14, offset + 55)
        self.input_win = self.menu_win.subwin(1, 49, 13, offset + 6)
        self.input_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)
        self.input_win.addstr(0, 0, file_path)
        input_pan = curses.panel.new_panel(self.input_win)
        text_box = curses.textpad.Textbox(self.input_win)
        text_box.stripspaces = 1
        curses.panel.update_panels()
        self.input_win.refresh()
        while not self.check_file_path(file_path):
            curses.curs_set(1)
            file_path = text_box.edit(self.check_input)
            curses.curs_set(0)
        return str(file_path).strip(chr(0)).strip()

    def ask_save_config(self):
        """Ask for config save"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        choice = "0"
        options = ["1", "2"]
        self.menu_win = curses.newwin(self.MENU_H, self.MENU_W, self.MENU_Y, self.MENU_X)
        self.draw_banner()
        self.menu_win.addstr(11, offset + 8, "Save configuration ?", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 10, "1", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 12, "- Yes")
        self.menu_win.addstr(15, offset + 10, "2", curses.A_BOLD)
        self.menu_win.addstr(15, offset + 12, "- No")
        while choice not in options:
            choice = self.ask_action()
        if choice == "1":
            return True
        return False

    def ask_play_game(self):
        """Ask for playing game"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        choice = "0"
        options = ["1", "2"]
        self.menu_win = curses.newwin(self.MENU_H, self.MENU_W, self.MENU_Y, self.MENU_X)
        self.draw_banner()
        self.menu_win.addstr(11, offset + 8, "Play game ?", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 10, "1", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 12, "- Yes")
        self.menu_win.addstr(15, offset + 10, "2", curses.A_BOLD)
        self.menu_win.addstr(15, offset + 12, "- No")
        while choice not in options:
            choice = self.ask_action()
        if choice == "1":
            return True
        return False

    def ask_map(self):
        """Display main menu window and ask for choice"""
        screen_y, screen_x = self.stdscr.getmaxyx()
        offset = screen_x/2 - 25
        choice = "0"
        options = ["1", "2", "3", "4", "5", "6"]
        self.menu_win = curses.newwin(self.MENU_H, self.MENU_W, self.MENU_Y, self.MENU_X)
        self.draw_banner()
        self.menu_win.addstr(9, offset + 8, "Please, choose a map:", curses.A_BOLD)
        self.menu_win.addstr(11, offset + 10, "1", curses.A_BOLD)
        self.menu_win.addstr(11, offset + 12, "- M1 : A 10X10 symetrical map")
        self.menu_win.addstr(13, offset + 10, "2", curses.A_BOLD)
        self.menu_win.addstr(13, offset + 12, "- M2 : A 12X12 symetrical map")
        self.menu_win.addstr(15, offset + 10, "3", curses.A_BOLD)
        self.menu_win.addstr(15, offset + 12, "- M3 : A 20X20 asymetrical map")
        self.menu_win.addstr(17, offset + 10, "4", curses.A_BOLD)
        self.menu_win.addstr(17, offset + 12, "- M4 : A 18X18 symetrical map")
        self.menu_win.addstr(19, offset + 10, "5", curses.A_BOLD)
        self.menu_win.addstr(19, offset + 12, "- M5 : A 18X18 symetrical map")
        self.menu_win.addstr(19, offset + 10, "6", curses.A_BOLD)
        self.menu_win.addstr(19, offset + 12, "- M6 : A 16X16 symetrical map")
        while choice not in options:
            choice = self.ask_action()
        return choice

# QUIT -----------------------------------------------------------------

    def ask_quit(self):
        """What don't you understand in 'press q to quit' ? ;-)"""
        keys = ["m", "s", "r"]
        self.help_win.hline(0, 1, " ", 98)
        self.help_win.addstr(0, 1, "M", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 2, "enu")
        self.help_win.addstr(0, 8, "S", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 9, "ave")
        self.help_win.addstr(0, 15, "R", curses.A_BOLD + curses.A_STANDOUT)
        self.help_win.addstr(0, 16, "eplay")
        curses.doupdate()
        key = None
        while key not in keys:
            key = self.help_win.getkey()
        return key

    def quit_ui(self):
        """Quit the UI and restore terminal state"""
        self.stdscr.clear()
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.endwin()
        self.running = False

    def pause(self):
        """Switch pause state"""
        self.paused = not self.paused
