#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#
# Pure random A.I, you may NOT use it to win ;-)
#
########################################################################

import random


class AI:
    """Pure random A.I, you may NOT use it to win ;-)"""
    def __init__(self):
        pass

    def process(self, game):
        """Do whatever you need with the Game object game"""
        self.game = game

    def decide(self):
        """Must return a tuple containing in that order:
          1 - path_to_goal :
                  A list of coordinates representing the path to your
                 bot's goal for this turn:
                 - i.e: [(y, x) , (y, x), (y, x)]
                 where y is the vertical position from top and x the
                 horizontal position from left.

          2 - action:
                 A string that will be displayed in the 'Action' place.
                 - i.e: "Go to mine"

          3 - decision:
                 A list of tuples containing what would be useful to understand
                 the choice you're bot has made and that will be printed
                 at the 'Decision' place.

          4- hero_move:
                 A string in one of the following: West, East, North,
                 South, Stay

          5 - nearest_enemy_pos:
                 A tuple containing the nearest enenmy position (see above)

          6 - nearest_mine_pos:
                 A tuple containing the nearest enenmy position (see above)

          7 - nearest_tavern_pos:
                 A tuple containing the nearest enenmy position (see above)"""

        actions = ['mine', 'tavern', 'fight']

        decisions = {'mine': [("Mine", 30), ('Fight', 10), ('Tavern', 5)],
                    'tavern': [("Mine", 10), ('Fight', 10), ('Tavern', 50)],
                    'fight': [("Mine", 15), ('Fight', 30), ('Tavern', 10)]}

        walkable = []
        path_to_goal = []
        dirs = ["North", "East", "South", "West", "Stay"]

        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                if (y, x) not in self.game.walls_locs or \
                        (y, x) not in self.game.taverns_locs or \
                        (y, x) not in self.game.mines_locs:

                    walkable.append((y, x))

        # With such a random path, path highlighting would
        # display a random continuous line of red bullets over the map.
        first_cell = self.game.hero.pos
        path_to_goal.append(first_cell)

        for i in range(int(round(random.random()*self.game.board_size))):
            for i in range(len(walkable)):
                random.shuffle(walkable)
                if (walkable[i][0] - first_cell[0] == 1 and
                        walkable[i][1] - first_cell[1] == 0) or \
                        (walkable[i][1] - first_cell[1] == 1 and
                        walkable[i][0] - first_cell[0] == 0):
                    path_to_goal.append(walkable[i])
                    first_cell = walkable[i]
                    break

        hero_move = random.choice(dirs)
        action = random.choice(actions)
        decision = decisions[action]
        nearest_enemy_pos = random.choice(self.game.heroes).pos
        nearest_mine_pos = random.choice(self.game.mines_locs)
        nearest_tavern_pos = random.choice(self.game.mines_locs)

        return (path_to_goal,
                action,
                decision,
                hero_move,
                nearest_enemy_pos,
                nearest_mine_pos,
                nearest_tavern_pos)


if __name__ == "__main__":
    pass
