# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponseRedirect

from lobby.models import Player, Room


def index(request):
    return render_to_response('index.html', locals())


def allot(request):
    if not (request.method == 'POST'):
        return HttpResponse('not post')
    if 'uid' in request.session:
        player = Player.objects.get(id=int(request.session.get('uid')))
    else:
        player = Player()
        player.name = request.POST.get('name')
        player.save()
    request.session['uid'] = player.id
    request.session.set_expiry(60)
    return HttpResponse(json.dumps({'uid': player.id, 'name': player.name, 'session': request.session.get_expiry_age()}))


def hall(request):
    if not ('uid' in request.session):
        return HttpResponse('Uid is Invalid')
    info = {}
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
    return HttpResponse(json.dumps(info))


def room(request):
    if not ('uid' in request.session):
        return HttpResponse('Uid is Invalid')
    if not (request.method == 'POST'):
        return HttpResponse('not post')
    host = request.POST.get('host')
    info = {}
    item = Room.objects.get(host=host)
    info['name'] = Player.find_name(item.host)
    info['host'] = item.host
    info['num'] = item.num
    info['length'] = item.length
    info['capacity'] = item.capacity
    info['energy'] = item.energy
    info['players'] = item.members.split(';')
    return HttpResponse(json.dumps(info))


def host_room(request):
    if not ('uid' in request.session):
        return HttpResponse('Uid is Invalid')
    uid = request.session.get('uid')
    player = Player.objects.get(id=uid)
    if not (player.status == "Idle"):
        return HttpResponse("you are not idle")
    item = Room()
    item.host = uid
    item.members = item.host
    item.save()
    player.status = "Host"
    player.save()
    return HttpResponseRedirect('/hall/')


def enter_room(request):
    if not ('uid' in request.session):
        return HttpResponse()
    if not (request.method == 'POST'):
        return json.dumps('not post')
    uid = request.session.get('uid')
    player = Player.objects.get(id=uid)
    if not (player.status == "Idle"):
        return HttpResponse("you are not idle")
    host = request.POST.get('host')
    item = Room.objects.get(host=host)
    if item:
        if item.capacity > item.num:
            item.num += 1
            item.members += ";" + str(uid)
            item.save()

            player.status = "Indoor"
            player.save()
            return HttpResponseRedirect('/hall/')
    return HttpResponse('room no exist or room is full')


def leave_room(request):
    if not ('uid' in request.session):
        return HttpResponse('Uid is Invalid')
    if not (request.method == 'POST'):
        return json.dumps('not post')
    uid = request.session.get('uid')
    player = Player.objects.get(id=uid)
    if not (player.status == "Indoor" or player.status == "Host"):
        return HttpResponse("you are not Indoor")
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
    return HttpResponse('/hall/')


def change_room(request):
    if not ('uid' in request.session):
        return HttpResponse('Uid is Invalid')
    if not (request.method == 'POST'):
        return json.dumps('not post')
    uid = request.session.get('uid')
    player = Player.objects.get(id=uid)
    if not (player.status == "Host"):
        return HttpResponse("you are not Host")
    host = request.POST.get('host')
    item = Room.objects.get(host=host)
    item.capacity = int(request.POST.get('capacity'))
    item.length = int(request.POST.get('length'))
    item.energy = int(request.POST.get('energy'))
    item.save()
    return HttpResponse('/hall/')







