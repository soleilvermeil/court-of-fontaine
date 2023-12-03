from django.contrib import admin
from .models import *


class SubstatInline(admin.TabularInline):
    model = Substat
    raw_id_fields = ['owner']
class ArtifactAdmin(admin.ModelAdmin):
    inlines = [SubstatInline]


class ArtifactInline(admin.TabularInline):
    model = Artifact
    raw_id_fields = ['owner']
class CharacterAdmin(admin.ModelAdmin):
    inlines = [ArtifactInline]


class CharacterInline(admin.TabularInline):
    model = Character
    raw_id_fields = ['owner']
class PlayerAdmin(admin.ModelAdmin):
    inlines = [CharacterInline]


admin.site.register(Player, PlayerAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Artifact, ArtifactAdmin)
admin.site.register(Substat)
