vindinium-curses_ui
===================

Python/Curses user interface for the Vindinium A.I contest.
http://www.vindinium.org/


1 - Licence :
-------------
	This code is published by Doug Le Tough (doug.letough@free.fr) 
	and released under the W.T.F.P.L.
	
	It is based upon the Vindium python starter available here :
	https://github.com/ornicar/vindinium-starter-python
	
	A copy of the W.T.F.P.L is available in the LICENCE.txt file 
	that should accompany this source code.

	For further information about the WTFPL please
	visit  http://www.wtfpl.net/

2 - Content :
-------------

 - ai.py                The random A.I. This is where to put your A.I code
 - bot.py               The bot object source code. Collects data processed.
 - CHANGELOG.TXT        The changelog, you may read it.
 - client.py            The client source code used to connect to game server
 - curses_ui_bot.png    A screenshot of the running U.I
 - game.py              Source code used to process data sent by the server
 - LICENCE.txt          A copy of the W.T.F.P.L
 - README.md            This file
 - ui.py                The curses U.I. source code

3 - How to make it work :
-------------------------

	The ai.py file contains the code of your bot.
	With the bot.py file, it's merely the only file you'll need to play with.

	Many comments are dissiminated within the source code. 
	They shall help you to understand how to plug your A.I to the U.I.

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
	but only a random AI. However it would run fine as is but would only win by mistake :)
	
	Also note that in many points this code is far from perfect or even far from good.
	Don't hesitate to contribute, improve, refactor or even simply trash it !
	
	


