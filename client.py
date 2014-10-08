#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bot import Curses_ui_bot
import ui
import sys
import select
import time

TIMEOUT=15

class Client:
    def __init__(self):
        self.start_time = None
        self.gui = None
        self.session = None
        self.state = None
                
        self.running = True
        self.bot = Curses_ui_bot() # our bot
        
    
    def start_ui(self):
        """ Start the curses UI """
        self.gui = ui.tui()        
        choice = self.gui.ask_main_menu()
        number_of_games = 1
        number_of_turns = 300
        if choice =='1':
            # Setup game
            choice = self.gui.ask_game_mode()
            if choice == '1':
                # Arena mode
                game_mode = "arena"
                number_of_games = self.gui.ask_number_games()
            elif choice == '2':
                # Training mode
                game_mode = "training"
                number_of_turns = self.gui.ask_number_turns()
                map_name = self.gui.ask_map()

            server_url = self.gui.ask_server_url(game_mode)
            key = self.gui.ask_key(game_mode)
            
            # Start game U.I
            self.gui.draw_game_windows()
            # Launch game
            self.play(number_of_games, number_of_turns, server_url, key, game_mode)
             
        elif choice =='2':
            # Load game from file
            game_file_path = self.gui.ask_game_file_path()
        elif choice =='3':
            # Load game from URL
            game_file_url = self.gui.ask_game_file_url()
        elif choice =='4':
            # quit
            self.gui.quit_ui()
            exit(0)    
            
    def display_game(self, game):
        # Display game data on the U.I
        
        if not self.gui.paused :
            # Draw the map
            self.gui.draw_map(self.bot.game.board_map, self.bot.path_to_goal)
            
            # Print informations about other players
            self.gui.display_heroes(self.bot.game.heroes, self.bot.game.hero.user_id)
            
            # Use the following methods to display datas
            # within the interface
            self.gui.display_url(self.bot.game.url)
            self.gui.display_bot_name(self.bot.game.hero.name)        
            self.gui.display_last_move(self.bot.hero_last_move)
            self.gui.display_pos(self.bot.game.hero.pos)
            self.gui.display_last_pos(self.bot.last_pos)
            self.gui.display_last_life(self.bot.last_life)
            self.gui.display_life(self.bot.game.hero.life)
            self.gui.display_last_action(self.bot.last_action)
            self.gui.display_turn((self.bot.game.turn/4)-1, self.bot.game.max_turns/4)
            self.gui.display_elo(self.bot.game.hero.elo)
            self.gui.display_gold(self.bot.game.hero.gold)
            self.gui.display_last_gold(self.bot.last_gold)
            self.gui.display_mine_count(str(self.bot.game.hero.mine_count)+"/"+str(len(self.bot.game.mines)))
            self.gui.display_last_mine_count(str(self.bot.last_mine_count)+"/"+str(len(self.bot.game.mines)))
            

            # You can also use those methods to display more information
            # Function names are explicit, don't they ?
            self.gui.display_nearest_mine(self.bot.nearest_mine_pos)
            self.gui.display_nearest_hero(self.bot.nearest_enemy_pos)
            self.gui.display_nearest_tavern(self.bot.nearest_tavern_pos)
            self.gui.display_last_nearest_mine(self.bot.last_nearest_mine_pos)
            self.gui.display_last_nearest_hero(self.bot.last_nearest_enemy_pos)
            self.gui.display_last_nearest_tavern(self.bot.last_nearest_tavern_pos)

            # Print what you think is usefull to understand
            # how the decision has been taken to make this move
            # If too long the string will be truncated to fit 
            # in the display
            self.gui.display_decision(self.bot.decision)
            
            # Print the estimated path to reach the goal if any
            # If too long the path will be truncated to fit 
            # in the display
            self.gui.display_path(self.bot.path_to_goal)
            
            # Move cursor along the time line
            cursor_pos = int(float(self.gui.TIME_W) / self.bot.game.max_turns * self.bot.game.turn)
            self.gui.move_time_cursor(cursor_pos)
            
            # Finally display selected move
            self.gui.display_move(self.bot.hero_move)
            self.gui.display_action(self.bot.action)
            
            # Add whathever you want to log using self.gui.append_log()
            # self.gui.append_log("Whatever")

            elapsed = round(time.time() - self.start, 3)
            self.gui.display_elapsed(elapsed)
            
            self.gui.refresh()
                

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
            if self.gui.log_win:
                self.gui.append_log(printable)
                self.gui.log_win.refresh()
        else:
            print printable
                

    def play(self, number_of_games, number_of_turns, server_url, key, mode):
        """ Play all games """        
        game_num = 0
        for i in range(number_of_games):
            # start a new game
            if self.bot.running :
                self.start_game(server_url, key, mode, number_of_turns, self.bot)
                self._print("Game finished: "+str(i+1)+"/"+str(number_of_games))
            game_num += 1

        if self.gui.running and self.gui.help_win:
            self.gui.ask_quit()


    def get_new_game_state(self, session, server_url, key, mode='training', number_of_turns = 10):
        """Get a JSON from the server containing the current state of the game"""

        if(mode=='training'):
            #Don't pass the 'map' parameter if you want a random map
            params = { 'key': key, 'turns': number_of_turns, 'map': 'm1'}
            #~ params = { 'key': key, 'turns': number_of_turns}
            api_endpoint = '/api/training'
        elif(mode=='arena'):
            params = { 'key': key}
            api_endpoint = '/api/arena'

        #Wait for 10 minutes
        r = session.post(server_url + api_endpoint, params, timeout=10*60)
        if(r.status_code == 200):
            return r.json()
        else :
            self._print("Error when creating the game:", str(r.status_code))
            self.running = False
            self._print(r.text)
            
        
    def send_move(self, session, url, direction):
        """Send a move to the server
        Moves can be one of: 'Stay', 'North', 'South', 'East', 'West' 
        """

        try:
            r = session.post(url, {'dir': direction}, timeout=TIMEOUT)

            if(r.status_code == 200):
                return r.json()
            else :
                self._print("Error HTTP ", str(r.status_code), " : ", r.text)
                self.running = False
                return {'game': {'finished': True}}
                 
        except requests.exceptions.RequestException as e:
            self._print("Error at client.move;", str(e))
            self.running = False
            return {'game': {'finished': True}}
    

    def is_game_over(self, state):
        try:
            return state['game']['finished']
        except:
            return True


    def start_game(self, server_url, key, mode, turns, bot):
        """Starts a game with all the required parameters"""
        self.running = True
        
        # Create a requests session that will be used throughout the game
        self.session = requests.session()

        if(mode=='arena'):
            self._print ('Connecting and waiting for other players to join...')

        try:
            # Get the initial state
            self.state = self.get_new_game_state(self.session, server_url, key, mode, turns)
            self._print("Playing at: " + self.state['viewUrl'])
        except Exception as e:
            self._print("Error: Please verify your settings.")
            self._print("Settings:", server_url, key, mode, turns)
            self._print("Settings:", len(server_url), len(key), len(mode), type(turns))
            self._print("Game state:", self.state)
            self.running = False
            self.gui.ask_quit()
            quit(0)

        # Default move is no move !
        direction = "Stay"
            
        for i in range(turns + 1):
            if self.running:
                # Choose a move                
                self.start = time.time()
                
                try:
                    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.read(1)
                        if line.strip() == "q":
                            self.running = False
                            self.gui.quit_ui()
                            self.bot.running = False
                            break
                        elif line.strip() == "p":
                            self.gui.pause()
                            
                    if self.bot.running:
                        direction = self.bot.move(self.state)
                        self.display_game(self.bot.game)
                        
                except Exception, e:
                    if self.gui.log_win:
                        self._print("Error at client.start_game:", str(e))
                        self._print("If your code or your settings are not responsible of this error, please report this error to:")
                        self._print("doug.letough@free.fr.")
                        self.gui.pause()
                        self.running = False
                    if self.gui.help_win:
                        self.gui.ask_quit()

                if not self.is_game_over(self.state):
                    # Send the move and receive the updated game state
                    self.url = self.state['playUrl']
                    self.state = self.send_move(self.session, self.url, direction)

        # Clean up the session
        self.session.close()

if __name__ == "__main__":
    server_url = "http://vindinium.org"
    
    if len(sys.argv) == 1:
        # Go for interactive setup
        client = Client()
        client.start_ui()
    
    elif len(sys.argv) < 3 or sys.argv[1] == "--help":
        print("Usage: %s <key> <[training|arena]> <number-of-games|number-of-turns> [server-url]" % (sys.argv[0]))
        print("or: %s " % (sys.argv[0]))
        print('Example: %s mySecretKey training 20' % (sys.argv[0]))
        exit(0)
    elif len(sys.argv) > 3:
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
        
        # Go for playing according to sys.argv
        # Do not use interactive setup
        client = Client()
        client.gui = ui.tui()
        client.gui.draw_game_windows()
        client.play(number_of_games, number_of_turns, server_url, key, mode)

