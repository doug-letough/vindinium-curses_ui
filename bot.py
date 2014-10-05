#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from game import Game
import ui
import ai


DIRS = ["North", "East", "South", "West", "Stay"]
ACTIONS = ["Go mine", "Go beer", "Go enemy"]

class Curses_ui_bot:
	""" THis is your bot """
	def __init__(self):
		# If false UI will not spawn and log
		# will be printed to the console
		self.use_ui = True
		
		self.gui = None
		self.state = None
		self.game = None
		self.last_mine_count = 0
		self.last_gold = 0
		self.last_life = 0
		self.hero_move = None
		self.hero_last_move = None
		self.action = None
		self.last_action = None
		self.path_to_goal = None
		self.decision = None
		self.last_pos = None
		self.last_nearest_enemy_pos = None
		self.last_nearest_mine_pos = None
		self.last_nearest_tavern_pos = None
		
		# The AI, Skynet's rising !
		self.ai = ai.AI()
	
	def start_ui(self):
		""" Start the curses UI """
		if self.use_ui :
			self.gui = ui.tui()
	
	def move(self, state):
		start = time.time()
		
		self.state = state
		self.game = Game(self.state)
		################################################################
		# Put your AI code here
		################################################################
		
		
		self.ai.process(self.game)
		
		self.path_to_goal, \
		self.action, \
		self.decision, \
		self.hero_move, \
		self.nearest_enemy_pos, \
		self.nearest_mine_pos, \
		self.nearest_tavern_pos = self.ai.decide()
		
		
		################################################################
		# /AI
		################################################################

		# Use self._print() to add entry to log
		# or console if no GUI
		#~ self._print("My direction:", self.hero_move)
		#~ self._print("My pos:", self.game.hero.pos)
		
		if self.use_ui:
			if not self.gui.paused :	
				# Draw the map
				self.gui.draw_map(self.game.board_map, self.path_to_goal)
				
				# Print informations about other players
				self.gui.display_heroes(self.game.heroes, self.game.hero.user_id)
				
				# Use the following methods to display datas
				# within the interface
				self.gui.display_url(state['viewUrl'])		
				self.gui.display_bot_name(self.game.hero.name)		
				self.gui.display_last_move(self.hero_last_move)
				self.gui.display_pos(self.game.hero.pos)
				self.gui.display_last_pos(self.last_pos)
				self.gui.display_last_life(self.last_life)
				self.gui.display_life(self.game.hero.life)
				self.gui.display_last_action(self.last_action)
				self.gui.display_turn(self.game.turn/4, self.game.max_turns/4)
				self.gui.display_elo(self.game.hero.elo)
				self.gui.display_gold(self.game.hero.gold)
				self.gui.display_last_gold(self.last_gold)
				self.gui.display_mine_count(str(self.game.hero.mine_count)+"/"+str(len(self.game.mines)))
				self.gui.display_last_mine_count(str(self.last_mine_count)+"/"+str(len(self.game.mines)))
				

				# You can also use those methods to display more information
				# Function names are explicit, don't they ?
				self.gui.display_nearest_mine(self.nearest_mine_pos)
				self.gui.display_nearest_hero(self.nearest_enemy_pos)
				self.gui.display_nearest_tavern(self.nearest_tavern_pos)
				self.gui.display_last_nearest_mine(self.last_nearest_mine_pos)
				self.gui.display_last_nearest_hero(self.last_nearest_enemy_pos)
				self.gui.display_last_nearest_tavern(self.last_nearest_tavern_pos)

				# Print what you think is usefull to understand
				# how the decision has been taken to make this move
				# If too long the string will be truncated to fit 
				# in the display
				self.gui.display_decision(self.decision)
				
				# Print the estimated path to reach the goal if any
				# If too long the path will be truncated to fit 
				# in the display
				self.gui.display_path(self.path_to_goal)
				
				# Finally display selected move
				self.gui.display_move(self.hero_move)
				self.gui.display_action(self.action)
			
		################################################################
		# Log
		################################################################
		# Uncomment the following line to append log
		
		self._print(self.game.hero.pos, self.hero_move)
		
		################################################################
		# /Log
		################################################################

		# Store status for later report
		self.hero_last_move = self.hero_move
		self.last_life = self.game.hero.life
		self.last_action = self.action
		self.last_gold = self.game.hero.gold
		self.last_mine_count = self.game.hero.mine_count
		self.last_pos = self.game.hero.pos
		self.last_nearest_enemy_pos = self.nearest_enemy_pos
		self.last_nearest_mine_pos = self.nearest_mine_pos
		self.last_nearest_tavern_pos = self.nearest_tavern_pos
		
		# How long does it take to compute
		# (and to display it) this move ?
		end = time.time()
		elapsed = round(end - start, 3)
		
		if self.use_ui:
			if not self.gui.paused:
				self.gui.display_elapsed(elapsed)
				self.gui.refresh()
			
		return self.hero_move
		
		
	def _print(self, *args, **kwargs):
		"""Display args in the bot gui or 
		print it if no gui is available"""
		printable = ""
		for arg in args:
			printable = printable + str(arg)+" "
		if kwargs and len(kwargs) :
			a = 1
			coma = ""
			printable = printable + "["
			for k,v in kwargs.iteritems():
				if 1 < a < len(kwargs):
					coma = ", "
				else:
					coma = "]"
				printable = printable + str(k) + ": " + str(v) + coma
				a = a + 1
				  
		if self.gui and self.gui.running:
			# bot has a gui so we add this entries to its log panel
			self.gui.append_log(printable)
		else:
			print printable 
	
