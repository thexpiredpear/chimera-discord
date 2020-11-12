import discord
import redis
import psutil
import json
from discord.ext import commands, tasks
from itertools import cycle
from test import *
from Enemy import *
import random
import time
import os
import asyncio
from urllib.parse import urlparse
import sys
import aiohttp

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix="ch ", intents=intents)
status = cycle(["TwinkiePlayz Kinda Gay", "Suffocation, a game we all can play!", "Global Thermonuclear War"])

TOKEN = os.getenv("bot-token")
url = urlparse(os.getenv('REDISCLOUD_URL'))
db = redis.Redis(host=url.hostname, port=url.port, password=url.password)
classes_list = ['Warrior', 'Mage', 'Archer', 'Rogue']
fruit_list = ['Grape', 'Mango', 'Blueberry', 'Strawberry', 'Lemon', 'Kiwi']

def fight_embed(author):
    with open("regen_stats.json") as f:
        stats = json.load(f)
    with open("player_weapons.json") as f:
        weapons = json.load(f)
    with open("class.json") as f:
        classes = json.load(f)

    name, discrim = str(author).split("#")
    nest = stats[str(name)]
    nest2 = weapons[str(name)]

    embed = discord.Embed(
        title="Battle",
        description="Battle in Chimera 1.0",
        color=discord.Color.blue()
    )
    health = "Health: "+progress_bar(nest["Health"], nest["Max Health"])
    mana = "Mana:  "+progress_bar(nest["Mana"], nest["Max Mana"])
    if classes[name] == "Warrior":
        ability = "Shield"
    elif classes[name] == "Mage":
        ability = "Spellbook"
    elif classes[name] == "Archer":
        ability = "Quiver"
    elif classes[name] == "Rogue":
        ability = "Venom"

    mana_value = percentage(nest["Mana"]/nest["Max Mana"])+" Mana - Class Ability: "+ability
    enemy_health = "Enemy: "+progress_bar(enemy.health, enemy.max_health)
    value = percentage(nest["Health"]/nest["Max Health"])+" Health - Attack: "+str(nest2["Attack"])+" - Defense: "+str(nest2["Defense"])
    enemy_value = percentage(enemy.health/enemy.max_health)+" Health - Attack: "+str(enemy.attack)+" - Defense: "+str(enemy.defense)
    embed.add_field(name=health, value=value, inline=False)
    embed.add_field(name=mana, value=mana_value, inline=False)
    embed.add_field(name=enemy_health, value=enemy_value, inline=False)
    embed.add_field(name="Choices", value="Attack, use skill")

    return embed

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    change_status.start()
    print_to_stdout("Bot ready")

@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@client.command(aliases=["create"])
async def create_profile(ctx, profile_class=None):
    if profile_class == None:
        await ctx.send("Please provide what class you would like to pick for your profile! The classes are Warrior, Mage, Archer, and Rogue")
        return True
    elif profile_class not in classes_list:
        thing = profile_class + ' is not a valid class! The classes are Warrior, Mage, Archer, and Rogue'
        await ctx.send(thing)
        return True
    try:
        user = ctx.message.author.id
        fruit = str(random.choice(fruit_list))
        profile = {"class": profile_class, "fruit": fruit}
        db.hmset(str(user), profile)
        await ctx.send("Created profile " + fruit " successfully as class" + str(profile_class))
    except:
        await ctx.send("There was an error creating your profile!")

@client.command()
async def fight(ctx):
    with open("regen_stats.json") as f:
        stats = json.load(f)
    with open("player_weapons.json") as f:
        weapons = json.load(f)

    await ctx.send(embed=fight_embed(ctx.message.author))
    channel = ctx.message.channel

    nest2 = stats[str(author)]

    while enemy.health > 0: # and nest2["Health"] > 0:
        def check(m):
            return (m.content.lower() == 'attack' or m.content.lower() == 'skill' or m.content.lower() == 'use skill') and m.channel == channel
        try:
            await client.wait_for('message', timeout=10.0, check=check)
            author = str(ctx.message.author)[:-5]
            nest = weapons[str(author)]
            strike = nest["Attack"]-(nest["Attack"]*(enemy.defense/100))
            enemy.health -= round(strike)
            await ctx.send('You struck the enemy for {0}!'.format(strike))
        except asyncio.TimeoutError:
            await channel.send("You were too late and you missed your chance to strike")

        author = str(ctx.message.author)[:-5]
        nest = weapons[str(author)]
        nest2 = stats[str(author)]
        strike2 = enemy.attack - (enemy.attack * (nest["Defense"] / 100))
        nest2["Health"] -= round(strike2)
        await ctx.send('The enemy struck you for {0}!'.format(strike2))
        with open("regen_stats.json", "w") as f:
            json.dump(stats, f, indent=4)

        await ctx.send(embed=fight_embed(ctx.message.author))

@client.command()
async def craft(ctx, object=None):
    all_items = []
    with open("armor.json") as f:
        armor = json.load(f)
    with open("weapons.json") as f:
        weapons = json.load(f)
    with open("player_items.json") as f:
        items = json.load(f)

    embed = discord.Embed(
        title="Crafting",
        description="Crafting in RPG Bot 1.0",
        color=discord.Color.blue()
    )
    for defense in armor:
        nest = armor[str(defense)]
        if nest["Craft"]["Craftable"] == "Yes":
            # skill = nest["Class"]
            defend = nest["Defense"]
            # health = nest["Hitpoints"]
            # value = f"Class: {skill} \n Defense: {defend} \n Hitpoints Bonus: {health} \n "
            embed.add_field(name=str(defense), value=f"Defense: {defend}", inline=False)
            all_items.append(defense)

    for weapon in weapons:
        nest = weapons[str(weapon)]
        if nest["Craft"]["Craftable"] == "Yes":
            attack = nest["Damage"]
            embed.add_field(name=str(weapon), value=f"Attack: {attack}", inline=False)
            all_items.append(weapon)

    embed.add_field(name="Choices", value="Choose an item to get a more in depth description, or exit!")

    await ctx.send(embed=embed)

    channel = ctx.message.channel

    def check(m):
        content = ' '.join(word[0].upper() + word[1:] for word in m.content.lower().split())
        return (content in all_items) and m.channel == channel

    try:
        msg = await client.wait_for('message', timeout=10.0, check=check)
        content = ' '.join(word[0].upper() + word[1:] for word in msg.content.lower().split())
        if content in armor:
            nest = armor[str(content)]
            description = nest["Description"]
            defend = nest["Defense"]
            health = nest["Hitpoints"]
            craftnest = nest["Craft"]
            ingredients = {}
            for ingredient in craftnest:
                if ingredient == "Craftable":
                    pass
                else:
                    ingredients[str(ingredient)] = craftnest[ingredient]

            embed = discord.Embed(title=str(content),
                    description=description,
                    color=discord.Color.blue()
            )
            embed.add_field(name="Defense", value=f"{defend} points", inline=False)
            embed.add_field(name="Hitpoints", value=f"{health} points", inline=False)
            embed.add_field(name="**Crafting**", value="-", inline=False)
            for ingredient in ingredients:
                embed.add_field(name=str(ingredient), value=craftnest[ingredient], inline=False)
            embed.set_footer(text="Do you want to craft this item?")
            await ctx.send(embed=embed)
        else:
            nest = weapons[str(content)]
            description = nest["Description"]
            damage = nest["Damage"]
            range = nest["Range"]
            craftnest = nest["Craft"]
            ingredients = {}
            for ingredient in craftnest:
                if ingredient == "Craftable":
                    pass
                else:
                    ingredients[str(ingredient)] = craftnest[ingredient]

            embed = discord.Embed(title=str(content),
                                  description=description,
                                  color=discord.Color.blue()
                                  )
            embed.add_field(name="Damage", value=f"{damage} points", inline=False)
            embed.add_field(name="Range", value=f"{range} range", inline=False)
            embed.add_field(name="**Crafting**", value="-", inline=False)
            for ingredient in ingredients:
                embed.add_field(name=str(ingredient), value=craftnest[ingredient], inline=False)
            embed.set_footer(text="Do you want to craft this item?")
            await ctx.send(embed=embed)

        channel = ctx.message.channel

        def check(m):
            return (m.content.lower() == "yes") and m.channel == channel

        try:
            await client.wait_for("message", timeout=20.0, check=check)
            author = str(ctx.message.author)[:-5]
            nest = items[author]
            has_necessary_ingredients = True
            for item in ingredients:
                if nest[item] >= ingredients[item]:
                    pass

                else:
                    await channel.send("You do not have the necessary ingredients to craft this item.")
                    has_necessary_ingredients = False
                    break
            if has_necessary_ingredients:
                await ctx.send(f"You crafted the {content}! It has been added to your inventory and the appropriate amount of ingredients have been removed from your inventory.")
                for item in ingredients:
                    nest = items[author]
                    nest[item] -= ingredients[item]

                with open("player_items.json", "w") as f:
                    json.dump(items, f, indent=4)


        except asyncio.TimeoutError:
            await channel.send("The storekeep was uncomfortable with you holding the item for so long, so she kicked you out of her store.")


    except asyncio.TimeoutError:
        await channel.send("You did not respond in time, so the storekeep asked you to leave the store. You complied with her demands.")


client.run(TOKEN)
