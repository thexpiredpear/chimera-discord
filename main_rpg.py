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
from time import strftime
from time import gmtime

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix="ch ", intents=intents)
status = cycle(["TwinkiePlayz Kinda Gay", "Suffocation, a game we all can play!", "Global Thermonuclear War"])

devs = ["677343881351659570", "712057428765704192",  "721918108901703702"]

TOKEN = os.getenv("bot-token")
url = urlparse(os.getenv('REDISCLOUD_URL'))
rpgdb = redis.Redis(host=url.hostname, port=url.port, password=url.password)
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
    print("Bot ready")

@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))
           
            
@client.command()
async def profile(ctx, statement=None, profile_class=None):
    if statement == None:
        await ctx.send("Choose whether to create a new profile or delete your current one! [ch profile create <class>] [ch profile delete]")
    elif statement.lower() == "create":
        if profile_class == None:
            await ctx.send("Please provide what class you would like to pick for your profile! The classes are Warrior, Mage, Archer, and Rogue")
            return True
        elif profile_class.capitalize() not in classes_list:
            thing = profile_class.capitalize() + ' is not a valid class! The classes are Warrior, Mage, Archer, and Rogue'
            await ctx.send(thing)
            return True
        elif rpgdb.exists(str(ctx.message.author.id)):
            await ctx.send("You already have an existing profile " + rpgdb.hget(str(ctx.message.author.id), "fruit").decode("utf-8") + " with class " + rpgdb.hget(str(ctx.message.author.id), "class").decode("utf-8").capitalize())
            return True
        try:
            userid = str(ctx.message.author.id)
            fruit = str(random.choice(fruit_list))
            profile = {"class": profile_class.capitalize(), "fruit": fruit, "health": 25, "max_health": 25, "mana": 25, "max_mana": 25, "gold": 100}
            rpgdb.hmset(userid, profile)
            await ctx.send("Created profile " + fruit + " successfully as class " + profile_class.capitalize())
        except:
            await ctx.send("There was an error creating your profile, please try again")
    elif statement.lower() == "delete":
        if rpgdb.exists(str(ctx.message.author.id)):
            try:
                deleted_profile = rpgdb.hget(str(ctx.message.author.id), "fruit").decode("utf-8")
                rpgdb.delete(str(ctx.message.author.id))
                await ctx.send("Profile " + deleted_profile + " was successfully deleted!")
            except:
                await ctx.send("There was an error deleting your profile")
        else:
            await ctx.send("You have no profiles to delete!")

@client.command()
async def profiles(ctx):
    if rpgdb.exists(str(ctx.message.author.id)):
        await ctx.send("You currently have profile " + rpgdb.hget(str(ctx.message.author.id), "fruit").decode("utf-8") + " using class " + rpgdb.hget(str(ctx.message.author.id), "class").decode("utf-8"))
    else:
        await ctx.send("You currently have no profiles! Create one with [ch profile create <class>]")
                       
@client.command()
async def inventory(ctx: commands.Context):
    try:
        gold = rpgdb.hget(str(ctx.author.id), "gold").decode("utf-8")
        class_ = rpgdb.hget(str(ctx.author.id), "class").decode("utf-8")
        name = rpgdb.hget(str(ctx.author.id), "fruit").decode("utf-8")
    
        embed = discord.Embed(title="Inventory", description="Welcome to your inventory!",
                              color=discord.Color.blue())
        embed.set_author(name=name, icon_url=ctx.author.avatar_url)
    
        embed.add_field(name="Class", value=class_, inline=False)
        embed.add_field(name="Gold", value=gold, inline=False)
    
        await ctx.send(embed=embed)
    except BaseException:
        await ctx.send("Please create a new profile to update!")
                       
@client.command()
async def fight(ctx):
    with open("regen_stats.json") as f:
        stats = json.load(f)
    with open("player_weapons.json") as f:
        weapons = json.load(f)

    await ctx.send(embed=fight_embed(ctx.message.author))
    channel = ctx.message.channel

    author = str(ctx.message.author)[:-5]
    nest2 = stats[str(author)]

    while enemy.health > 0 and nest2["Health"] > 0:
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

        nest = weapons[str(author)]
        nest2 = stats[str(author)]
        strike2 = enemy.attack - (enemy.attack * (nest["Defense"] / 100))
        nest2["Health"] -= round(strike2)
        await ctx.send('The enemy struck you for {0}!'.format(strike2))
        with open("regen_stats.json", "w") as f:
            json.dump(stats, f, indent=4)

        await ctx.send(embed=fight_embed(ctx.message.author))



@client.command()
async def add_sets(ctx):
    with open("armor.json") as f:
        armor = json.load(f)

    with open("weapons.json") as f:
        weapons = json.load(f)

    for armor_set in armor:
        userid = "armor"
        profile = {"piece": armor_set}
        rpgdb.hmset(userid, profile)

    for weapon in weapons:
        userid = "weapons"
        profile = {"piece": weapon}
        rpgdb.hmset(userid, profile)


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

@client.command()
async def squishy(ctx):
    party_emoji = "<:squishy:800761490428264468>"
    await ctx.send(party_emoji)

@client.command(pass_context=True, aliases=["eval", "run"])
async def _eval(ctx, *, code="You need to input code."):
    if str(ctx.message.author.id) in devs:
        global_vars = globals().copy()
        global_vars["bot"] = client
        global_vars["ctx"] = ctx
        global_vars["message"] = ctx.message
        global_vars["author"] = ctx.message.author
        global_vars["channel"] = ctx.message.channel
        global_vars["server"] = ctx.message.guild

        try:
            result = eval(code, global_vars, locals())
            if asyncio.iscoroutine(result):
                result = await result
            result = str(result)
            embed = discord.Embed(title="Evaluated successfully.", color=0x80FF80)
            embed.add_field(
                name="**Input** :inbox_tray:",
                value="```py\n" + code + "```",
                inline=False,
            )
            embed.add_field(
                name="**Output** :outbox_tray:",
                value=f"```diff\n+ {result}```".replace(
                    f"{TOKEN}", "no ur not getting my token die"
                ).replace(f"{os.getenv('REDISCLOUD_URL')}", "no ur not getting my db url die"),
            )
            await ctx.send(embed=embed)
        except Exception as error:
            error_value = (
                "```diff\n- {}: {}```".format(type(error).__name__, str(error))
                .replace(f"{TOKEN}", "no ur not getting my token die")
                .replace(f"{os.getenv('REDISCLOUD_URL')}", "no ur not getting my db url die")
            )
            embed = discord.Embed(title="Evaluation failed.", color=0xF7665F)
            embed.add_field(
                name="Input :inbox_tray:", value="```py\n" + code + "```", inline=False
            )
            embed.add_field(
                name="Error :interrobang: ",
                value=error_value,
            )
            await ctx.send(embed=embed)
            return
    else:
        embed = discord.Embed(title="Evaluation failed.", color=0xF7665F)
        embed.add_field(
            name="Input :inbox_tray:", value="```py\n" + code + "```", inline=False
        )
        embed.add_field(
            name="Error :interrobang: ",
            value="```You are not a admin```",
        )
        await ctx.send(embed=embed)

@client.command(aliases=["feedback", "suggest"])
@commands.cooldown(1, 86400, commands.BucketType.user)
async def suggestion(ctx):
    embed = discord.Embed(title="Rules of Suggestions", description="The rules of suggestions! Please read before "
                                                                    "making a suggestion.", color=discord.Color.blue())

    embed.add_field(name="Make a suggestion that will be beneficial to the bot", value="Please make sure that your suggestion "
                                                                                      "will help the bot helpful to the bot, "
                                                                                      "do not suggest something that will hurt "
                                                                                      "the bot.", inline=False)
    embed.add_field(name="No using inappropriate language", value="In your suggestion make sure to not have inappropriate language, "
                                                                  "in fact we do have profanity filters and if you somehow bypass "
                                                                  "that, it may be a bannable offense. **Occasional swearing is permitted.**", inline=False)
    embed.add_field(name="You may suggest something be added to the Server", value="Although you may suggest something beneficial to the bot, "
                                                                                   "you may suggest something be added to the *server*, and "
                                                                                   "we will take your suggestion into account.", inline=False)
    embed.add_field(name="No trolling or spamming", value="Do not troll the bot's server by typing arbitrary suggestions, and do not create alts "
                                                          "and spam our suggestion feed. This is a *bannable* offense.")
    embed.add_field(name="Thank you for reading!", value="Type your suggestion down below. You have **10 minutes.**", inline=False)
    embed.set_footer(text="Thank you for reading suggestions!")

    await ctx.send(embed=embed)

    def check(m):
        return m.channel == ctx.message.channel and m.author == ctx.message.author

    try:
        feedback = await client.wait_for("message", timeout=600, check=check)
        author = ctx.message.author
        pfp = author.avatar_url

        channel = client.get_channel(774385992668151838)

        embed = discord.Embed(title="Suggestion", description=f"{feedback.content}", color=discord.Color.blue())
        embed.set_footer(text=f"Member ID: {ctx.message.author.id}")

        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        embed = discord.Embed(description="Your suggestion has been added!", color=discord.Color.blue())
        embed.set_author(name=f"{str(author)[:-5]}'s suggestion", icon_url=pfp)
        embed.add_field(name="See The Results", value="To see the results of your suggestion and to vote on others' suggestion, "
                                                      "join our [Support Server](https://discord.gg/F4W8YJ8BeC) and get **$500** daily!")

        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, you did not send feedback in time.")


@suggestion.error
async def suggestion_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        if int(error.retry_after) <= 3600:
            if int(error.retry_after) <= 60:
                retry = str(strftime("%S seconds", gmtime(error.retry_after)))
            else:
                retry = str(strftime("%M minutes and %S seconds", gmtime(error.retry_after)))
        else:
            retry = str(strftime("%H hours %M minutes and %S seconds", gmtime(error.retry_after)))

        embed = discord.Embed(description=f"You can only make one suggestion a day! Try again in `{retry}`",
                              color=discord.Color.blue())

        await ctx.send(embed=embed)
     
                
try:
    client.load_extension("jishaku")
except BaseException:
    print("jsk loading failed")
                
client.run(TOKEN)
