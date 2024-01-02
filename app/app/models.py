from django.db import models
from django.contrib import admin


class Player(models.Model):
    uid = models.CharField(verbose_name="UID", max_length=9, primary_key=True, unique=True, db_index=True)
    nickname = models.CharField(max_length=20)
    avatar = models.URLField(max_length=100, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nickname} ({self.uid})"


class Character(models.Model):
    name = models.CharField(max_length=20)
    owner = models.ForeignKey(Player, on_delete=models.CASCADE)
    def __str__(self):
        return f"[{self.owner}] {self.name}"


class Artifact(models.Model):
    equiptype = models.CharField(max_length=20, choices=[
        ("EQUIP_BRACER", "Flower"),
        ("EQUIP_NECKLACE", "Feather"),
        ("EQUIP_SHOES", "Sands"),
        ("EQUIP_RING", "Goblet"),
        ("EQUIP_DRESS", "Circlet"),
    ])
    level = models.IntegerField(max_length=2, default=0)
    # equiptype = models.CharField(max_length=20, choices=[
    #     ("Flower", "Flower"),
    #     ("Feather", "Feather"),
    #     ("Sands", "Sands"),
    #     ("Goblet", "Goblet"),
    #     ("Circlet", "Circlet"),
    # ])
    owner = models.ForeignKey(Character, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.owner}'s {self.equiptype}"
    

class Substat(models.Model):
    name = models.CharField(max_length=100, choices=[
        ("FIGHT_PROP_BASE_ATTACK", "Base ATK"),
        ("FIGHT_PROP_HP", "Flat HP"),
        ("FIGHT_PROP_ATTACK", "Flat ATK"),
        ("FIGHT_PROP_DEFENSE", "Flat DEF"),
        ("FIGHT_PROP_HP_PERCENT", "HP%"),
        ("FIGHT_PROP_ATTACK_PERCENT", "ATK%"),
        ("FIGHT_PROP_DEFENSE_PERCENT", "DEF%"),
        ("FIGHT_PROP_CRITICAL", "Crit RATE"),
        ("FIGHT_PROP_CRITICAL_HURT", "Crit DMG"),
        ("FIGHT_PROP_CHARGE_EFFICIENCY", "Energy Recharge"),
        ("FIGHT_PROP_HEAL_ADD", "Healing Bonus"),
        ("FIGHT_PROP_ELEMENT_MASTERY", "Elemental Mastery"),
        ("FIGHT_PROP_PHYSICAL_ADD_HURT", "Physical DMG Bonus"),
        ("FIGHT_PROP_FIRE_ADD_HURT", "Pyro DMG Bonus"),
        ("FIGHT_PROP_ELEC_ADD_HURT", "Electro DMG Bonus"),
        ("FIGHT_PROP_WATER_ADD_HURT", "Hydro DMG Bonus"),
        ("FIGHT_PROP_WIND_ADD_HURT", "Anemo DMG Bonus"),
        ("FIGHT_PROP_ICE_ADD_HURT", "Cryo DMG Bonus"),
        ("FIGHT_PROP_ROCK_ADD_HURT", "Geo DMG Bonus"),
        ("FIGHT_PROP_GRASS_ADD_HURT", "Dendro DMG Bonus"),
    ])
    value = models.DecimalField(max_digits=5, decimal_places=1)
    rolls = models.IntegerField(max_length=1, default=0)
    ismainstat = models.BooleanField(default=False)
    owner = models.ForeignKey(Artifact, related_name="substats", on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.owner} -> {self.name}"

