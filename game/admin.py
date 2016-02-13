from django.contrib import admin

from models import Game


class GameAdmin(admin.ModelAdmin):
    list_display = ('position', 'bomb', 'wall', 'status', 'no', 'turn', 'times', 'start', 'left')

admin.site.register(Game, GameAdmin)
