import math
from config import*
import json, discord, datetime, random

def has_profile(id):
    if str(id) in data:
        return True
    else:
        return False
    
def create_profile(name,id,difficulty="Easy"):
    data[str(id)] = {"name": name, "diff": difficulty, "inv":{},"tools":{}, "armour":{}, "location":"home","world":"over","inv_size": 25,"level":0,"xp":0, "health": 100,"food":100,"max_health":100, "builds": [],"places": [], "adv":[], "log":{}}


async def add_item(ctx,id,item,value):
    inv = data[str(id)]["inv"]
    inv_size = data[str(id)]["inv_size"]
    tools_sixe = len(data[str(id)]["tools"])
    if item in inv:
        inv[item] += value
    else:
        inv[item] = value
    if value > 0:
        filled = tools_sixe
        for item_size in inv.values():
            if item_size > 64:
                filled += math.ceil(item_size/64)
            else:
                filled += 1
        if filled > inv_size:
            how_much = filled - inv_size
            amt = 64*(how_much-1) + (inv[item]%64 if inv[item]%64 != 0 else 64)
            inv[item] -= amt
            await ctx.send(f"<@{id}> you inventory id full. You threw out {amt} {item} {info["id"][item]}")
    elif inv[item] == 0:
        inv.pop(item)
    data[str(id)]["inv"] = inv
        
def get_id(id):
    for aliases in info["alias"]:
        if id in info["alias"][aliases]:
            return aliases
        if aliases == id:
            return aliases       
        
def place_searcher(ctx, place):
    """Searches for place in user profile, if found returns true"""
    if place in data[str(ctx.author.id)]["places"]:
        return True
    else:
        return False
    
def adv_manager(ctx, adv):
    """Adds advancements in the user profile"""
    data[str(ctx.author.id)]["adv"].append(adv)
        
def adv_searcher(ctx, adv):
        """Searches for advancement in profile, if found returns true"""
        if adv in data[str(ctx.author.id)]["adv"]:
            return True
        else:
            return False
        
def log_cmd(ctx, cmd):   
    if cmd in data[str(ctx.author.id)]["log"]:
        data[str(ctx.author.id)]["log"][cmd] += 1
    else:
        data[str(ctx.author.id)]["log"].update({cmd: 1})

async def spawn(ctx):
    mob = random.choice(list(info["mob"].keys()))
    if str(ctx.guild.id) not in server:
        await ctx.send("A mob has spawned.\nUse command ```m!kill <mob_name>``` to kill the mob")
        server[str(ctx.guild.id)] = (mob, 500)

async def despawn(ctx):
    if str(ctx.guild.id) in server:
        mob = server[str(ctx.guild.id)][0]
        await ctx.channel.send(f"Oh oo {mob} despawned.")
        server.pop(str(ctx.guild.id))
        
async def xp_manager(ctx, xp_add):
    """Increases or decreases xp"""
    xp = data[str(ctx.author.id)]["xp"]
    level = data[str(ctx.author.id)]["level"]
    xp += xp_add
    if build_searcher(ctx, "xp_farm"):
        data[str(ctx.author.id)]["xp"] += xp
    if xp >= (level+1)*100:        
        xp -= (level+1) * 100
        level += 1
        await ctx.author.send(f"{ctx.author.mention} you reached level {level}")
        await ctx.send(f"{ctx.author.mention} you reached level {level}")
    data[str(ctx.author.id)]["xp"] = xp
    data[str(ctx.author.id)]["level"] = level
        

def builds_manager(ctx, build, replace=False):
    """Adds or removes builds from profile"""
    if replace is False:
        data[str(ctx.author.id)]["builds"].append(build)
    else:
        data[str(ctx.author.id)]["builds"].pop(build)

def build_searcher(ctx, build):
    """Searches for builds in profile, if found returns true"""
    if build in data[str(ctx.author.id)]["builds"]:
        return True
    else:
        return False
    
def add_place(ctx, place, replace= False):
    """Adds place in the places list of the user id"""
    if replace is False:
        data[str(ctx.author.id)]["places"].append(place)
    else:
        data[str(ctx.author.id)]["inv"].pop(place)
        
def food_level(ctx, value):
    food = data[str(ctx.author.id)]["food"]
    if food + value > 100:
        food = 100
    else:
        food += value
        if food < 0:
            food = 0
    data[str(ctx.author.id)]["food"] = food
        
def hearts(ctx):
    """Return String of hearts according to user's health."""
    health = data[str(ctx.author.id)]["health"]
    max_health = data[str(ctx.author.id)]["max_health"]
    heart = "<:minecraft_heart:898867063924330507>"
    half_heart = "<:half_heart:914832762773602324>"
    user_heart = ""
    if health == max_health:
        user_heart = heart*10
        return user_heart
    for i in range(1,health+1):
        if (i % 10) == 0:
            # Replacing Half heart by full heart.
            user_heart = user_heart.replace(half_heart, heart)
        elif (i % 5) == 0:
            user_heart += half_heart
    return user_heart

def food(ctx):
    """Return String of foods according to user's food level."""
    foods = data[str(ctx.author.id)]["food"]
    if foods == 0:
        return "0"
    food = "<:food:914830073067102218>"
    half_food = "<:half_food:914829417501589546>"
    user_food = ""
    if foods == 100:
        user_food = food*10
        return user_food
    for i in range(1,foods+1):
        if (i % 10) == 0:
            # Replacing Half heart by full heart.
            user_food = user_food.replace(half_food, food)
        elif (i % 5) == 0:
          user_food += half_food
    return user_food

def inv_searcher(ctx, *items):
    inv = data[str(ctx.author.id)]["inv"]
    tools = data[str(ctx.author.id)]["tools"]
    for item in items:
        if item in inv or item in tools:
            return True
    return False

async def tool_manager(ctx, tool, value):
    tools = data[str(ctx.author.id)]["tools"]
    for tooli in tools:
        if tooli == tool:
            tools[tool] += value
            if tools[tool] < 0:
                tools.pop(tool)
                await ctx.send(f"<@{ctx.author.id}> ayooo your {tool.replace("_", " ").capitalize()} broke down!!")
            data[str(ctx.author.id)]["tools"] = tools
            return
        
def user_location(ctx, world = False ):
      if not world:
        return data[str(ctx.author.id)]["location"]
      else:
        return data[str(ctx.author.id)]["world"]
        
async def location_changer(ctx, world=False, location=False):
    """Changes user's location"""
    loc = data[str(ctx.author.id)]["location"].replace("_"," ").capitalize()
    dest = location.replace("_"," ").capitalize()
    data[str(ctx.author.id)]["location"] = location
    filled = info["id"]["progress_filled"]
    empty = info["id"]["progress_empty"]
    bar = filled + (empty * 9)
    em = discord.Embed(title=f"{ctx.author.name} is Travelling", description=f"{loc} {bar} {dest}",color = discord.Color.green())
    em.set_footer(text=f"Updated at  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
    msg = await ctx.send(content=f"<@{ctx.author.id}>",embed=em)
    try:
        msg_dm = await ctx.author.send(embed=em)
    except discord.Forbidden:
        msg_dm = None
    message[msg] = [msg, msg_dm, em, 1, ctx]

async def change_health(ctx, value):
    """Changes user's health (only reduces it)"""
    armours= data[str(ctx.author.id)]["armour"]
    health = data[str(ctx.author.id)]["health"]
    max_health = data[str(ctx.author.id)]["max_health"]
    if armour == {}:
        health += value
    else:
        for i in range((-value)):
            if health > 100:
                for armour in armour:
                    armours[armour] -= random.randint(1,3)
                if random.randint(1,2) == 1:
                    health-=1
            else:
                health -= 1
        for armour in armours:
            if armours[armour] <= 0:
                armours.pop(armour)
                await ctx.send(f"<@{ctx.author.id} your {armour.replace("_"," ").capitalize()} broke down")
                try:
                    await ctx.author.send(f"<@{ctx.author.id}> your {armour.replace("_", " ").capitalize()} broke down")
                except:
                    pass
                max_health -= info["armour"][armour]
    if health <=  0:
        await kill(str(ctx.author.id))
        await ctx.send(f"Oho <@{ctx.author.id}> died.")
    elif health <= 30:
        await ctx.author.send("Oho you are on low health, try eating something.")
        
    data[str(ctx.author.id)]["armour"] = armour
    data[str(ctx.author.id)]["health"] = health
    data[str(ctx.author.id)]["max_health"] = max_health 

def equipt_armour(ctx, armour):
    """Equipts the armour and increases the max health"""
    armours = data[str(ctx.author.id)]["armour"]
    armour_dur = info["armour"][armour]
    health_increase = info["armour_health"][armour]
    armours.update({armour: armour_dur})
    data[str(ctx.author.id)]["max_health"] += health_increase
    data[str(ctx.author.id)]["armour"] = armours

async def kill(id, user, reason):
    del data[id]
    await user.send(embed=discord.Embed(title="YOU DIED!",description=reason + "\n You can start a new game using m!start command",color=discord.Color.red()).set_footer(text=f"{user.name} died at  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", icon_url=user.avatar))