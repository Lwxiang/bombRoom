# -*- coding: utf-8 -*-
import json
import random

from django.http import HttpResponse

from game.models import Game
from lobby.models import Player, Room

color = ("#FF0000", "#458B00", "#6959CD", "#FFFF00", "#97FFFF", "#CD2990")


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
    info = {}
    if not ('uid' in request.session):
        status = '4'
    else:
        if not (request.method == 'GET'):
            status = "3"
        else:
            uid = request.session.get('uid')
            info['uid'] = uid
            host = uid
            room = Room.objects.get(host=host)
            members = room.members.split(';')
            for i in members:
                player = Player.objects.get(id=int(i))
                player.status = "Gaming"
                player.save()
            game = room.game
            game.start = True
            game.turn = random.randint(0, room.num - 1)
            game.times = 0
            game.left = room.num
            game.save()

            # Make the default position
            position = ""

            flag = False
            for i in range(0, room.num):
                x = random.randint(0, room.length - 1)
                y = random.randint(0, room.length - 1)
                if flag:
                    position += ';'
                flag = True
                position += str(x) + ',' + str(y)
                game.position = position
            game.save()
            status = "1"

    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    response['Access-Control-Allow-Origin'] = '*'
    return response


def wait_start(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'GET'):
            status = "3"
        else:
            uid = request.session.get('uid')
            info['uid'] = uid
            player = Player.objects.get(id=int(uid))
            game = Room.objects.get(host=player.where)
            if game.start:
                status = "1"
            else:
                status = "0"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    response['Access-Control-Allow-Origin'] = '*'
    return response


def action(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = "2"
        else:
            uid = request.session.get('uid')
            player = Player.objects.get(id=int(uid))
            room = Room.objects.get(host=player.where)
            game = room.game
            game.no += 1
            members = room.members.split(';')
            if members[game.turn] != str(uid):
                status = "5"
            else:
                move = request.POST.get('move')
                flag = False
                if move == "turnLeft()":
                    player.face = (player.face + 1) % 4
                    player.save()
                    game.status += str(game.no) + ',' + str(uid) + ',' + "tL" + ',' + str(player.face) + ',' + color[int(game.turn)] + ";"
                    game.save()
                    flag = True
                if move == "turnRight()":
                    player.face = (player.face + 4 - 1) % 4
                    player.save()
                    game.status += str(game.no) + ',' + str(uid) + ',' + "tR" + ',' + str(player.face) + ',' + color[int(game.turn)] + ";"
                    game.save()
                    flag = True
                if move == "goForward()":
                    game.status += str(game.no) + ',' + str(uid) + ',' + "gF" + ',' + str(player.face) + ',' + color[int(game.turn)] + ";"
                    game.save()
                    z = 0
                    for i in range(0, room.num):
                        if members[i] == uid:
                            z = i
                            break
                    item = game.position.split(';')
                    x = int(str(item[z]).split(',')[0])
                    y = int(str(item[z]).split(',')[1])
                    if player.face == 0:
                        x = (x + 1) % room.length
                    if player.face == 1:
                        y = (y + 1) % room.length
                    if player.face == 2:
                        x = (x - 1 + room.length) % room.length
                    if player.face == 3:
                        y = (y - 1 + room.length) % room.length
                    item[z] = str(x) + ',' + str(y)
                    game.position = ""
                    for i in range(0, room.num):
                        if i > 0:
                            game.position += ";"
                        game.position += str(item[i])
                    game.save()
                    flag = True
                if move == "putBomb()":
                    game.status += str(game.no) + ',' + str(uid) + ',' + "pB" + ',' + str(player.face) + ',' + color[int(game.turn)] + ";"
                    game.save()
                    z = 0
                    for i in range(0, room.num):
                        if members[i] == uid:
                            z = i
                            break
                    item = game.position.split(';')
                    x = int(str(item[z]).split(',')[0])
                    y = int(str(item[z]).split(',')[1])
                    bomb = game.bomb
                    get = bomb[0: x * room.length + y]
                    get += '1'
                    if x == (room.length - 1) and y == (room.length - 1):
                        get += ""
                    else:
                        get += bomb[x * room.length + y + 1: room.length * room.length]
                    game.bomb = get
                    game.save()
                    flag = True
                if move == "endTurn()":
                    game.status += str(game.no) + ',' + str(uid) + ',' + "eT" + ',' + str(player.face) + ',' + color[int(game.turn)] + ";"
                    game.times = room.energy
                    game.save()
                    flag = True
                if flag:
                    game.times += 1
                    game.save()
                    if game.times >= room.energy:
                        z = 0
                        for i in range(0, room.num):
                            if members[i] == uid:
                                z = i
                                break
                        item = game.position.split(';')
                        x = int(str(item[z]).split(',')[0])
                        y = int(str(item[z]).split(',')[1])
                        bomb = game.bomb
                        if bomb[x * room.length + y] == '1':
                            get = bomb[0: x * room.length + y]
                            get += '0'
                            if x == (room.length - 1) and y == (room.length - 1):
                                get += ""
                            else:
                                get += bomb[x * room.length + y + 1: room.length * room.length]
                            game.no += 1
                            game.status += str(game.no) + ',' + str(uid) + ',' + "dD" + ',' + color[int(game.turn)] + ";"
                            game.left -= 1
                            game.save()
                            player.alive = False
                            player.save()
                        while True:
                            game.turn = (game.turn + 1) % room.num
                            player = Player.objects.get(id=int(members[game.turn]))
                            if player.alive:
                                break
                        game.times = 0
                        game.save()
                    status = "1"
                else:
                    game.no -= 1
                    game.save()
                    status = "0"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    response['Access-Control-Allow-Origin'] = '*'
    return response


def turn_to(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'GET'):
            status = "3"
        else:
            uid = request.session.get('uid')
            player = Player.objects.get(id=int(uid))
            room = Room.objects.get(host=player.where)
            game = room.game
            members = room.members.split(';')
            if members[game.turn] == str(uid):
                status = "1"
                if game.left == 1:
                    status = "7"
            else:
                status = "0"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    response['Access-Control-Allow-Origin'] = '*'
    return response


def query(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = "2"
        else:
            uid = request.session.get('uid')
            player = Player.objects.get(id=int(uid))
            room = Room.objects.get(host=player.where)
            game = room.game
            mid = int(request.POST.get('mid'))
            seq = game.status.split(';')
            info['uid'] = uid
            info['name'] = Player.find_name(uid)
            info['data'] = []
            direction = (u'东', u'北', u'西', u'南')
            for i in range(0, len(seq) - 1):
                if i >= mid:
                    xdata = {}
                    ss = str(seq[i]).split(',')
                    xdata['mid'] = ss[0]
                    xdata['uid'] = ss[1]
                    name = Player.find_name(int(ss[1]))
                    selfs = (int(ss[1]) == int(uid))
                    word = ""
                    if ss[2] == "tL":
                        if selfs:
                            word += u" 您 向左转了身。(现在面向 " + direction[int(ss[3])]
                        else:
                            word += " " + name + u" 执行了一次操作"
                    if ss[2] == "tR":
                        if selfs:
                            word += u" 您 向右转了身。(现在面向 " + direction[int(ss[3])]
                        else:
                            word += " " + name + u" 执行了一次操作"
                    if ss[2] == "gF":
                        if selfs:
                            word += u" 您 向前走了一步(现在面向 " + direction[int(ss[3])]
                        else:
                            word += " " + name + u" 执行了一次操作"
                    if ss[2] == "pB":
                        if selfs:
                            word += u" 您 安置了一个炸弹！请注意安全！(现在面向 " + direction[int(ss[3])]
                        else:
                            word += " " + name + u" 执行了一次操作"
                    if ss[2] == "eT":
                        if selfs:
                            word += u" 您 提前结束了回合。(现在面向 " + direction[int(ss[3])]
                        else:
                            word += " " + name + u" 执行了一次操作"
                    if ss[2] == "dD":
                        if selfs:
                            word += u" 您 被炸飞了desu。输掉了游戏。"
                        else:
                            word += " " + name + u"被人炸飞了。输掉了游戏。"
                    xdata['content'] = word
                    xdata['color'] = ss[3]
                    info['data'].append(xdata)
            info['position'] = str(game.position).split(';')
            info['order_id'] = str(room.members).split(';')
            info['order_name'] = []
            for k in info['order_id']:
                info['order_name'].append(Player.find_name(int(k)))
            status = "1"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    response['Access-Control-Allow-Origin'] = '*'
    return response










