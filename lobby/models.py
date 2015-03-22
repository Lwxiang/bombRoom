# -*- coding: utf-8 -*-
from django.db import models

from game.models import Game


class Room(models.Model):
    host = models.IntegerField(max_length=100)
    members = models.CharField(max_length=100)
    num = models.IntegerField(default=1)
    capacity = models.IntegerField(default=4)
    length = models.IntegerField(default=4)
    energy = models.IntegerField(default=3)
    game = models.ForeignKey(Game, blank=True)

    @staticmethod
    def get_total():
        if Room.objects.all():
            return len(Room.objects.all())
        else:
            return 0


class Player(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="Idle")
    where = models.IntegerField(default=0, blank=True)
    face = models.IntegerField(default=0, blank=True)
    alive = models.BooleanField(default=True)

    @staticmethod
    def find_name(uid):
        return Player.objects.get(id=int(uid)).name
