#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from bot import Curses_ui_bot
import tui

TIMEOUT=15

def _print(*args, **kwargs):
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
              
	if my_bot.gui:
		# bot has a gui so we add this entries to its log panel
		my_bot.gui.display(printable)
	else:
		print printable
				
	

def get_new_game_state(session, server_url, key, mode='training', number_of_turns = 10):
	"""Get a JSON from the server containing the current state of the game"""

	if(mode=='training'):
		#Don't pass the 'map' parameter if you want a random map
		#~ params = { 'key': key, 'turns': number_of_turns, 'map': 'm5'}
		params = { 'key': key, 'turns': number_of_turns}
		api_endpoint = '/api/training'
	elif(mode=='arena'):
		params = { 'key': key}
		api_endpoint = '/api/arena'

	#Wait for 10 minutes
	r = session.post(server_url + api_endpoint, params, timeout=10*60)
	if(r.status_code == 200):
		return r.json()
	else :
		_print("Error when creating the game")
		_print(r.text)
		
def move(session, url, direction):
	"""Send a move to the server

	Moves can be one of: 'Stay', 'North', 'South', 'East', 'West' 
	"""

	try:
		r = session.post(url, {'dir': direction}, timeout=TIMEOUT)

		if(r.status_code == 200):
			return r.json()
		else :
			_print("Error HTTP ", str(r.status_code), " : ", r.text)
			return {'game': {'finished': True}}
			 
	except requests.exceptions.RequestException as e:
		_print("Error at client.move;", str(e))
		return {'game': {'finished': True}}
	

def is_finished(state):
	return state['game']['finished']

def start(server_url, key, mode, turns, bot):
	"""Starts a game with all the required parameters"""

	# Create a requests session that will be used throughout the game
	session = requests.session()

	if(mode=='arena'):
		_print ('Connected and waiting for other players to join...')

	# Get the initial state
	state = get_new_game_state(session, server_url, key, mode, turns)
	
	# Start the GUI
	if not bot.gui :
		bot.start_ui()
	
	_print("Playing at: " + state['viewUrl'])

	# Default move is no move !
	direction = "Stay"
		
	while not is_finished(state):
		# Choose a move
		# Remove the try/except exception trap to help debugging 
		# your bot, but keep the "direction = bot.move(state)" line.
		#~ try:
			direction = bot.move(state)
		except Exception, e:
			_print("Error at client.start:", str(e))
			_print("Please report this error to doug.letough@free.fr.")
			if bot.gui:
				bot.gui.ask_quit()

		# Send the move and receive the updated game state
		url = state['playUrl']
		state = move(session, url, direction)

	# Clean up the session
	session.close()
    

if __name__ == "__main__":
	my_bot = None # our bot

	if (len(sys.argv) < 4):
		_print("Usage: %s <key> <[training|arena]> <number-of-games|number-of-turns> [server-url]" % (sys.argv[0]))
		_print('Example: %s mySecretKey training 20' % (sys.argv[0]))
	else:
		key = sys.argv[1]
		mode = sys.argv[2]

		if(mode == "training"):
			number_of_games = 1
			number_of_turns = int(sys.argv[3])
		else: 
			number_of_games = int(sys.argv[3])
			number_of_turns = 300 # Ignored in arena mode

		if(len(sys.argv) == 5):
			server_url = sys.argv[4]
		else:
			server_url = "http://vindinium.org"

		for i in range(number_of_games):
			# start a new game
			my_bot = Curses_ui_bot()
			start(server_url, key, mode, number_of_turns, my_bot)
			_print("Game finished : "+str(i+1)+"/"+str(number_of_games))
			if i < (number_of_games - 1):
				# EXTRA BALL ! Same player shoot again :)
				if my_bot and my_bot.gui:
					my_bot.gui.quit_ui()
			else:
				# no more game to play
				if my_bot and my_bot.gui:
					my_bot.gui.ask_quit()
			
