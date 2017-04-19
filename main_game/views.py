# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import json
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from MSRM import settings
from .models import GameMap


def index(request):
    return render(request, 'index.html', {})


def show_game(request, name):
    try:
        game_map = GameMap.objects.get(name=name)
    except GameMap.DoesNotExist:
        return redirect('/')

    data = {
        'width': game_map.width,
        'height': game_map.height,
        'title': 'Minesweeper - ' + game_map.name,
        'name': game_map.name,
        'map': game_map.get_map_matrix('hidden')
    }

    return render(request, 'home.html', data)


# Create a new game
def create_new_game(request):
    name = request.GET.get('name')

    if not re.match(r'^([0-9a-zA-Z]+)*$', name):
        return HttpResponse('no-fancy-names', status=400)

    # Check if game already exists
    if GameMap.objects.filter(name=name).count() > 0:
        return HttpResponse('game-exists', status=400)

    game_map = GameMap(
        name=name,
        width=settings.GAME_WIDTH,
        height=settings.GAME_HEIGHT,
        num_bombs=settings.NUM_BOMBS,
    )
    game_map.initialize_map()
    game_map.save()

    return HttpResponse('game-created')


# Validate Game if its already exist
def validate_game(request):
    name = request.GET.get('name')

    if GameMap.objects.filter(name=name).count() > 0:
        return HttpResponse('game-exists')

    return HttpResponse('game-doesnt-exist', status=400)


# Magic goes here validations for the position of Block
def mark(request, name):
    x = int(request.GET.get('x'))
    y = int(request.GET.get('y'))

    try:
        game_map = GameMap.objects.get(name=name)
    except GameMap.DoesNotExist:
        return HttpResponse('map-doesnt-exist', status=404)

    num_bombs = game_map.mark(x, y)
    win = game_map.check_for_win() and num_bombs != -1
    game_map.save()

    result = {}

    # Check if Bomb blast
    if num_bombs == -1:
        result['status'] = 'dead'
        result['map'] = game_map.get_map_matrix('reveal')
        game_map.delete()

    # Hit a regular space
    elif num_bombs > 0:
        result['status'] = 'clear'
        result['num_bombs'] = num_bombs

    # Hit a super space
    elif num_bombs == 0:
        result['status'] = 'superclear'
        result['num_bombs'] = num_bombs
        result['empties'] = game_map.compile_empties(x, y)
        game_map.save()

    if win:
        result['status'] = 'win'
        result['map'] = game_map.get_map_matrix('reveal')
        game_map.delete()

    return HttpResponse(json.dumps(result))
