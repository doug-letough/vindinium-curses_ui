#!/usr/bin/env python
# -*- coding: utf-8 -*-


from game import Game
import ai


DIRS = ["North", "East", "South", "West", "Stay"]
ACTIONS = ["Go mine", "Go beer", "Go enemy"]


class Curses_ui_bot:
    """THis is your bot"""
    def __init__(self):
        self.running = True
        self.state = {}
        self.game = None
        self.last_mine_count = 0
        self.last_gold = 0
        self.last_life = 0
        self.hero_move = None
        self.hero_last_move = None
        self.action = None
        self.last_action = None
        self.path_to_goal = []
        self.decision = []
        self.nearest_enemy_pos = None
        self.nearest_mine_pos = None
        self.nearest_tavern_pos = None
        self.last_nearest_enemy_pos = None
        self.last_nearest_mine_pos = None
        self.last_nearest_tavern_pos = None
        self.last_pos = None
        # The A.I, Skynet's rising !
        self.ai = ai.AI()

    def move(self, state):
        """Return store data provided by A.I
        and return selected move"""
        self.state = state        
        # Store status for later report
        try:
            self.hero_last_move = self.hero_move
            self.last_life = self.game.hero.life
            self.last_action = self.action
            self.last_gold = self.game.hero.gold
            self.last_mine_count = self.game.hero.mine_count
            self.last_pos = self.game.hero.pos
            self.last_nearest_enemy_pos = self.nearest_enemy_pos
            self.last_nearest_mine_pos = self.nearest_mine_pos
            self.last_nearest_tavern_pos = self.nearest_tavern_pos
        except AttributeError:
            # First move has no previous move
            pass
        self.game = Game(self.state)
        
        ################################################################
        # Put your call to AI code here
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

        return self.hero_move

    def process_game(self, state):
        """Process state data (for replay mode)"""
        self.state = state
        try:
            self.hero_last_move = self.hero_move
            self.last_life = self.game.hero.life
            self.last_action = self.action
            self.last_gold = self.game.hero.gold
            self.last_mine_count = self.game.hero.mine_count
            self.last_nearest_enemy_pos = self.nearest_enemy_pos
            self.last_nearest_mine_pos = self.nearest_mine_pos
            self.last_nearest_tavern_pos = self.nearest_tavern_pos
        except AttributeError:
            # First move has no previous move and no game
            pass
        self.game = Game(self.state)
        
