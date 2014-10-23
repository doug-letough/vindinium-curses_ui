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
import ast

TIMEOUT = 15


class Config:
    def __init__(self, game_mode="training", server_url="http://vindinium.org",
                        number_of_games=1, number_of_turns=300, map_name="m3", key=None):
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
        self.states = []
        self.delay = 0.5  # Delay in s between turns in replay mode
        self.victory = 0 
        self.time_out = 0

    def pprint(self, *args, **kwargs):
        """Display args in the bot gui or
        print it if no gui is available
        For debugging purpose consider using self.gui.append_log()
        """
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
                self.gui.refresh()
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
        except (IOError, ConfigParser.Error) as e:
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
        except (IOError, ConfigParser.Error) as e:
            self.gui.quit_ui()
            print "Error  while saving config file", config_file_name, ":", e
            quit(1)

    def load_game(self, game_file_name):
        """Load saved game from file"""
        # Reset our bot and self.states
        self.states = []
        try:
            with open(game_file_name, "r") as game_file:
                for line in game_file.readlines():
                    if len(line.strip(chr(0)).strip()) > 0:
                        self.states.append(ast.literal_eval(line))
            self.state = self.states[0]
        except (IOError, IndexError) as e:
            self.gui.quit_ui()
            print "Error while loading game file", game_file_name, ":", e
            quit(1)

    def save_game(self):
        """Save game to file in ~/.vindinium/save/<game ID>"""
        user_home_dir = os.path.expanduser("~")
        try:
            # Get game_id from  game sate
            game_id = self.state['game']["id"]
        except KeyError:
            try:
                # State has not been downloaded
                # Try to get game_id from last state saved if any
                game_id = self.states[0]['game']["id"]
            except IndexError:
                self.pprint("No states available for this game, unable to save game.")
        game_file_name = os.path.join(user_home_dir, ".vindinium", "save", game_id)
        try:
            if not os.path.isdir(os.path.join(user_home_dir, ".vindinium", "save")):
                os.makedirs(os.path.join(user_home_dir, ".vindinium", "save"))
            with open(game_file_name, "w") as game_file:
                for state in self.states:
                    game_file.write(str(state)+"\n")
            self.pprint("Game saved: "+game_file_name)
        except IOError as e:
            self.gui.append_log("Error  while saving game file", game_file_name, ":", e)

    def download_game_file(self, game_file_url):
        # I will treat no other forbidden char than space char.
        game_file_url = game_file_url.replace(" ", "%20")
        # 
        # FIXME :
        # 
        # Game file available online at http://vindinium.org/events/<gameId>
        # are not parsable by ast.literal_eval() ????
        #
        # self.session = requests.session()
        # response = self.session.get(game_file_url, timeout=10*60)
        # if response.status_code == 200:
        #    for line in response.text:
        #        line = line.strip(chr(0)).strip()
        #        if len(line) > 0:
        #            self.states.append(ast.literal_eval(line)) <<< Here is the problem
        #
        # MUST TRY:
        # games=[json.loads(line[6:]) for line in requests.get(game_file_url).content.splitlines() if line.startswith("data: ")]
        #           
        self.gui.quit_ui()
        os.system('cls' if os.name == 'nt' else 'clear')
        print "********************************************************"
        print "*            Feature not available yet.                *"
        print "*           Please wait for U.I restart                *"
        print "********************************************************"
        for i in reversed(range(1, 6)):
            print i
            time.sleep(1)
        self.start_ui()

    def start_ui(self):
        """Start the curses UI"""
        self.bot = Curses_ui_bot()
        self.running = True
        self.game_url = None
        self.states = []
        self.state = None
        self.gui = ui.tui()
        choice = self.gui.ask_main_menu()
        if choice == '1':
            # Load config then play game
            self.load_config()
            self.gui.draw_game_windows()
            self.play()
        elif choice == '2':
            # Setup game
            self.config = Config()
            choice = self.gui.ask_game_mode()
            if choice == '1':
                # Arena mode config
                self.config.game_mode = "arena"
                self.config.number_of_turns = 300
                self.config.number_of_games = self.gui.ask_number_games()
            elif choice == '2':
                # Training mode config
                self.config.game_mode = "training"
                self.config.number_of_games = 1
                self.config.number_of_turns = self.gui.ask_number_turns()
                self.config.map_name = "m"+str(self.gui.ask_map())
            self.config.server_url = self.gui.ask_server_url(self.config.game_mode)
            self.config.key = self.gui.ask_key(self.config.game_mode)
            if self.gui.ask_save_config():
                self.save_config()
            if self.gui.ask_play_game():
                self.gui.draw_game_windows()
                self.play()
            else:
                self.start_ui()
        elif choice == '3':
            # Load game from file
            game_file_name = self.gui.ask_game_file_path()
            self.load_game(game_file_name)
            self.gui.draw_game_windows()
            self.replay()
        elif choice == '4':
            # Load game from URL
            game_file_url = self.gui.ask_game_file_url()
            self.download_game_file(game_file_url)
            self.gui.draw_game_windows()
            self.replay()
        elif choice == '5':
            # quit
            self.gui.quit_ui()
            exit(0)
        if self.gui.running and self.gui.help_win:
            key = None
            while key != 'm':
                key = self.gui.ask_quit()
                if key == 's':
                    self.save_game()
                elif key == 'r':
                    self.replay()
        self.gui.clear()
        self.start_ui()

    def play(self):
        """Play all games"""
        self.victory = 0
        self.time_out = 0
        for i in range(self.config.number_of_games):
            # start a new game
            if self.bot.running:
                self.start_game()
                gold = 0
                winner = ("Noone", -1)
                for player in self.bot.game.heroes:
                    if int(player.gold) > gold:
                        winner = (player.name, player.bot_id)
                        gold = int(player.gold)
                if winner[1] == self.bot.game.hero.bot_id:
                    self.victory += 1
                self.pprint("* " + winner[0] + " wins. ******************")
                self.gui.display_summary(str(i+1) + "/" + str(self.config.number_of_games),
                                        str(self.victory) + "/" + str(i+1),
                                        str(self.time_out) + "/" + str(i+1))
                self.pprint("Game finished: "+ str(i+1) + "/" + str(self.config.number_of_games))

    def replay(self):
        """Replay last game"""
        # Restart with a new bot
        self.bot = Curses_ui_bot()
        for i in range(self.config.number_of_games):
            # start a new game
            if self.bot.running:
                self.restart_game()
                gold = 0
                winner = "Noone"
                for player in self.bot.game.heroes:
                    if int(player.gold) > gold:
                        winner = player.name
                        gold = int(player.gold)
                self.pprint("**** " + winner + " wins. ****")
                self.pprint("Game finished: "+str(i+1)+"/"+str(self.config.number_of_games))

    def start_game(self):
        """Starts a game with all the required parameters"""
        self.running = True
        # Delete prévious game states
        self.states = []
        # Restart game with brand new bot
        self.bot = Curses_ui_bot()
        # Default move is no move !
        direction = "Stay"
        # Create a requests session that will be used throughout the game
        self.pprint('Connecting...')
        self.session = requests.session()
        if self.config.game_mode == 'arena':
            self.pprint('Waiting for other players to join...')
        try:
            # Get the initial state
            # May raise error if self.get_new_state() returns
            # no data or inconsistent data (network problem)
            self.state = self.get_new_game_state()
            self.states.append(self.state)
            self.pprint("Playing at: " + self.state['viewUrl'])
        except (KeyError, TypeError) as e:
            # We can not play a game without a state
            self.pprint("Error: Please verify your settings.")
            self.pprint("Settings:", self.config.__dict__)
            self.running = False
            return
        for i in range(self.config.number_of_turns + 1):
            if self.running:
                # Choose a move
                self.start_time = time.time()
                try:
                    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.read(1)
                        if line.strip() == "q":
                            self.running = False
                            self.bot.running = False
                            break
                        elif line.strip() == "p":
                            self.gui.pause()
                        elif line.strip() == "s":
                            self.save_game()
                    if self.bot.running:
                        direction = self.bot.move(self.state)
                        self.display_game()
                except Exception as e:
                    # Super error trap !
                    if self.gui.log_win:
                        self.pprint("Error at client.start_game:", str(e))
                        self.pprint("If your code or your settings are not responsible of this error, please report this error to:")
                        self.pprint("doug.letough@free.fr.")
                        self.gui.pause()
                    self.running = False
                    return
                if not self.is_game_over():
                    # Send the move and receive the updated game state
                    self.game_url = self.state['playUrl']
                    self.state = self.send_move(direction)
                    self.states.append(self.state)
        # Clean up the session
        self.session.close()

    def restart_game(self):
        """Starts a game with all the required parameters"""
        self.running = True
        try:
            # Get the initial state
            self.state = self.states[0]
            self.pprint("Replaying: " + self.state['viewUrl'])
        except (IndexError, KeyError) as e:
            self.pprint("Error while trying to replay game.")
            self.pprint("Game states length:", len(self.states))
            self.running = False
            return
        self.gui.draw_help_win()
        for state in self.states:
            self.state = state
            if self.running:
                # Choose a move
                self.start_time = time.time()
                try:
                    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.read(1)
                        if line.strip() == "q":
                            self.running = False
                            self.bot.running = False
                            break
                        elif line.strip() == "p":
                            self.gui.pause()
                        elif line.strip() == "s":
                            self.save_game()
                    if self.bot.running:
                        self.bot.process_game(state)
                        self.display_game()
                except Exception, e:
                    if self.gui.log_win:
                        self.pprint("Error at client.restart_game:", str(e))
                        self.pprint("If your code or your settings are not responsible of this error, please report this error to:")
                        self.pprint("doug.letough@free.fr.")
                        self.gui.pause()
                    self.running = False
                    return
                if not self.is_game_over():
                    # Replay next turn
                    self.game_url = state['playUrl']
                    time.sleep(self.delay)

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
        try:
            r = self.session.post(self.config.server_url + api_endpoint, params, timeout=10*60)
            if r.status_code == 200:
                return r.json()
            else:
                self.pprint("Error when creating the game:", str(r.status_code))
                self.running = False
                self.pprint(r.text)
        except requests.ConnectionError as e:
            self.pprint("Error when creating the game:", e)
            self.running = False

    def is_game_over(self):
        """Return True if game defined by state is over"""
        try:
            return self.state['game']['finished']
        except (TypeError, KeyError):
            return True

    def send_move(self, direction):
        """Send a move to the server
        Moves can be one of: 'Stay', 'North', 'South', 'East', 'West'"""
        try:
            response = self.session.post(self.game_url, {'dir': direction}, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                self.pprint("Error HTTP ", str(response.status_code), ": ", response.text)
                self.time_out += 1
                self.running = False
                return {'game': {'finished': True}}
        except requests.exceptions.RequestException as e:
            self.pprint("Error at client.move;", str(e))
            self.running = False
            return {'game': {'finished': True}}

    def display_game(self):
        """Display game data on the U.I"""
        if not self.gui.paused:
            # Draw the map
            self.gui.draw_map(self.bot.game.board_map, self.bot.path_to_goal, self.bot.game.heroes)
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
            # Print informations about other players
            self.gui.display_heroes(self.bot.game.heroes, self.bot.game.hero.bot_id)
            # Print a *list of tuples* representing what you think can be usefull
            # i.e an heuristic result
            self.gui.display_decision(self.bot.decision)
            # Print *list of tuples* representing
            # the estimated path to reach the goal if any.
            # If too long the path will be truncated to fit
            # in the display
            self.gui.display_path(self.bot.path_to_goal)
            # Move cursor along the time line (cost cpu time)
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
