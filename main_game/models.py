# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

from django.db import models
# Took reference from https://www.youtube.com/watch?v=5d1CfnYT-KM
# https://www.youtube.com/watch?v=5xnZW7lZTDY
# https://www.youtube.com/watch?v=uDB723bqoPA
# https://www.youtube.com/watch?v=o-kx4Vf0DvQ
# Create your models here.
class GameMap(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()
    num_bombs = models.IntegerField()
    name = models.CharField(max_length=128)
    data = models.CharField(max_length=10000)

    # Mark a coordinate as clicked
    def mark(self, x, y):
        contents = self.read_content(x, y)

        if contents == 'B':
            return -1
        elif contents == 'E':
            num_bombs = self.count_adj_bombs(x, y)
            self.change_content(x, y, str(num_bombs))
            return num_bombs

    # Perform chain reaction of supers to find all revealed coords
    def compile_empties(self, x, y):
        empties = set(self._get_adj_empties(x, y))
        supers = self._get_unmarked_supers(empties)

        while supers:
            group = supers.pop()
            new_empties = self._get_adj_empties(group[0], group[1])
            new_supers = self._get_unmarked_supers(new_empties)
            supers = supers.union(new_supers)
            empties = empties.union(new_empties)
            self.change_content(group[0], group[1], str(group[2]))

        return list(empties)

    def _is_unmarked_super(self, x, y):
        bombs = self.count_adj_bombs(x, y)
        content = self.read_content(x, y)
        if bombs == 0 and content == 'E':
            return True
        return False

    # Get all the supers from a list that aren't yet marked
    def _get_unmarked_supers(self, superclears):
        supers = set([])
        for group in superclears:
            if group[2] == 0 and self.read_content(group[0], group[1]) == 'E':
                supers.add(group)
        return supers

    # Get all empty spots adjacent to coordinate
    def _get_adj_empties(self, x, y):
        bombs = self.count_adj_bombs(x, y)
        empties = [(x, y, bombs)]
        coords = self.build_adj_coords(x, y)

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= self.width
            out_of_bounds_y = pair[1] < 0 or pair[1] >= self.height

            if out_of_bounds_x or out_of_bounds_y:
                continue

            bombs = self.count_adj_bombs(pair[0], pair[1])
            pair.append(bombs)
            empties.append(tuple(pair))

            if bombs != 0:
                self.change_content(pair[0], pair[1], str(bombs))

        return empties

    # Perform initial map generation
    def initialize_map(self):
        data = []

        # Make empty map
        for i in range(self.width * self.height):
            data.append('E')
        self.data = "".join(data)

        # Place the bombs
        for i in range(self.num_bombs):
            self.put_bomb_in_random_places()

    # Adding Bomb to random places of Data
    def put_bomb_in_random_places(self):
        is_set = False

        while not is_set:
            randx = randint(0, self.width - 1)
            randy = randint(0, self.height - 1)

            if self.read_content(randx, randy) == 'E':
                self.change_content(randx, randy, 'B')
                is_set = True

    # Get the contents of a single space on the map
    def read_content(self, x, y):
        index = self.get_index_of_data(x, y)
        c = self.data[index]
        return c

    # Change the contents of a single space on the map
    def change_content(self, x, y, new_content):
        index = self.get_index_of_data(x, y)
        data = list(self.data)
        data[index] = new_content
        self.data = "".join(data)

    # Transform x, y coordinate into index in the data field
    def get_index_of_data(self, x, y):
        z = self.width * y
        index = z + x
        return index

    # Build coordinates array
    def build_adj_coords(self, x, y):
        coords = [
            [x - 1, y],
            [x - 1, y - 1],
            [x, y - 1],
            [x + 1, y - 1],
            [x + 1, y],
            [x + 1, y + 1],
            [x, y + 1],
            [x - 1, y + 1]
        ]
        return coords

    # Count the number of bombs adjacent to coordinate
    def count_adj_bombs(self, x, y):
        count = 0
        coords = self.build_adj_coords(x, y)

        stack = []

        # If this space is a bomb, just say so
        if self.read_content(x, y) == 'B':
            return -1

        for pair in coords:
            out_of_bounds_x = pair[0] < 0 or pair[0] >= self.width
            out_of_bounds_y = pair[1] < 0 or pair[1] >= self.height

            if out_of_bounds_x or out_of_bounds_y:
                continue

            if self.read_content(pair[0], pair[1]) == 'B':
                count += 1

        return count

    # Get a matrix version of the map
    def get_map_matrix(self, type):

        matrix = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                content = self.read_content(j, i)

                # a revealing matrix will show everything
                if type != 'reveal':
                    if content == 'B' or content == 'E':
                        content = ''

                else:
                    if content != 'B':
                        content = self.count_adj_bombs(j, i)

                row.append(content)
            matrix.append(row)

        return matrix

    # Determine whether game has been won
    def check_for_win(self):
        if not 'E' in self.data:
            return True
        return False
