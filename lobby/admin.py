from django.contrib import admin

from models import Player, Room


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'where', 'face', 'alive')


class RoomAdmin(admin.ModelAdmin):
    list_display = ('host', 'members', 'num', 'capacity', 'length', 'energy')


admin.site.register(Player, PlayerAdmin)
admin.site.register(Room, RoomAdmin)
