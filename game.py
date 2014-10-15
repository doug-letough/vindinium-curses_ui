#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Hero:
    """The Hero object"""
    def __init__(self, hero):
        try:
            # Training bots have no elo or userId
            self.elo = hero['elo']
            self.user_id = hero['userId']
            self.bot_last_move = hero['lastDir']
        except KeyError:
            self.elo = 0
            self.user_id = 0
            self.last_move = None

        self.bot_id = hero['id']
        self.life = hero['life']
        self.gold = hero['gold']
        self.pos = (hero['pos']['x'], hero['pos']['y'])
        self.spawn_pos = (hero['spawnPos']['x'], hero['spawnPos']['y'])
        self.crashed = hero['crashed']
        self.mine_count = hero['mineCount']
        self.mines = []
        self.name = hero['name'].encode("utf-8")


class Game:
    """The game object that gather
    all game state informations"""
    def __init__(self, state):
        self.state = state
        self.mines = {}
        self.mines_locs = []
        self.spawn_points_locs = {}
        self.taverns_locs = []
        self.hero = None
        self.heroes = []
        self.heroes_locs = []
        self.walls_locs = []
        self.url = None
        self.turn = None
        self.max_turns = None
        self.finished = None
        self.board_size = None
        self.board_map = []

        self.process_data(self.state)

    def process_data(self, state):
        """Parse the game state"""
        self.set_url(state['viewUrl'])
        self.process_hero(state['hero'])
        self.process_game(state['game'])

    def set_url(self, url):
        """Set the game object url var"""
        self.url = url

    def process_hero(self, hero):
        """Process the hero data"""
        self.hero = Hero(hero)

    def process_game(self, game):
        """Process the game data"""
        process = {'board': self.process_board,
                    'heroes': self.process_heroes}
        self.turn = game['turn']
        self.max_turns = game['maxTurns']
        self.finished = game['finished']
        for key in game:
            if key in process:
                process[key](game[key])

    def process_board(self, board):
        """Process the board datas
            - Retrieve walls locs, tavern locs
            - Converts tiles in a displayable form"""
        self.board_size = board['size']
        tiles = board['tiles']
        map_line = ""
        char = None
        for y in range(0, len(tiles), self.board_size * 2):
            line = tiles[y:y+self.board_size*2]
            for x in range(0, len(line), 2):
                tile = line[x:x+2]
                tile_coords = (y/self.board_size/2, x/2)
                if tile[0] == " ":
                    # It's passable
                    char = " "
                elif tile[0] == "#":
                    # It's a wall
                    char = "#"
                    self.walls_locs.append(tile_coords)
                elif tile[0] == "$":
                    # It's a mine
                    char = "$"
                    self.mines_locs.append(tile_coords)
                    self.mines[tile_coords] = tile[1]
                    if tile[1] == str(self.hero.bot_id):
                        # This mine is belong to me:-)
                        self.hero.mines.append(tile_coords)
                elif tile[0] == "[":
                    # It's a tavern
                    char = "T"
                    self.taverns_locs.append(tile_coords)
                elif tile[0] == "@":
                    # It's a hero
                    char = "H"
                    if not int(tile[1]) == self.hero.bot_id:
                        # I don't want to be put in an array !
                        # I'm not a number, i'm a free bot:-)
                        self.heroes_locs.append(tile_coords)
                    else:
                        # And I want to be differenciated
                        char = "@"
                map_line = map_line + str(char)
            self.board_map.append(map_line)
            map_line = ""

    def process_heroes(self, heroes):
        """Add heroes"""
        for hero in heroes:
            self.spawn_points_locs[(hero['spawnPos']['y'], hero['spawnPos']['x'])] = hero['id']
            self.heroes.append(Hero(hero))
            # Add spawn points to map
            line = list(self.board_map[int(hero['spawnPos']['x'])])
            if line[int(hero['spawnPos']['y'])] != "@" and \
                    line[int(hero['spawnPos']['y'])] != "H":
                line[int(hero['spawnPos']['y'])] = "X"
            line = "".join(line)
            self.board_map[int(hero['spawnPos']['x'])] = line
