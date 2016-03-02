# -*- coding: utf-8 -*-
from django.db import models


class Game(models.Model):
    position = models.CharField(max_length=2000)
    bomb = models.CharField(max_length=2000)
    wall = models.CharField(max_length=2000)
    status = models.TextField()
    no = models.IntegerField(default=0)
    turn = models.IntegerField(default=0)
    times = models.IntegerField(default=0)
    start = models.BooleanField(default=False)
    left = models.IntegerField(default=0)
    colors = models.CharField(max_length=1000)
