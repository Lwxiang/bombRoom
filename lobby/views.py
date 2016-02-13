# -*- coding: utf-8 -*-
import json
import random

from django.http import HttpResponse
from django.shortcuts import render_to_response

from lobby.models import Player, Room
from game.views import game_init


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
                info['name'] = Player.find_name(item.host)
                info['host'] = item.host
                info['num'] = item.num
                info['length'] = item.length
                info['capacity'] = item.capacity
                info['energy'] = item.energy
                info['players'] = item.members.split(';')
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
        uid = int(request.session.get('uid'))
        try:
            player = Player.objects.get(id=uid)
            if not (player.status == "Idle"):
                status = "5"
            else:
                item = Room()
                item.host = uid
                item.members = item.host
                item.game = game_init()
                item.save()
                player.status = "Host"
                player.where = uid
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
                    item = Room.objects.get(host=host)
                    flag = True
                    if item:
                        if item.capacity > item.num:
                            item.num += 1
                            item.members += ";" + str(uid)
                            item.save()

                            player.status = "Indoor"
                            player.where = host
                            player.face = random.randint(0, 3)
                            player.save()
                            flag = False
                    if flag:
                        status = "6"
                    else:
                        status = "1"

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
                status = "5"
            else:
                host = request.POST.get('host')
                item = Room.objects.get(host=host)
                members = item.members.split(';')
                sequence = ""
                flag = False
                for i in range(0, len(members)):
                    if int(members[i]) != uid:
                        if flag:
                            sequence += ';'
                        sequence += str(members[i])
                        flag = True
                item.members = sequence
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
                host = request.POST.get('host')
                item = Room.objects.get(host=host)
                item.capacity = int(request.POST.get('capacity'))
                item.length = int(request.POST.get('length'))
                item.energy = int(request.POST.get('energy'))
                item.save()
                game = item.game
                game.bomb = '0' * item.length * item.length
                game.wall = '0' * item.length * item.length
                game.save()
                item.save()
                status = "1"
    response = HttpResponse(json.dumps({'status': status, 'info': info}))
    return response







