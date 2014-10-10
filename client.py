#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bot import Curses_ui_bot
import ui
import sys
import select
import time
import os
import ConfigParser

TIMEOUT = 15


class Config:
    def __init__(self, game_mode="training", server_url="http://vindinium.org",
                        number_of_games=1, number_of_turns=300, map_name="m1", key=None):
        self.game_mode = game_mode
        self.number_of_games = number_of_games
        self.number_of_turns = number_of_turns
        self.map_name = map_name
        self.server_url = server_url
        self.key = key


class Client:
    def __init__(self):
        self.start_time = None
        self.gui = None
        self.session = None
        self.state = None
        self.running = True
        self.game_url = None
        self.config = Config()
        self.bot = Curses_ui_bot()  # Our bot

    def _print(self, *args, **kwargs):
        """Display args in the bot gui or
        print it if no gui is available"""
        printable = ""
        for arg in args:
            printable = printable + str(arg)+" "
        if kwargs and len(kwargs):
            a = 1
            coma = ""
            printable = printable + "["
            for k, v in kwargs.iteritems():
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

    def load_config(self):
        """Load saved config from file ~/.vindinium/config"""
        config_parser = ConfigParser.ConfigParser()
        user_home_dir = os.path.expanduser("~")
        config_file_name = os.path.join(user_home_dir, ".vindinium", "config")
        try:
            if os.path.isfile(config_file_name):
                config_parser.read(config_file_name)
                self.config.server_url = config_parser.get("game", "server_url")
                self.config.game_mode = config_parser.get("game", "game_mode")
                self.config.map_name = config_parser.get("game", "map_name")
                self.config.key = config_parser.get("game", "key")
                self.config.number_of_games = config_parser.getint("game", "number_of_games")
                self.config.number_of_turns = config_parser.getint("game", "number_of_turns")
        except Exception as e:
            self.gui.quit_ui()
            print "Error while loading config file", config_file_name, ":", e
            quit(1)

    def save_config(self):
        """Save config to file in ~/.vindinium/config"""
        config_parser = ConfigParser.ConfigParser()
        user_home_dir = os.path.expanduser("~")
        config_file_name = os.path.join(user_home_dir, ".vindinium", "config")
        try:
            if not os.path.isdir(os.path.join(user_home_dir, ".vindinium")):
                os.makedirs(os.path.join(user_home_dir, ".vindinium"))
            config_parser.add_section("game")
            with open(config_file_name, "w") as config_file:
                for key, value in self.config.__dict__.items():
                    config_parser.set("game", key, value)
                config_parser.write(config_file)
        except Exception as e:
            self.gui.quit_ui()
            print "Error  while saving config file", config_file_name, ":", e
            quit(1)

    def start_ui(self):
        """ Start the curses UI"""
        self.gui = ui.tui()
        choice = self.gui.ask_main_menu()
        if choice == '1':
            # Load config then play game
            self.load_config()
            self.gui.draw_game_windows()
            self.play()
        elif choice == '2':
            # Setup game
            choice = self.gui.ask_game_mode()
            if choice == '1':
                # Arena mode config
                self.config.game_mode = "arena"
                self.config.number_of_games = self.gui.ask_number_games()
            elif choice == '2':
                # Training mode config
                self.config.game_mode = "training"
                self.config.number_of_turns = self.gui.ask_number_turns()
                self.config.map_name = "m"+str(self.gui.ask_map())
            self.config.server_url = self.gui.ask_server_url(self.config.game_mode)
            self.config.key = self.gui.ask_key(self.config.game_mode)
            if self.gui.ask_save_config():
                self.save_config()
            if self.gui.ask_play_game():
                # Start game U.I
                self.gui.draw_game_windows()
                # Launch game
                self.play()
            else:
                self.start_ui()
        elif choice == '3':
            # Load game from file
            game_file_path = self.gui.ask_game_file_path()
            self.gui.quit_ui()
            print game_file_path, len(game_file_path)
            exit(0)
        elif choice == '4':
            # Load game from URL
            game_file_url = self.gui.ask_game_file_url()
            self.gui.quit_ui()
            print game_file_url, len(game_file_url)
            exit(0)
        elif choice == '5':
            # quit
            self.gui.quit_ui()
            exit(0)

    def play(self):
        """ Play all games """
        for i in range(self.config.number_of_games):
            # start a new game
            if self.bot.running:
                self.start_game()
                self._print("Game finished: "+str(i+1)+"/"+str(self.config.number_of_games))
        if self.gui.running and self.gui.help_win:
            self.gui.ask_quit()

    def start_game(self):
        """Starts a game with all the required parameters"""
        self.running = True
        # Default move is no move !
        direction = "Stay"
        # Create a requests session that will be used throughout the game
        self.session = requests.session()
        if self.config.game_mode == 'arena':
            self._print('Connecting and waiting for other players to join...')
        try:
            # Get the initial state
            self.state = self.get_new_game_state()
            self._print("Playing at: " + self.state['viewUrl'])
        except Exception as e:
            self._print("Error: Please verify your settings.")
            self._print("Settings:", self.config.__dict__)
            self._print("Game state:", self.state)
            self.running = False
            self.gui.ask_quit()
            quit(0)

        for i in range(self.config.number_of_turns + 1):
            if self.running:
                # Choose a move
                self.start_time = time.time()
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
                        self.display_game()
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
                    self.game_url = self.state['playUrl']
                    self.state = self.send_move(direction)
        # Clean up the session
        self.session.close()

    def get_new_game_state(self):
        """Get a JSON from the server containing the current state of the game"""
        if self.config.game_mode == 'training':
            # Don't pass the 'map' parameter if no map has been selected
            if len(self.config.map_name) > 0:
                params = {'key': self.config.key, 'turns': self.config.number_of_turns, 'map': self.config.map_name}
            else:
                params = {'key': self.config.key, 'turns': self.config.number_of_turns}
            api_endpoint = '/api/training'
        elif self.config.game_mode == 'arena':
            params = {'key': self.config.key}
            api_endpoint = '/api/arena'
        # Wait for 10 minutes
        r = self.session.post(self.config.server_url + api_endpoint, params, timeout=10*60)
        if r.status_code == 200:
            return r.json()
        else:
            self._print("Error when creating the game:", str(r.status_code))
            self.running = False
            self._print(r.text)

    def is_game_over(self, state):
        """Return True if game defined by state is over"""
        try:
            return state['game']['finished']
        except Exception:
            return True

    def send_move(self, direction):
        """Send a move to the server
        Moves can be one of: 'Stay', 'North', 'South', 'East', 'West'"""
        try:
            r = self.session.post(self.game_url, {'dir': direction}, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            else:
                self._print("Error HTTP ", str(r.status_code), ": ", r.text)
                self.running = False
                return {'game': {'finished': True}}
        except requests.exceptions.RequestException as e:
            self._print("Error at client.move;", str(e))
            self.running = False
            return {'game': {'finished': True}}

    def display_game(self):
        """Display game data on the U.I"""
        if not self.gui.paused:
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
            elapsed = round(time.time() - self.start_time, 3)
            self.gui.display_elapsed(elapsed)
            self.gui.refresh()

if __name__ == "__main__":
    client = Client()
    if len(sys.argv) == 1:
        # Go for interactive setup
        client.start_ui()
    elif len(sys.argv) < 3 or sys.argv[1] == "--help":
        print "Usage: %s <key> <[training|arena]> <number-of-games|number-of-turns> [server-url]" % (sys.argv[0])
        print "or: %s " % (sys.argv[0])
        print 'Example: %s mySecretKey training 20' % (sys.argv[0])
        exit(0)
    elif len(sys.argv) > 3:
        client.config.key = sys.argv[1]
        client.config.game_mode = sys.argv[2]
        if client.config.game_mode == "training":
            client.config.number_of_games = 1
            client.config.number_of_turns = int(sys.argv[3])
        else:
            client.config.number_of_games = int(sys.argv[3])
            client.config.number_of_turns = 300  # Ignored in arena mode
        if len(sys.argv) == 5:
            client.config.server_url = sys.argv[4]
        # Go for playing according to sys.argv
        # Do not use interactive setup

        client.start_ui()
        client.gui.draw_game_windows()
        client.play()
