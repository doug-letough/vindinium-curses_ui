#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import re

# 80 cols horizontal rule
HR = "------------------------------------------------------------------------------"
VR = "|"

# Minimal terminal size
MIN_LINES = 48
MIN_COLS = 80
# Map vertical offset
MAP_Y = 16
# Log panel offset
LOG_Y = MAP_Y
LOG_X = 30
# Log panel size
LOG_HEIGHT = 19
LOG_WIDTH = 47

		
class tui:
	"""The Terminal User Interface for Vindimium bot"""
	def __init__(self):
		self.stdscr = curses.initscr()
		curses.start_color()
		# Basic color set
		self.WHITE = curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
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
		self.stdscr.clear()
		try :
			self.draw_ui()
			self.log_panel = log_panel(self.stdscr)
		except Exception as e:
			self.term_error(e)

	
	def draw_ui(self):
		""" Draw the main UI """
		separators = [3, 5, 7]
		for i in range(15):
			if not i % 2 :
				self.stdscr.addstr(i, 1, HR, curses.A_BOLD)
			else :
				self.stdscr.addstr(i, 0, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 79, VR, curses.A_BOLD)
			if i in separators:
				self.stdscr.addstr(i, 12, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 21, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 29, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 36, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 49, VR, curses.A_BOLD)
				self.stdscr.addstr(i, 61, VR, curses.A_BOLD)
				
		self.stdscr.addstr(1, 2, "Playing at:", curses.A_BOLD)
		self.stdscr.addstr(1, 44, "| Elapsed:", curses.A_BOLD)
		self.stdscr.addstr(1, 61, "| Pos:", curses.A_BOLD)
		self.stdscr.addstr(3, 4, "Turn", curses.A_BOLD)
		self.stdscr.addstr(3, 14, "Action", curses.A_BOLD)
		self.stdscr.addstr(3, 23, "Move", curses.A_BOLD)
		self.stdscr.addstr(3, 31, "Life", curses.A_BOLD)
		self.stdscr.addstr(3, 38, "Mine count", curses.A_BOLD)
		self.stdscr.addstr(3, 53, "Gold", curses.A_BOLD)
		self.stdscr.addstr(3, 67, "Elo", curses.A_BOLD)
		self.stdscr.addstr(9, 2, "Nearest mine:", curses.A_BOLD)
		self.stdscr.addstr(9, 25, "| Nearest tavern:", curses.A_BOLD)
		self.stdscr.addstr(9, 52, "| Nearest hero:", curses.A_BOLD)
		self.stdscr.addstr(11, 2, "Decision:", curses.A_BOLD)	
		self.stdscr.addstr(13, 2, "Path to goal:", curses.A_BOLD)	
		self.draw_log_panel_frame()
	
	def draw_map(self, board_map, path):
		""" Draw the map"""
		board_size = len(board_map)
		self.stdscr.addstr(MAP_Y-1, 1, "Map", curses.A_BOLD)
		# map frame		
		for y in range(board_size+2):
			for x in range(board_size+2):
				if (y == 0 and 0 < x < board_size+1) or (y == board_size+1 and 0 < x < board_size+1):
					self.stdscr.addstr(MAP_Y+y, x, "-", curses.A_BOLD)
				if (y > 0 and y < board_size+1) and (x == 0 or x == board_size+1):
					self.stdscr.addstr(MAP_Y+y, x, "|", curses.A_BOLD)
		
		# highlight choosen path
		for cell in path:
			self.stdscr.addch(MAP_Y+cell[0]+1, cell[1]+1, curses.ACS_BULLET, curses.color_pair(3) + curses.A_BOLD)
				
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
				
				if char != " ":
					self.stdscr.addch(MAP_Y+y+1, x+1, char, attr)
				x = x +1
			y = y +1
		
	def draw_log_panel_frame(self):
		""" Draw the log panel"""
		self.stdscr.addstr(LOG_Y-1, LOG_X+1, "Log", curses.A_BOLD)
		
		log_height = LOG_HEIGHT+1
		log_width = LOG_WIDTH+1
		for y in range(log_height+2):
			for x in range(log_width+2):
				if (y == 0 and 0 < x < log_width+1) or (y == log_height+1 and 0 < x < log_width+1):
					self.stdscr.addstr(LOG_Y+y, x+LOG_X, "-", curses.A_BOLD)
				if (y > 0 and y < log_height+1) and (x == 0 or x == log_width+1):
					self.stdscr.addstr(LOG_Y+y, x+LOG_X, "|", curses.A_BOLD)
					

	def display(self, string):
		""" Add string to log entries"""
		self.log_panel.append(str(string))


	# Following methods are used to display data at
	# the good place. Names are explicit.
	
	def display_url(self, url):
		self.stdscr.addstr(1, 14, str(url))
		
	def display_turn(self, turn, max_turns):
		if turn > 0 :
			self.stdscr.addstr(5, 4, str(turn-1)+"/"+str(max_turns), curses.A_BOLD )
		self.stdscr.addstr(7, 4, str(turn)+"/"+str(max_turns), curses.A_BOLD)
		
	def display_elapsed(self, elapsed):
		attr = 0
		if elapsed > 0.5 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.stdscr.addstr(1, 55, str(elapsed), attr)
		
	def display_pos(self, pos):
		self.stdscr.addstr(1, 68, str(pos))

	def display_last_action(self, action):
		self.stdscr.addstr(5, 14, str(action))
		
	def display_action(self, action):
		self.stdscr.addstr(7, 14, str(action))
		
	def display_last_move(self, move):
		self.stdscr.addstr(5, 23, str(move))
		
	def display_move(self, move):
		self.stdscr.addstr(7, 23, str(move))
		
	def display_last_life(self, life):
		attr = 0
		if life < 20 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.stdscr.addstr(5, 31, str(life), attr)
		
	def display_life(self, life):
		attr = 0
		if life < 20 :
			attr = curses.color_pair(3) + curses.A_BOLD
		self.stdscr.addstr(7, 31, str(life), attr)
		
	def display_mine_count(self, mine_count):
		attr = 0
		if mine_count[0] == "0":
			attr = curses.color_pair(3) + curses.A_BOLD
		self.stdscr.addstr(7, 40, str(mine_count), attr)
		
	def display_last_mine_count(self, mine_count):
		attr = 0
		if mine_count[0] == "0":
			attr = curses.color_pair(3) + curses.A_BOLD
		self.stdscr.addstr(5, 40, str(mine_count), attr)
	
	def display_gold(self, gold):
		self.stdscr.addstr(7, 53, str(gold))
		
	def display_last_gold(self, gold):
		self.stdscr.addstr(5, 53, str(gold))
	
	def display_elo(self, elo):
		self.stdscr.addstr(7, 66, str(elo))
	
	def display_last_elo(self, elo):
		self.stdscr.addstr(5, 66, str(elo))
		
	def display_nearest_mine(self, mine):
		self.stdscr.addstr(9, 16, str(mine))
		
	def display_nearest_tavern(self, tavern):
		self.stdscr.addstr(9, 43, str(tavern))
		
	def display_nearest_hero(self, hero):
		self.stdscr.addstr(9, 68, str(hero))
	
	def display_decision(self, decision):
		if len(str(decision)) > 66 :
			decision = str(decision)[0:63]+"..."
		self.stdscr.addstr(11, 12, str(decision))
		
	def display_path(self, path):
		if len(str(path)) > 62 :
			path = str(path)[0:59]+"..."
		self.stdscr.addstr(13, 16, str(path))
	
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

	def refresh(self):
		""" Refresh UI """
		self.log_panel.display()
		self.stdscr.refresh()

	def clear(self):
		""" Clear screen """
		self.stdscr.clear()
		
	def ask_quit(self):
		""" What don't you understand in 'press q to exit' ? ;-) """
		self.display("Press 'q' to quit.")
		while 1:
			k = self.stdscr.getkey()
			if k == 'q':
				break
			else:
				""" You did *NOT* press the good 'q' key """
				self.log_panel.append("Try the _other_ 'q' !")
		self.quit_ui()

	
	def quit_ui(self):
		""" Quit the UI and restore terminal state """
		self.stdscr.clear()
		curses.nocbreak()
		self.stdscr.keypad(0)
		curses.curs_set(1)
		curses.echo()
		curses.endwin()


class log_panel:
	""" The log panel object """
	def __init__(self, screen):
		self.entries = []
		self.screen = screen
	
		
	def append(self, string):
		""" Append log with new string """		
		for i in range(0, len(string), LOG_WIDTH):
			""" Cut string to parts with appropriate length """
			self.entries.append(string[i:i+LOG_WIDTH])	
		self.purge()
		self.display()


	def purge(self):
		""" Purge log of oldest entries """
		diff = len(self.entries) - LOG_HEIGHT
		if diff > 0:
			for i in range(diff):
				self.entries.remove(self.entries[i])
	
	
	def display(self):
		""" Display log entries """
		i = 0
		empty_line = ""
		for j in range(LOG_WIDTH):
			empty_line = empty_line + " "
		for entry in self.entries:
			attr = 0
			regexp = re.compile('Error')
			if regexp.search(entry) is not None:
				attr = attr = curses.color_pair(3) + curses.A_BOLD
			self.screen.addstr(LOG_Y+1+i, LOG_X+1, empty_line)
			self.screen.addstr(LOG_Y+1+i, LOG_X+1, entry, attr)
			i += 1

if __name__ == "__main__":
	a = tui()
	a.ask_quit()
