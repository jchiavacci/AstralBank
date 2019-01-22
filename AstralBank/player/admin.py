from django.contrib import admin

from .models import Player, Character

admin.site.register(Character)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'points', 'active')
