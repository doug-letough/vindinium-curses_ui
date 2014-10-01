#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses, curses.panel
import re

# Minimal terminal size
MIN_LINES = 48
MIN_COLS = 120

class tui:
	"""The Terminal User Interface for Vindimium bot"""
	def __init__(self, scr):
		self.DATA_Y = 1
		self.DATA_X = 0
		self.DATA_H = 29
		self.DATA_W = 32

		self.MAP_Y = 0
		self.MAP_X = 0
		self.MAP_H = 0
		self.MAP_W = 0

		self.PATH_Y = self.DATA_Y + self.DATA_H + 1
		self.PATH_X = 0
		self.PATH_H = 6
		self.PATH_W = 66

		self.LOG_Y = self.PATH_Y + self.PATH_H + 1
		self.LOG_X = 0
		self.LOG_H = 12
		self.LOG_W = 66

		self.HELP_X = 0
		self.HELP_Y = self.LOG_Y + self.LOG_H - 3
		self.HELP_H = 3
		self.HELP_W = self.LOG_W

		self.PATH_Y = self.DATA_Y + self.DATA_H + 1
		self.PATH_X = 0
		self.PATH_H = 5
		self.PATH_W = 66

		self.LOG_Y = self.PATH_Y + self.PATH_H + 1
		self.LOG_X = 0
		self.LOG_H = 12
		self.LOG_W = 66

		self.HELP_X = 0
		self.HELP_Y = self.LOG_Y + self.LOG_H - 3
		self.HELP_H = 3
		self.HELP_W = self.LOG_W
		
		
		self.map_win = None
		self.path_win = None
		self.log_win = None
		self.help_win = None
		self.stdscr = scr
		self.log_entries = []
		
		curses.start_color()
		# Basic color set
		self.WBK = curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
		self.ALERT = curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
		self.RED = curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
		self.YELLOW = curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		self.GREEN = curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
		self.BLUE = curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
		self.CYAN = curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
		# check for minimal screen size
		screen_y, screen_x = self.stdscr.getmaxyx() 
		if screen_y < MIN_LINES or screen_x < MIN_COLS:
			try:
				#~ # Try resizing terminal
				curses.resizeterm(MIN_LINES, MIN_COLS)
				screen_y, screen_x = self.stdscr.getmaxyx() 
				if screen_y < MIN_LINES or screen_x < MIN_COLS:
					raise Exception()
			except Exception as e:
				self.term_error(e)
		
		# Screen is up
		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)
		self.stdscr.keypad(1)
		self.stdscr.nodelay(1)
		self.stdscr.clear()
		#- /screen init ----
		
		self.data_win = curses.newwin(self.DATA_H, self.DATA_W, self.DATA_Y, self.DATA_X)		
		self.data_win.box()
		self.stdscr.addstr(self.DATA_Y -1 , self.DATA_X +1, "Game", curses.A_BOLD)
		
		
		data_lines = ["Playing", \
						"Bot name", \
						"Elo", \
						"Elapsed time", \
						"Turn", \
						"Position", \
						"Life", \
						"Mine count", \
						"Gold", \
						"Move", \
						"Action", \
						"Nearest hero", \
						"Nearest bar", \
						"Nearest mine" ]

		self.data_win.vline(1, 13, curses.ACS_VLINE, self.DATA_H)
		self.data_win.addch(0, 13, curses.ACS_TTEE)
		self.data_win.addch(self.DATA_H-1, 13, curses.ACS_BTEE)
		
		self.data_win.vline(9, 22, curses.ACS_VLINE, self.DATA_H-9)
		self.data_win.addch(self.DATA_H-1, 22, curses.ACS_BTEE)

		y = 0			
		for line in data_lines:
				self.data_win.addstr(y+1, 1, line, curses.A_BOLD)
				if y < len(data_lines)*2 - 2:
					self.data_win.hline(y+2, 1, curses.ACS_HLINE, 30)
					self.data_win.addch(y+2, 0, curses.ACS_LTEE)
					self.data_win.addch(y+2, 31, curses.ACS_RTEE)
					self.data_win.addch(y+2, 13, curses.ACS_PLUS)
					if y*2 - 7 > 7:
						self.data_win.addch(y+2, 22, curses.ACS_PLUS)
				y += 2
		
		self.data_win.addch(8, 22, curses.ACS_TTEE)						
		self.refresh()

	def refresh(self):
		self.stdscr.refresh()
		self.data_win.refresh()
		if self.map_win:
			self.map_win.refresh()
		if self.help_win:
			self.help_win.refresh()
		if self.path_win:
			self.path_win.refresh()
		if self.log_win:
			self.log_win.refresh()

# MAP ------------------------------------------------------------------
	
	def draw_map(self, board_map, path):
		""" Draw the map"""
		board_size = len(board_map)
		
		if board_size > 27 :
			self.PATH_Y = self.DATA_Y + board_size + 3
			self.PATH_X = 0
			self.LOG_Y = self.PATH_Y + self.PATH_H + 1
			self.LOG_X = 0
			self.HELP_X = 0
			self.HELP_Y = self.LOG_Y + self.LOG_H - 3
			self.HELP_H = 3
			self.HELP_W = self.LOG_W
		
		self.stdscr.addstr(self.PATH_Y -1 , self.PATH_X +1, "Path and heuristic", curses.A_BOLD)
		self.path_win = curses.newwin(self.PATH_H, self.PATH_W, self.PATH_Y, self.PATH_X)
		self.path_win.addstr(1, 1, "Heuristic", curses.A_BOLD)
		self.path_win.addstr(3, 1, "Path to goal", curses.A_BOLD)
		self.path_win.hline(2, 1, curses.ACS_HLINE, 64)
		self.path_win.vline(1, 13, curses.ACS_VLINE, 4)
		self.path_win.box()
		self.path_win.addch(2, 0, curses.ACS_LTEE)
		self.path_win.addch(2, 65, curses.ACS_RTEE)	
		self.path_win.addch(0, 13, curses.ACS_TTEE)
		self.path_win.addch(4, 13, curses.ACS_BTEE)		
		
		self.stdscr.addstr(self.LOG_Y - 1, self.LOG_X + 1, "Log", curses.A_BOLD)	
		self.log_win = curses.newwin(self.LOG_H, self.LOG_W, self.LOG_Y, self.LOG_X)
		self.log_win.box()
		
		self.help_win = curses.newwin(self.HELP_H, self.HELP_W, self.HELP_Y, self.HELP_X)
		self.help_win.bkgd(curses.color_pair(4) + curses.A_REVERSE)	
		
		self.map_win = curses.newwin(board_size+2, board_size+2, self.DATA_Y, self.DATA_X + self.DATA_W + 2)
		self.map_win.box()
		self.MAP_Y, self.MAP_X = self.map_win.getbegyx()
		self.stdscr.addstr(self.MAP_Y - 1, self.MAP_X + 1, "Map", curses.A_BOLD)
		self.MAP_H = board_size
		self.MAP_W = board_size
		
		# highlight choosen path
		for cell in path:
			self.map_win.addch(cell[0]+1, cell[1]+1, curses.ACS_BULLET, curses.color_pair(3) + curses.A_BOLD)
				
		# Draw map content
		y = 0
		for line in board_map:
			x = 0
			for char in line :
				attr = 0
				if char == "#":
					attr = 0
					char = curses.ACS_CKBOARD
				elif char == "$":
					attr = curses.A_BOLD + curses.color_pair(4)
				elif char == "T":
					attr = curses.A_BOLD + curses.color_pair(5)
				elif char == "H":
					attr = curses.A_BOLD + curses.color_pair(6)
				elif char == "@":
					attr = curses.A_BOLD + curses.color_pair(2)
				elif char == "X":
					char = 164
					attr = curses.A_BOLD + curses.color_pair(7)
				
				if char != " ":
					self.map_win.addch(y+1, x+1, char, attr)
				x = x +1
			y = y +1
		self.stdscr.refresh()

# DATA -----------------------------------------------------------------

	# Following methods are used to display data at
	# the good place. Names are explicit.
	
	def display_url(self, url):
		url = url[url.rfind("/")+1:]
		self.data_win.addstr(1, 17, str(url))
		
	def display_bot_name(self, name):
		self.data_win.addstr(3, 15, str(name[0:15]))
		
	def display_turn(self, turn, max_turns):
		self.clear_data_cell((9, 14), 8)
		self.clear_data_cell((9, 23), 8)
		self.data_win.addstr(9, 24, str(turn)+"/"+str(max_turns), curses.A_BOLD)
		self.data_win.addstr(9, 15, str(turn+1)+"/"+str(max_turns), curses.A_BOLD )
		
	def display_elapsed(self, elapsed):
		self.clear_data_cell((7, 14), 17)
		attr = 0
		if elapsed > 0.5 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.data_win.addstr(7, 20, str(elapsed), attr)
		
	def display_pos(self, pos):
		self.clear_data_cell((11, 14), 8)
		self.data_win.addstr(11, 14, str(pos))
		
	def display_last_pos(self, pos):
		self.clear_data_cell((11, 23), 8)
		self.data_win.addstr(11, 23, str(pos))

	def display_action(self, action):
		self.clear_data_cell((21, 14), 8)
		self.data_win.addstr(21, 15, str(action))

	def display_last_action(self, action):
		self.clear_data_cell((21, 23), 8)
		self.data_win.addstr(21, 24, str(action))

	def display_move(self, move):
		self.clear_data_cell((19, 14), 8)
		self.data_win.addstr(19, 15, str(move))

	def display_last_move(self, move):
		self.clear_data_cell((19, 23), 8)
		self.data_win.addstr(19, 24, str(move))

	def display_life(self, life):
		self.clear_data_cell((13, 14), 8)
		attr = 0
		if life < 20 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.data_win.addstr(13, 16, str(life), attr)

	def display_last_life(self, life):
		self.clear_data_cell((13, 23), 8)
		attr = 0
		if life < 20 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.data_win.addstr(13, 25, str(life), attr)
		
	def display_mine_count(self, mine_count):
		self.clear_data_cell((15, 14), 8)
		attr = 0
		if mine_count[0] == "0":
			attr = curses.color_pair(3) + curses.A_BOLD
		self.data_win.addstr(15, 15, str(mine_count), attr)
		
	def display_last_mine_count(self, mine_count):
		self.clear_data_cell((15, 23), 8)
		attr = 0
		if mine_count[0] == "0":
			attr = curses.color_pair(3) + curses.A_BOLD
		self.data_win.addstr(15, 24, str(mine_count), attr)
	
	def display_gold(self, gold):
		self.clear_data_cell((17, 14), 8)
		self.data_win.addstr(17, 15, str(gold))
		
	def display_last_gold(self, gold):
		self.clear_data_cell((17, 23), 8)
		self.data_win.addstr(17, 24, str(gold))
	
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
		decision = str(decision)[0:48]+"..."
		self.path_win.addstr(1, 14, decision)
		
	def display_path(self, path):
		path = str(path)[0:48]+"..."
		self.path_win.addstr(3, 14, path)

	def clear_data_cell(self, pos, length):
		self.data_win.hline(pos[0], pos[1],  " ", length)

# LOG ------------------------------------------------------------------

	def append_log(self, data):
		""" Append log with new data """		
		for i in range(0, len(str(data)), self.LOG_W - 2):
			""" Cut string to parts with appropriate length """
			self.log_entries.append(str(data)[i:i+self.LOG_W - 2])	
		self.purge_log()
		self.display_log()

	def purge_log(self):
		""" Purge log of oldest entries """
		diff = len(self.log_entries) - (self.LOG_H - self.HELP_H)
		if diff > 0:
			for i in range(diff):
				self.log_entries.remove(self.log_entries[i])


	def display_log(self):
		""" Display log entries """
		if self.map_win:
			self.log_win.erase()
			self.log_win.box()
			i = 0
			for entry in self.log_entries:
				attr = 0
				regexp = re.compile('Error')
				
				if regexp.search(entry) is not None:
					attr = curses.color_pair(3) + curses.A_BOLD				
				self.log_win.addstr(i+1, 1, entry, attr)
				i += 1
			self.refresh()

# QUIT -----------------------------------------------------------------
		
	def ask_quit(self):
		""" What don't you understand in 'press q to exit' ? ;-) """
		#~ self.help_win.clear()
		self.help_win.addstr(1, 1, "Press 'q' to quit.")
		curses.doupdate()

		k = self.help_win.getkey()
		if k == 'q':
			self.quit_ui()
		else :
			self.ask_quit()
	
	def quit_ui(self):
		""" Quit the UI and restore terminal state """
		self.stdscr.clear()
		curses.nocbreak()
		self.stdscr.keypad(0)
		curses.curs_set(1)
		curses.echo()
		curses.endwin()

# ERROR ----------------------------------------------------------------

	def term_error(self, error):
		""" Manage terminal errors. 
		May not work at all ! """
		# Terminal is to small and not resizable
		screen_y, screen_x = self.stdscr.getmaxyx() 
		self.quit_ui()
		print ("Unable to resize terminal: Your terminal needs to be at least "+\
		str(MIN_LINES)+" lines X "+str(MIN_COLS)+" cols and was "+str(screen_y)+"X"+str(screen_y))
		print error
		quit()
