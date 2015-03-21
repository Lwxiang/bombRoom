# -*- coding: utf-8 -*-
import json
import random

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect

from game.models import Game
from lobby.models import Player, Room


def game_init():
    game = Game()

    # Make the status start
    game.no = 0
    game.status = ""
    game.turn = 0

    # Make the bomb and the wall init
    game.bomb = '0' * 4 * 4
    game.wall = '0' * 4 * 4
    game.save()
    return game


def game_start(request):
    response = HttpResponse()
    if not ('uid' in request.session):
        response.write('Uid is Invalid')
    else:
        if not (request.method == 'POST'):
            response.write('not post')
        else:
            host = request.POST.get('host')
            room = Room.objects.get(host=host)
            members = room.members.split(';')
            for i in members:
                player = Player.objects.get(id=int(i))
                player.status = "Gaming"
                player.save()
            game = room.game
            game.start = True
            game.save()

            # Make the default position
            position = ""

            flag = False
            for i in range(0, room.num):
                x = random.randint(0, room.length)
                y = random.randint(0, room.length)
                if flag:
                    position += ';'
                flag = True
                position += str(x) + ',' + str(y)


def wait_start(request):
    response = HttpResponse()
    if not ('uid' in request.session):
        response.write('Uid is Invalid')
    else:
        if not (request.method == 'GET'):
            response.write('not get')











