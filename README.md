vindinium-curses_ui
===================

Python/Curses user interface for the Vindinium A.I contest.
http://www.vindinium.org/


1 - Licence :
-------------
	This code is published by Doug Le Tough (doug.letough@free.fr) 
	and released under the W.T.F.P.L.
	
	It is based uppon the Vindium python starter available here :
	https://github.com/ornicar/vindinium-starter-python
	
	A copy of the W.T.F.P.L is available in the LICENCE.txt file 
	that should accompany this source code.

	For further information about the WTFPL please
	visit  http://www.wtfpl.net/

2 - Content :
-------------

/vindinium-curses_ui
  |_ bot.py ------- The bot code source. This where to put your AI main code
  |_ client.py ---- The client used to connect to game server
  |_ game.py ------ Code used to process data sent by the server
  |_ tui.py ------- The curses U.I code source
  |_ README.md ---- This file
  |_ LICENCE.txt -- A copy of the W.T.F.P.L
  |_ curses_ui_bot.png ------ A screenshoot of the running U.I

3 - How to make it work :
-------------------------

	The bot.py file contains the code of your bot.
	It's merely the only file you'll need to play with.

	In order to make it work, you need to :
		a - If you don't want the curses UI to be displayed, set the 
			self.use_ui variable to False in bot.py file (line 18)
			
			In this case, all log message will be printed out to the console.
		
		b - Launch it with :
			python client.py <key> <[training|arena]> <number-of-games-to-play> [server-url]
			
			Examples:
			
			python client.py mySecretKey arena 10
			python client.py mySecretKey training 10 http://localhost:9000
		
	Note : The code provided here do NOT contains any AI or path-finding code 
	but only a random AI. However it would run fine as is but would only win by mistake :-)


