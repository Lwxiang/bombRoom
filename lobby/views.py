# -*- coding: utf-8 -*-
import json
import random

from django.http import HttpResponse
from django.shortcuts import render_to_response

from lobby.models import Player, Room
from game.views import game_init, color


def index(request):
    return render_to_response('index.html', locals())


def allot(request):
    info = {}
    if not (request.method == 'POST'):
        status = "2"
    else:
        if 'uid' in request.session:
            # player = Player.objects.get(id=int(request.session.get('uid')))
            pass

        player = Player()
        player.name = request.POST.get('name')
        player.save()
        request.session['uid'] = player.id

        info = {'uid': player.id, 'name': player.name, 'session': request.session.get_expiry_age()}
        status = "1"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def hall(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if request.method == 'GET':
            info['total'] = Room.get_total()
            info['rooms'] = {}
            if info['total']:
                step = 0
                for item in Room.objects.all():
                    step += 1
                    info['rooms'][step] = {}
                    info['rooms'][step]['name'] = Player.find_name(item.host)
                    info['rooms'][step]['host'] = item.host
                    info['rooms'][step]['num'] = item.num
                    info['rooms'][step]['length'] = item.length
                    info['rooms'][step]['capacity'] = item.capacity
                    info['rooms'][step]['energy'] = item.energy
        status = "1"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def room(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = '2'
        else:
            try:
                host = request.POST.get('host')
                if not host:
                    raise Room.DoesNotExist
                info = {}
                item = Room.objects.get(host=int(host))
                game = item.game
                info['start'] = game.start
                info['name'] = Player.find_name(item.host)
                info['host'] = item.host
                info['num'] = item.num
                info['length'] = item.length
                info['capacity'] = item.capacity
                info['energy'] = item.energy
                info['uids'] = item.members.split(';')
                info['players'] = item.names.split(';')
                info['colors'] = item.colors.split(';')
                status = "1"
            except Room.DoesNotExist:
                status = "5"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def host_room(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        try:
            uid = request.session.get('uid')
            if not uid:
                raise Player.DoesNotExist
            player = Player.objects.get(id=int(uid))
            if not (player.status == "Idle"):
                status = "5"
            else:
                item = Room()
                item.host = int(uid)
                item.members = item.host
                item.names = player.name
                item.game = game_init()
                item.colors = item.game.colors.split(';')[0]
                item.save()
                player.status = "Host"
                player.where = int(uid)
                player.face = random.randint(0, 3)
                player.save()
                status = "1"

        except Player.DoesNotExist:
            status = "4"

    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def enter_room(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = "2"
        else:
            try:
                uid = request.session.get('uid')
                player = Player.objects.get(id=uid)
                if not (player.status == "Idle"):
                    status = "5"
                else:
                    host = request.POST.get('host')
                    try:
                        item = Room.objects.get(host=host)
                        if item.game.start:
                            status = "7"
                        elif item.capacity > item.num:
                            item.num += 1
                            item.members += ";" + str(uid)
                            item.names += ";" + player.name
                            item.colors = ";".join(item.game.colors.split(';')[:item.num])
                            item.save()

                            player.status = "Indoor"
                            player.where = host
                            player.face = random.randint(0, 3)
                            player.save()
                            status = "1"
                        else:
                            status = "6"
                    except Room.DoesNotExist:
                        status = "7"

            except Player.DoesNotExist:
                status = "4"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def leave_room(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = "2"
        else:
            uid = request.session.get('uid')
            player = Player.objects.get(id=uid)
            if not (player.status == "Indoor" or player.status == "Host"):
                status = "10"
            else:
                host = request.POST.get('host')
                item = Room.objects.get(host=host)
                members = item.members.split(';')
                names = item.names.split(';')
                colors = item.colors.split(';')
                seq_members = ""
                seq_names = ""
                seq_colors = ""
                flag = False
                for i in range(0, len(members)):
                    if int(members[i]) != uid:
                        if flag:
                            seq_members += ';'
                            seq_names += ';'
                            seq_colors += ';'
                        seq_members += str(members[i])
                        seq_names += names[i]
                        seq_colors += colors[i]
                        flag = True
                item.members = seq_members
                item.names = seq_names
                item.colors = seq_colors
                item.num -= 1
                item.save()
                if item.num == 0:
                    item.delete()
                else:
                    if item.host == int(uid):
                        item.host = int(item.members.split(';')[0])
                    item.save()
                player.status = "Idle"
                player.save()
                status = "1"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def change_room(request):
    info = {}
    if not ('uid' in request.session):
        status = "4"
    else:
        if not (request.method == 'POST'):
            status = "2"
        else:
            uid = request.session.get('uid')
            player = Player.objects.get(id=uid)
            if not (player.status == "Host"):
                status = "5"
            else:
                try:
                    host = request.POST.get('host')
                    item = Room.objects.get(host=host)
                    item.capacity = int(request.POST.get('capacity'))
                    item.length = int(request.POST.get('length'))
                    item.energy = int(request.POST.get('energy'))
                    if item.capacity > 6 or item.length > 10 or item.energy > 6:
                        raise Room.DoesNotExist
                    item.save()
                    game = item.game
                    game.bomb = '0' * item.length * item.length
                    game.wall = '0' * item.length * item.length
                    game.save()
                    item.save()
                    status = "1"
                except Room.DoesNotExist:
                    status = "11"

    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response


def restart_server(request):
    response = 'refuse'
    if request.method == "POST":
        import os, sys
        url = os.path.dirname(sys.path[0])
        os.system(url + "/bombRoom/restart.sh")
        response = 'ok'
    return HttpResponse(response)





