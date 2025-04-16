import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
import json
from config import*
from functions.game_functions import*
from datetime import datetime, UTC
import asyncio, random

class Activity(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.command()
    async def start(self, ctx):
        '''creates profiles for new users'''
        if str(ctx.author.id) in data:
            await ctx.reply("Your profile is already created. You can play now")
            return
        em = Embed(title="New Profile", description="You new profile is being created.\nPlease select a difficulty level to begin", colour=Color.green())
        em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        
        select = Select(placeholder="select a difficulty level",max_values=1,options=[SelectOption(label="Easy", value="easy"),SelectOption(label="Normal",value= "normal"),SelectOption(label="Peaceful", value="peaceful"),SelectOption(label="Hard", value="hard"),SelectOption(label="Hardcore", value="hardcore")])

        view = View(timeout=30)
        view.add_item(select)
        await ctx.reply(embed=em,view=view)
        
        async def select_callback(interaction: discord.Interaction):
            create_profile(ctx.author.name, ctx.author.id, interaction.data["values"][0])
            em.color = Color.greyple()
            em.description = "New Profile created successfully"
            em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
            await interaction.response.edit_message(embed=em,view=None)
            await ctx.send(f"<@{ctx.author.id}> you can start playing now")
        
        select.callback = select_callback
            
    @commands.command()        
    async def delete(self,ctx):
        em= Embed(title="Profile Deletion",description="We are so sorry to see you go 😥.\nAre you sure want delete your profile ?\nThis process is highly irreversible.",color=Color.red())
        em.set_thumbnail(url=ctx.author.avatar)
        em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        
        msg = await ctx.reply(embed=em)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        async def check(reaction, user):
            if str(reaction.emoji) == '❌':
               await ctx.reply("Good job you stepped back from account deletion")
            return user == ctx.author and str(reaction.emoji) == '✅'
        try:
            react, user = await self.client.wait_for( "reaction_add",check = check, timeout=30)
        except asyncio.TimeoutError:
            return
        data.pop(str(ctx.author.id))
        await ctx.send(f"<@{ctx.author.id}> your profile have been successfully deleted. You can play again by creating a new profile.")
        
    
    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        '''Views users inventory'''
        inv = data[str(ctx.author.id)]["inv"]
        tools = data[str(ctx.author.id)]["tools"]
        if inv == []:
            await ctx.reply("You don't have anything in your inventory haha 😆")
            return
        inv_size = data[str(ctx.author.id)]["inv_size"]
        tools_size = len(tools)
        import math
        em = Embed(title=f"{ctx.author.name} Inventory",color=discord.Colour.green())
        fill = tools_size
        for item_size in inv.values():
            if item_size > 64:
                fill += math.ceil(item_size/64)
            else:
                fill += 1
        em.set_footer(text=f"Showing {ctx.author.name}'s inventory: {fill} out of {inv_size}", icon_url=ctx.author.avatar)
        target = 1
        for item in inv:
            emoji = info["id"][item]
            name = item.replace("_", " ").capitalize()
            type = "unknown"
            for keys in info:
                if item in info[keys]:
                    type = keys
                    break
            if inv[item] > 64:
                for i in range(math.ceil(inv[item]/64)):
                    em.add_field(name = f"{target}) {emoji} {name} x {64 if i != math.ceil(inv[item])-1 else inv[item]%64}", value= f"    ID -  *{item}* - {type} - [Click here for item info]https://minecraft.fandom.com/wiki/{item})", inline=False)
                    target +=1
            else:      
                em.add_field(name = f"{target}) {emoji} {name} x {inv[item]}", value= f"    ID - *{item}* - {type} - [Click here for item info]https://minecraft.fandom.com/wiki/{item})", inline=False)
                target += 1
        for tool in tools:
            emoji = info["id"][tool]
            name = tool.replace("_", " ").capitalize()
            type = tool.split("_")[1]
            em.add_field(name = f"{target}) {emoji} {name}", value= f"    ID -  *{tool}* - {type} - [Click here for item info]https://minecraft.fandom.com/wiki/{item})", inline=False)
            target += 1

        await ctx.reply(embed=em)
        
    @commands.command()
    @commands.cooldown(1,200,type= commands.BucketType.user )
    async def mine(self,ctx):
        tools = data[str(ctx.author.id)]["tools"]
        pickaxe = []
        for tool in tools:
            if "pickaxe" in tool:
                pickaxe.append(tool)
        if pickaxe == []:
            await ctx.reply("You need a pickaxe to mine stupid haha 😝😝")
            return
        pages = len(pickaxe)
        index = 0
        em = Embed(title="Mining",color=Color.green())
        em.set_image(url = f"https://cdn.discordapp.com/emojis/{info["id"][pickaxe[index]].split(":")[2][:-1]}.png")
        em.set_footer(text=f"Showing pickaxe {index+1}//{pages}", icon_url=ctx.author.avatar)
        
        button_prev = Button(style=ButtonStyle.blurple,label="«",disabled=True, custom_id="button_prev")
        button_next=Button(style=ButtonStyle.blurple,label="»",disabled=pages<=1,custom_id="button_next")
        mine_button = Button(style=ButtonStyle.red, label=f"Use {pickaxe[index].replace("_"," ").capitalize()}",custom_id="mine_button")
      
        view = View(timeout=30)
        view.add_item(button_prev)
        view.add_item(mine_button)
        view.add_item(button_next)
        
        msg = await ctx.reply(embed=em, view=view)  
      
        async def button_callback(interaction: discord.Interaction):
            nonlocal em, pickaxe, index, view
            if interaction.user != ctx.author:
                return
            label = interaction.data["custom_id"]
            if label == "mine_button":
                em.color = Color.greyple()
                for children in view.children:
                    children.disabled = True
                await interaction.response.edit_message(embed=em,view=view)
                em = Embed(title=f"{ctx.author.name} went on Mining", description=f"You went on for mining using {pickaxe[index].replace("_"," ").capitalize()}.\n Use the ``m!return`` command to return home\n{info["id"]["progress_filled"]}{info["id"]["progress_empty"]*9}",color=Color.green())
                em.set_footer(text=f"Updated at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
                msg_send = await ctx.reply(embed=em)
                try:
                    msg_dm = await ctx.author.send(embed=em)
                except Exception as e:
                   msg_dm = None
                   print(e)
                message[msg_send] = [msg_send, msg_dm, em, 1, ctx, pickaxe[index]]
                log_cmd(ctx,"mine")
                return
            elif label == "button_prev":
                index -= 1
            else:
                index +=1
            button_prev.disabled = index == 0
            button_next.disabled = index == pages-1
            mine_button.label = f"Use {pickaxe[index].replace("_"," ").capitalize()}"
            em.set_image(url = f"https://cdn.discordapp.com/emojis/{info["id"][pickaxe[index]].split(":")[2][:-1]}.png")
            em.set_footer(text=f"Showing pickaxe {index+1}//{pages}", icon_url=ctx.author.avatar)
            await interaction.response.edit_message(embed = em, view = view)

        async def on_timeout():
          for children in view.children:
              children.disabled = True
          await msg.edit(view=view)
        
        button_prev.callback = button_callback
        button_next.callback = button_callback
        mine_button.callback = button_callback
        view.on_timeout = on_timeout
        
    @commands.command()
    async def eat(self, ctx):
        if data[str(ctx.author.id)]["food"] == 100:
            await ctx.reply("You are already full!! You dont need to eat anymore 🤢")
            return
        inv = data[str(ctx.author.id)]["inv"]
        not_eatables = ["wheat", "sugar_cane","spider_eye", "pumpkin_pie"]
        foods = [i for i in inv if i in info["food"] and (i not in not_eatables)]
        if foods == []:
            await ctx.reply("You have nothing to eat poor haha 😆😜")
            return
        pages = len(foods)
        index = 0
        em = Embed(title="Eating",description=f"***{info["id"][foods[index]]}{foods[index].replace("_"," ").capitalize()} X {inv[foods[index]]}***\n\n"+hearts(ctx)+"\n"+food(ctx),color=Color.green())
        em.set_image(url = f"https://cdn.discordapp.com/emojis/{info["id"][foods[index]].split(":")[2][:-1]}.png")
        em.set_footer(text=f"Showing food {index+1}//{pages}", icon_url=ctx.author.avatar)
        
        button_prev = Button(style=ButtonStyle.blurple,label="«",disabled=True, custom_id="button_prev")
        button_next=Button(style=ButtonStyle.blurple,label="»",disabled=pages<=1,custom_id="button_next")
        eat_button = Button(style=ButtonStyle.red, label=f"Eat {foods[index].replace("_"," ").capitalize()}",custom_id="eat_button")
      
        view = View(timeout=30)
        view.add_item(button_prev)
        view.add_item(eat_button)
        view.add_item(button_next)
        
        msg = await ctx.reply(embed=em, view=view)  
        
        async def button_callback(interaction: discord.Interaction):
            nonlocal not_eatables, foods, index, em, view, pages, inv
            if interaction.user != ctx.author:
                return
            label = interaction.data["custom_id"]
            print("going")
            if label == "eat_button":
                health_increase = random.randint(1,10)
                food_level(ctx,health_increase)
                await add_item(ctx, ctx.author.id, foods[index], -1)
                inv = data[str(ctx.author.id)]["inv"]
                if data[str(ctx.author.id)]["food"] == 100:
                    await interaction.response.edit_message(content="You are full now. You cant eat any more 🤢",embed=None, view=None)
                    return
                if foods[index] not in inv:
                    index -= 1
                    if index < 0:
                        index = 0
                foods = [i for i in inv if i in info["food"] and (i not in not_eatables)]
                pages = len(foods)
                if foods == []:
                    await interaction.response.edit_message(content="You have no more item in inventory to eat", embed = None, view = None)
                    return
                em.description=f"***{info["id"][foods[index]]}{foods[index].replace("_"," ").capitalize()} X {inv[foods[index]]}***\n"+hearts(ctx)+"\n"+food(ctx)
                em.set_image(url = f"https://cdn.discordapp.com/emojis/{info["id"][foods[index]].split(":")[2][:-1]}.png")
                em.set_footer(text=f"Showing food {index+1}//{pages}", icon_url=ctx.author.avatar)
                button_prev.disabled = index == 0
                button_next.disabled = index == pages-1
                await interaction.response.edit_message(embed=em,view=view)
                return
            elif label == "button_prev":
                index -= 1
            else:
                index +=1
            button_prev.disabled = index == 0
            button_next.disabled = index == pages-1
            em.set_image(url = f"https://cdn.discordapp.com/emojis/{info["id"][foods[index]].split(":")[2][:-1]}.png")
            em.description=f"***{info["id"][foods[index]]}{foods[index].replace("_"," ").capitalize()} X {inv[foods[index]]}***\n"+hearts(ctx)+"\n"+food(ctx)
            em.set_footer(text=f"Showing food {index+1}//{pages}", icon_url=ctx.author.avatar)
            await interaction.response.edit_message(embed = em, view = view)

        async def on_timeout():
            await msg.edit(view=None)
        button_prev.callback = button_callback
        button_next.callback = button_callback
        eat_button.callback = button_callback
        view.on_timeout = on_timeout
        
    @commands.command()
    async def kill(self, ctx, mob):
        if isinstance(mob, discord.Member):
            user = mob
            if not str(user.id) in data:
               await ctx.reply("That user isnt playing minecord!!")
               return
            if not any(guild in user.mutual_guilds for guild in ctx.author.mutual_guilds):
               await ctx.reply("That user isnt from your server!!")
               return

        elif mob.lower() in info["mob"]:
            mob = mob.lower()
            if str(ctx.guild.id) not in server:
                await ctx.reply("Oho there are no available mobs in your server.\nKeep playing and one will spawn automatically")
                return
            if mob not in server[str(ctx.guild.id)]:
                await ctx.reply("Oho that mob has not spawned in your server. Look for other mobs.\nKeep playing and one will spawn automatically")
                return
            swords = []
            for tool in data[str(ctx.guild.id)]["tools"]:
                if "sword" in tool:
                   swords.append(tool)
            em = Embed(title=f"Attacking {mob.replace("_"," ").capitalize()}",description="",color=Color.red())
            if swords == []:
               em.description += "You have no sword in your inventory!!"
            pages = len(swords)
            i = 0
            button_prev = Button(style=ButtonStyle.blurple, label="«", disabled=True, custom_id="button_prev")
            button_next = Button(style=ButtonStyle.blurple,label="»",disabled=pages <= 1,custom_id="button_next")
            attack = Button(style=ButtonStyle.green,label="Attack Bare Handed" if swords == [] else f"Attack using {swords[i].replace("_"," ").capitalize()}",custom_id="attack")
            view = View(timeout=30)
            view.add_item(button_prev)
            view.add_item(attack)
            view.add_item(button_next)

            async def on_interaction(interaction: discord.Interaction):
                label = interaction.data["custom_id"]
                if label == "attack":
                    if swords == []:
                        damage = random.randint(15,25)
                    elif swords[i] == "wooden_sword":
                        damage = random.randint(25, 35)
                    elif swords[i] == "stone_sword":
                        damage = random.randint(35, 45)
                    elif swords[i] == "iron_sword":
                        damage = random.randint(45, 55)
                    elif swords[i] == "gold_sword":
                        damage = random.randint(55, 65)
                    elif swords[i] == "diamond_sword":
                        damage = random.randint(65, 75)
                    elif swords[i] == "netherite_sword" :
                        damage = random.randint(80,100)
                    server[str(ctx.guild.id)][mob][0] -= damage
                    if server[str(ctx.guild.id)][mob] <= 0:
                        #Mob killed by user
                        server[str(ctx.guild.id)].pop(mob)
                        if server[str(ctx.guild.id)] == {}:
                            server.pop(str(ctx.guild.id))
                        button_prev.disabled = True
                        button_next.disabled = True
                        attack.disabled = True
                        items = {}
                        for i in info["mob"][mob]:
                           items[i] = random.randint(1,4)
                        await interaction.response.edit_message(embed = em, view=view)
                        await ctx.reply(f"<@{ctx.author.id}> you killed {mob.replace("_"," ").capitalize()}")
                        em = Embed(title=f"{ctx.author.name} killed {mob.replace("_"," ").capitalize()}",description="Items Recieved: ", color=Color.red())
                        em.set_thumbnail(url=ctx.author.avatar)
                        for item in items:
                           emoji = info["id"][item]
                           name = item.replace("_"," ").capitalize()
                           em.description += f"\n{emoji} {name} x {items[item]}"
                           await add_item(ctx, ctx.author.id, item, items[item])
                        if swords != []:    
                            await tool_manager(ctx, swords[i], damage//2 if random.randint(0,1) == 1 else damage//3)
                        await ctx.send(embed= em)
                        return
                    #Mob attacked by user
                    heart = hearts(ctx, mob=mob)
                    await ctx.send(embed=Embed(title=f"{mob.replace("_"," ").capitalize()} was attacked by {ctx.author.name}", color=Color.red()).set_image(url=f"attachment://{mob}.png").set_thumbnail(url=ctx.author.avatar).add_field(name=heart,value=""),files = images[mob])
                    if swords != []:    
                            await tool_manager(ctx, swords[i], damage//2 if random.randint(0,1) == 1 else damage//3)
                    
                elif label == "button_prev":
                   i -= 1
                else:
                   i += 1
                button_prev.disabled = i == 0
                button_next.disabled = i == pages - 1
                attack.label = f"Attack using {swords[i].replace("_"," ").capitalize()}"
                await interaction.response.edit_message(embed = em, view=view)

            async def on_timeout():
                for children in view.children:
                    children.disabled = True
                await msg.edit(embed = em, view = view)

            msg = await ctx.reply(embed = em, view = view)
            button_next.callback = on_interaction
            button_prev.callback = on_interaction
            attack.callback = on_interaction
            view.on_timeout = on_timeout
        else:
           await ctx.reply("You must either mention a valid user or a valid spawned mob of your server")      

    @commands.command(aliases=['adv'])
    @commands.cooldown(1,1800,type= commands.BucketType.user )
    async def adventure(self, ctx):
        chance = random.randint(1, 100) 
        log_cmd(ctx,"adv")
        adv = None 
        if chance <= 40:
          await ctx.reply("Haha you found nothing!")
          return
        elif chance <= 50:
          if not place_searcher(ctx, "ocean"):
            adv = "ocean" 
        elif chance <= 60:
          if not place_searcher(ctx, "village"):
            adv = "village" 
        elif chance <= 70:
          if not place_searcher(ctx, "pillager_tower"):
            adv = "pillager_tower" 
        elif chance <= 80:
          if not place_searcher(ctx, "cave"):
            adv = "cave" 
        elif chance <= 85:
          if not place_searcher(ctx, "underground_cave"):
            adv = "underground_cave"
        elif chance <= 90:
          if not place_searcher(ctx, "ravine"):
            adv = "ravine" 
        elif chance <= 92:
          if not place_searcher(ctx, "igloo"):
            adv = "igloo" 
        elif chance <= 94:
          if not place_searcher(ctx, "witch's_hut"):
            adv = "witch's_hut"  
        elif chance <= 96:
          if not place_searcher(ctx, "jungle_temple"):
            adv = "jungle_temple" 
        elif chance <= 98:
          if not place_searcher(ctx, "woodland_mansion"):
            adv = "woodland_mansion" 
        else:  
          if not place_searcher(ctx, "desert_temple"):
            adv = "desert_temple"
        if adv is None:
          await ctx.reply("Haha you found nothing!")
          return
        await xp_manager(ctx, random.randint(1,10))
        add_place(ctx, adv)      
        await ctx.reply(f"You went on an adventure and found a ***{adv.replace("_"," ").capitalize()}***")
                
    @commands.command(aliases=["travel"])
    @commands.cooldown(1,100,type= commands.BucketType.user )
    async def go(self, ctx, *, place=None):
        world = data[str(ctx.author.id)]["world"]
        places = [i for i in data[str(ctx.author.id)]["places"] if i in info[f"loc_type_{world}"]]
        if places == []:
            await ctx.reply("You havent discovered that place yet. First discover the place using the ``m!adv`` command and if you are lucky you'll dicover new places.")
            return
        if place is None:
            pages = len(places)
            index = 0
            images = info["images"]
            def create_embed(index):
                embed = discord.Embed(title="Going",description=f"***{places[index].replace("_"," ").capitalize()}***",color=discord.Color.green())
                embed.set_image(url=images[places[index]])
                embed.set_footer(
                    text=f"Showing {places[index]} {index+1}//{pages}",
                    icon_url=ctx.author.avatar,
                )
                return embed

            button_prev = Button(
                style=ButtonStyle.blurple, label="«", disabled=True, custom_id="button_prev"
            )
            button_next = Button(
                style=ButtonStyle.blurple,
                label="»",
                disabled=pages <= 1,
                custom_id="button_next"
            )
            go_button = Button(style=ButtonStyle.red, label=f"Go {places[index].replace("_"," ").capitalize()}",custom_id="go_button")

            view = discord.ui.View(timeout=30)
            view.add_item(button_prev)
            view.add_item(go_button)
            view.add_item(button_next)

            msg = await ctx.reply(
                embed=create_embed(index),
                view=view,
            )

            async def button_callback(interaction: discord.Interaction):
                nonlocal index, places, pages
                if interaction.user != ctx.author:
                    return
                label = interaction.data["custom_id"]
                if label == "go_button":
                    for item in view.children:
                        item.disabled = True
                    em = Embed(title=f"{ctx.author.name} is Travelling",description=f"You went on the journey to {places[index].replace("_"," ").capitalize()}",color=Color.green())
                    em.set_image(url=images[places[index]])
                    em.set_footer(text=f"Updated at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
                    for children in view.children:
                        children.disabled = True
                    await interaction.response.edit_message(embed=em,view=view)
                    await location_changer(ctx, location=places[index], world=world)
                    log_cmd(ctx, "travel")
                    return
                if label == "button_prev":
                    index -= 1
                elif label == "button_next":
                    index += 1

                # Update button states
                button_prev.disabled = index == 0
                button_next.disabled = index == pages - 1
                go_button.label = f"Go {places[index].replace("_"," ").capitalize()}"
                go_button.disabled = False
                if data[str(ctx.author.id)]["location"] == places[index]:
                    go_button.label = "You are already here"
                    go_button.disabled = True
                print("going to update", places[index])
                await interaction.response.edit_message(embed=create_embed(index),view=view)
                return
                #await msg.edit(embed=create_embed(index),view=view)

            # Bind callbacks
            button_prev.callback = button_callback
            button_next.callback = button_callback
            go_button.callback = button_callback

            async def on_timeout():
                for item in view.children:
                    item.disabled = True
                await msg.edit(view=view)

            view.on_timeout = on_timeout
            
        else:
            place = get_id(place)
            if place in places:
                await location_changer(ctx, location=place)
                #time mechanism
                embed = Embed(title="Going",colour=Color.green())
                embed.set_footer(text= f"Updated at {datetime.now(UTC)}", icon_url=ctx.author.avatar)
                msg = await ctx.reply(embed=embed)
           
    @commands.command()
    @commands.cooldown(1,100,type= commands.BucketType.user )
    async def craft(self, ctx):
        inv = data[str(ctx.author.id)]["inv"]
        images = {}
        if "crafting_table" in inv:
           for file in os.listdir("assets/craft_3x3"):
                images[file[:-4]] = discord.File(f"assets/craft_3x3/{file}", filename=file)
        else:
            for file in os.listdir("assets/craft_2x2"):
                images[file[:-4]] = discord.File(f"assets/craft_2x2/{file}", filename=file)
        items = list(images.keys())
        i = 0
        pages = len(images)
        craft_value = 1
        button_prev = Button(style=ButtonStyle.blurple,label="«",disabled=True, custom_id="button_prev")
        button_next=Button(style=ButtonStyle.blurple,label="»",disabled=pages<=1,custom_id="button_next")
        craft = Button(style=ButtonStyle.green, label="Craft",custom_id="craft")
        em = Embed(title="Crafting",description=f"Viewing recipe for {items[i].replace("_"," ").capitalize()}",color=Color.green())
        em.set_image(url= f"attachment://{items[i].png}")
        for item, value in info["craft"][items[i]].items():
            emoji = info["id"][item]
            name = item.replace("_"," ").capitalize()
            if item not in inv or inv[item] < value:
                em.add_field(name= f":x: {emoji} {name} x {value}",value="")
                craft.disabled = True
                craft.style = ButtonStyle.red
            else:
                em.add_field(name= f":white_check_mark: {emoji} {name} x {value}",value="")
        em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)

        async def on_callback(interaction: discord.Interaction):
            label = interaction.data["custom_id"]
            if label == "craft":
                for item, value in info["craft"][items[i]].items():
                    await add_item(ctx, ctx.author.id, item, -value)
                if items[i] in info["tools"]:
                    data[str(ctx.authot.id)]["tools"].update({items[i]: info["tools"][items[i]]})
                else:
                    if items[i] in info["armour"]:
                        craft_value = info["armour"][items[i]]
                    elif items[i] == "plank" or items[i] == "stick" or "stair" in items[i]:
                        craft_value = 4
                    await add_item(ctx, ctx.author.id, items[i], craft_value)
                for children in view.children:
                    children.disabled = True
                em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
                em.color = ButtonStyle.grey
                await interaction.response.edit_message(embed=em,view=view,file=images[items[i]])
                await ctx.send(f"<@{ctx.author.id}> you successfully created a {items[i].replace("_"," ").capitalize()}")
                return
            elif label == "button_prev":
                i -= 1
            else:
                i += 1
            button_prev.disabled = i == 0
            button_next.disabled = i == pages-1
            craft.disabled = False
            craft.style = ButtonStyle.green
            em.description = f"Viewing recipe for {items[i].replace("_"," ").capitalize()}"
            em.set_image(url= f"attachment://{items[i].png}")
            for item, value in info["craft"][items[i]].items():
                emoji = info["id"][item]
                name = item.replace("_"," ").capitalize()
                if item not in inv or inv[item] < value:
                    em.add_field(name= f":x: {emoji} {name} x {value}",value="")
                    craft.disabled = True
                    craft.style = ButtonStyle.red
                else:
                    em.add_field(name= f":white_check_mark: {emoji} {name} x {value}",value="")
            em.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
            await interaction.response.edit_message(embed=em, view=view, file= images[items[i]])

        async def on_timeout():
            for children in view.children:
                children.disabled = True
            msg.edit(embed=em,view=view)

        view = View(timeout=30)
        view.add_item(button_prev)
        view.add_item(craft)
        view.add_item(button_next)

        msg = await ctx.reply(embed= em, view = view, file = images[items[i]])

        button_prev.callback = on_callback
        button_next.callback = on_callback
        craft.callback = on_callback

        view.on_timeout = on_timeout
    
    @commands.command(aliases=["loc"] )     
    async def location(self, ctx):
        loc = data[str(ctx.author.id)]["world"]
        loc_sub = data[str(ctx.author.id)]["location"]
        em = Embed(title=f"{ctx.author.name}'s Location", description=f"World : {loc.capitalize()}\nLocation : {loc_sub.capitalize()}\nUse the ``m!go`` command to travel diffrent places", colour = discord.Colour.blue())
        await ctx.reply(embed=em)
    
    @commands.command()
    async def throw(self, ctx, item, value):
      with open("data.json","r")as f:
        profile = json.load(f)
        inv = profile[str(ctx.author.id)]["inv"]
      if not item in inv:
        await ctx.send("The item u r looking for isn't in your inventory.")
        return
      if value == "max" or value == "all":
        profile[str(ctx.author.id)]["inv"].pop(item)
      else:
        try:
          value = int(value)
          await add_item(ctx, ctx.author.id, item, value)
        except:
          await ctx.send("Amount can be ``max``, ``all`` or an integer only")
          return
      with open("data.json", "w") as f:
        json.dump(profile, f, indent=4)
      await ctx.send("Item thrown from inventory")

    @commands.command()
    async def use(self, ctx, item):
      item = await get_id(item)
      if item is None:
        await ctx.reply("The item you are looking for dosen't exsists")
        return
      with open("data.json", "r") as f:
        profile = json.load(f)[str(ctx.author.id)]
        inv = profile["inv"]
      if not item in inv:
        await ctx.reply("That item isn't in your inventory lmao")
        return
      with open("info.json", "r") as f:
        data = json.load(f)
      if item in data["armour"]:
        pass
      elif item in data["usables"]:
        pass
      else:
        await ctx.reply("You cant use that item")
        
    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello I am Minecord, Minecraft Discord Bot ,My prefix is ``m!``, start playing!")
        
    @commands.command()
    async def invite(self, ctx):
        invite_button = Button(style=ButtonStyle.link, label="Invite", url = discord.utils.oauth_url(self.client.user.id, permissions= discord.Permissions(1126864130526785)))
        vote_button = Button(style=ButtonStyle.link,label = "Vote",url = "https://top.gg/bot/896308161831657492")
        embed = Embed(title="Invite Minecord", description="Glad to hear that you are inviting us to your server.",colour=discord.Colour.light_grey())
        embed.set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        view = View(timeout=30)
        view.add_item(invite_button)
        view.add_item(vote_button)
        msg = await ctx.send(embed=embed,view = view)
        
        async def callback(interactions: discord.Interaction):
            embed.color = Color.greyple()
            msg.edit(embed = embed)
        invite_button.callback = callback
        vote_button.callback = callback
    
    @commands.command()
    async def health(self, ctx):
        health = data[str(ctx.author.id)]["health"]
        max_health = data[str(ctx.author.id)]["max_health"]
        heart = hearts(ctx)
        foods = food(ctx)
        food_bar = data[str(ctx.author.id)]["food"]
        await ctx.reply(embed = Embed(title=f"{ctx.author.name}'s health", description= f"{health} {heart} {max_health}\n{food_bar} {foods} 100", colour= discord.Colour.red()).set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar))
    
    @commands.command()
    async def profile(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
            url = user.avatar 
        try:
            url = user.avatar 
            user = data[str(user.id)]
        except KeyError:
            await ctx.reply("No user found")
            return
        name = user["name"]
        level = user["level"]
        xp = user["xp"]
        max_xp = (level+1)*100
        health = user["health"]
        max_health = user["max_health"]
        descrip = f"**Name** : {name}\n**Xp** :{xp}/{max_xp}\n**Health** : {health}/{max_health}\n**Armour** : "
        dict = {}
        list = []
        if user["armour"] == dict:
          descrip += "No Armour"
        else:
          for key, value in user["armour"]:
            descrip +=  f"***  • {key} : {value}***\n"
        
        em = Embed(title= f"{name}'s Profile", description= descrip, colour = discord.Colour.blue())
        em.set_thumbnail(url = str(url))        
        em.set_footer(text= f"Profile Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}" , icon_url= ctx.author.avatar)
        
        button1 = Button(style=ButtonStyle.blurple,label="Builds »",custom_id="Builds »")
        button2 = Button(style=ButtonStyle.blurple,label="« Profile",custom_id="« Profile")
        button3 = Button(style=ButtonStyle.blurple,label="Adventure »",custom_id="Adventure »")
        button4 = Button(style=ButtonStyle.blurple,label="« Builds",custom_id="« Builds")
        button5 = Button(style=ButtonStyle.blurple,label="Advancements »",custom_id="Advancements »")
        button6 = Button(style=ButtonStyle.blurple,label="« Adventure",custom_id="« Adventure")
        button7 = Button(style=ButtonStyle.blurple,label="Log »",custom_id="Log »")
        button8 = Button(style=ButtonStyle.blurple,label="« Advancements",custom_id="« Advancements")

        view = View(timeout=30)
        view.add_item(button1)
        msg = await ctx.reply(embed=em, view=view)
        
        async def on_interaction(interaction: discord.Interaction):
            #Processing Button Click
            button = interaction.data["custom_id"]
            if button == "« Profile":
                descrip = f"**Name** : {name}\n**Xp** :{xp}/{max_xp}\n**Health** : {health}/{max_health}\n**Armour** :"
                if user["armour"] == dict:
                    descrip += "No Armour"
                else:
                    for key, value in user["armour"]:
                      descrip +=  f"***  • {key} : {value}***\n"
                em.description = descrip
                view.clear_items()
                view.add_item(button1)
                await interaction.response.edit_message(embed = em, view=view)
              
            elif button == "Builds »" or button == "« Builds":
                descrip = "***• Builds***" 
                if user["builds"] == list:
                    descrip +="\nYou have build nothing"
                else:
                    for build in user["builds"]:
                        descrip += f"\n › {build}"
                em.description = descrip 
                view.clear_items()
                view.add_item(button2)
                view.add_item(button3)
                await interaction.response.edit_message(embed = em, view=view)
              
            elif  button == "Adventure »" or button == "« Adventure":
                descrip = "•Adventuress" 
                if user["places"] == list:
                    descrip +="\nYou have adventured nothing"
                else:
                    for place in user["places"]:
                        descrip += f"\n*** › {place}***"
                em.description = descrip
                view.clear_items()
                view.add_item(button4)
                view.add_item(button5)
                await interaction.response.edit_message(embed = em, view=view)
              
            elif button == "Advancements »" or button == "« Advancements":
                descrip = "•Advancements" 
                if user["adv"] == list:
                    descrip +="\nYou have got no advancements"              
                else:
                    for advancement in user["adv"]:
                        descrip += f"\n*** › {advancement}***"
                em.description = descrip 
                view.clear_items()
                view.add_item(button6)
                view.add_item(button7)
                await interaction.response.edit_message(embed = em, view = view)
              
            elif button == "Log »":
                descrip = "•Logs" 
                if user["log"] == dict:
                    descrip +="\nNo record"
                else:
                    for log, times in user["log"].items():
                        descrip += f"\n*** › {log} : {times}***"
                em.description = descrip 
                view.clear_items()
                view.add_item(button8)
                await interaction.response.edit_message(embed = em, view=view)
        
        async def on_timeout():
            for children in view.children:
                children.disabled = True
            await msg.edit(view=view)        
                
        button1.callback = on_interaction
        button2.callback = on_interaction
        button3.callback = on_interaction
        button4.callback = on_interaction
        button5.callback = on_interaction
        button6.callback = on_interaction
        button7.callback = on_interaction
        button8.callback = on_interaction
        view.on_timeout = on_timeout
   
    @commands.command(aliases= ["xp","lvl"])
    async def level(self, ctx):
        with open("data.json", 'r')as f:
          profile = json.load(f)[str(ctx.author.id)]
        level = profile["level"]
        xp = profile["xp"]
        await ctx.reply(embed = Embed(title= f"{ctx.author.name}'s level", description = f"Level : {level}\n Xp : {xp} / {(level+1)*100}",colour = discord.Colour.blurple()).set_footer(text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar))

    @commands.command()
    async def bug(self, ctx,*,bug):
        agent = self.client.get_user(894072003533877279)
        if agent == None:
          await ctx.reply("ERROR")
          return
        await agent.send(f"{ctx.author} says :- \n {bug}")

    @commands.command()
    async def vote(self, ctx):
        em = Embed(title = "Vote Minecord", description =  "Thanks for voting Minecord at top.gg\nVote daily and get a bonus chest.", color = Color.green()) 
        await ctx.send(embed= em, view=View().add_item(Button(style = ButtonStyle.link, label = "Vote", url = "https://top.gg/bot/896308161831657492")))

    @commands.command(aliases=["dev"])
    async def developer(self,ctx):
        em = Embed(title = "Mr.Harsh", description = "Hi, I make Bots like this, Vote and show support.\nID : Mr.Harsh#3188", colour = discord.Colour.dark_blue())
        em.set_thumbnail(url= (self.client.get_user(894072003533877279).avatar))
        invite = Button(label= "Invite",style=ButtonStyle.link, url = discord.utils.oauth_url(self.client.user.id))
        github = Button(label="Happyharsh-codes",style=ButtonStyle.link, url = git_hub )
        view = View(timeout=30)
        view.add_item(invite)
        view.add_item(github)
        await ctx.send(embed=em, view=view)
      
    @commands.command()
    async def enchant(self, ctx):
        await ctx.send("This command is yet to be made!\nSorry :(")

    @commands.command()
    async def trade(self, ctx):
        await ctx.send("This command is yet to be made!\nSorry :(")

    @commands.command()
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def hunt(self, ctx):
        chance = random.randint(1,100)
        quantity = random.randint(1, 3)
        log_cmd(ctx,"hunt")
        hunt = None
        mob = None
        if chance <= 20:
          #Raw porkchop
          hunt = "raw_porkchop"
          mob = "Pig" 
        elif chance <= 26:
          #raw beef
          if inv_searcher(ctx, "wooden_sword","stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "raw_beef"
            mob = "Cow"
        elif chance <= 32:
          #raw chicken
          if inv_searcher(ctx, "stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "raw_chicken"
            mob = "Chicken"
        elif chance <= 38:
          #raw mutton
          if inv_searcher(ctx, "stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "raw_mutton"
            mob = "Sheep"
        elif chance <= 44:
          #leather
          if inv_searcher(ctx, "stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "leather"
            mob = "Cow"
        elif chance <= 50:
          #feather
          if inv_searcher(ctx, "stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "feather"
            mob = "Chicken"
        elif chance <= 56:
          #wool
          if inv_searcher(ctx, "stone_sword,""iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "wool"
            mob = "Sheep"
        elif chance <= 62:
          # rotten flesh
          if inv_searcher(ctx, "iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "rotten_flesh"
            mob = "Zombie"
        elif chance <= 68:
          #gunpowder
          if inv_searcher(ctx, "iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "gunpowder"
            mob = "Creeper"
        elif chance <= 74:
          #bow
          if inv_searcher(ctx, "iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "bow"
            mob = "Skeleton"
        elif chance <= 80:
          #arrow
          if inv_searcher(ctx, "iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "arrow"
            mob = "Skeleton"
        elif chance <= 86:
          #spider_eye
          if inv_searcher(ctx, "iron_sword","golden_sword","diamond_sword","netherite_sword"):
            hunt = "spider_eye"
            mob = "Spider"
        elif chance <= 92:
          if inv_searcher(ctx, "diamond_sword", "netherite_sword"):
            #ender_pearl
            hunt = "ender_pearl"
            mob = "Enderman"
        elif chance <= 98:
          #iron_ingots & poppy
          if inv_searcher(ctx, "netherite_sword"):
            hunt = "iron_ingots"
            mob = "Iron Golem"           
        if hunt is None:
            await ctx.reply("Haha you got nothing")
            return
        tools = data[str(ctx.author.id)]["tools"]
        for tool in tools:
            if "sword" in tool:
                tool_manager(ctx, tool, -random.randint(1,2)*quantity)
                break
        await add_item(ctx,ctx.author.id, hunt, quantity)
        emoji = info["id"][hunt]
        hunt = hunt.replace("_"," ").capitalize()
        await ctx.reply(f"You killed a {mob} and got {quantity} {hunt} {emoji}")
            
    
    @commands.command()
    @commands.cooldown(1, 1800, type=commands.BucketType.user)
    async def fish(self, ctx):
        """Fishing command - complete"""
        if not inv_searcher(ctx, "fishing_rod"):
          await ctx.reply("You don't even own a ``fishing rod``")
          return
        chance = random.randint(1,100)
        quantity = random.randint(1, 3)
        log_cmd(ctx,"fish")
        fish = None 
        if chance <= 50:
          await ctx.reply("Haha you got nothing!")
          return
        elif chance <= 60:
          fish = "raw_code"  
        if chance <= 70:        
          fish = "raw_salmon" 
        elif chance <= 80:
          pass
        elif chance <= 90:
          pass
        else:
          pass
        if fish == None:
          return
        await add_item(ctx,ctx.author.id, fish, quantity)
        await ctx.reply(f"You caught {quantity} {fish}") 
      
    @commands.command()
    async def build(self, ctx, monument=None):
        try:
            index = 0
            indexx = 0
            items = list(info["build"].keys())
            button_prev = Button(style=ButtonStyle.blurple,label="«",disabled=True,   custom_id="button_prev")
            button_next=Button(style=ButtonStyle.blurple,label="»",custom_id="button_next")
            build = Button(style=ButtonStyle.green, label="Build", custom_id="build")
            button_prev2 = Button(style=ButtonStyle.blurple,label="«",disabled=True,   custom_id="button_prev")
            button_next2=Button(style=ButtonStyle.blurple,label="»",custom_id="button_next")
            build2 = Button(style=ButtonStyle.green, label="Build", custom_id="build")
            em = Embed(title="Build Command", description='''Items to build''', colour= discord.Colour.green())
            em.add_field(name= "Houses",value= "**Level 1 House - Dirt House**\n  id - _dirt_\n**Level 2 House - Wooden House**\n  id - _wooden_\n**Level 3 House - Stone Mansion**\n  id - _stone_\n**Level 4 House - Modern Apartment**\n  id - _modern_\n**Level 5 House - Castle-e-Minecraft**\n  id - _castle_")
            em.set_footer(icon_url= ctx.author.avatar,  text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")     
            view = View(timeout=30)    
            view.add_item(button_prev)
            view.add_item(build)
            view.add_item(button_next)
            msg = await ctx.reply(embed=em,view=view)

            def set_descrip():
                nonlocal build2, items, index, indexx, ctx
                descrip = f"***Building {items[indexx].replace("_", " ").capitalize()}***\n"
                build_info = info["build"][items[indexx]]
                if "farm" in items[indexx]:
                    if build_searcher(ctx, build_info[0]):
                        descrip += f":white_check_mark: {info["build"][items[indexx]][0]}\n"
                    else:
                        descrip += f":x: {build_info[0]}\n"
                        build2.disabled = True
                        build2.style = ButtonStyle.red
                    if inv_searcher(ctx, build_info[1]):
                        descrip += f":white_check_mark: {build_info[0]}"
                    else:
                        descrip += f":x: {build_info[0]}"
                        build2.disabled = True
                        build2.style = ButtonStyle.red
                else:
                    for item, val in build_info:
                        if item in data[str(ctx.author.id)]["inv"] and data[str(ctx.author.id)]["inv"][item] >= val:
                            descrip += f":white_check_mark: {item} X {val}\n"
                        else:
                            descrip += f":x: {item} X {val}\n"
                            build2.disabled = True
                            build2.style = ButtonStyle.red
                return descrip

            async def on_interaction(interaction: discord.Interaction):
                nonlocal index, items, indexx
                button = interaction.data["custom_id"]
                em.clear_fields()
                if button == "build":
                    if index == 0:
                        items = items[0:5]
                    elif index == 1:
                        items = items[5:10]
                    else:
                        items = items[10:]
                    em.description = set_descrip()
                    em.set_footer(icon_url= ctx.author.avatar,  text=f"Showing {indexx+1}//{len(items)}")
                    view.clear_items()
                    view.add_item(button_prev2)
                    view.add_item(build2)
                    view.add_item(button_next2)
                    await interaction.response.edit_message(embed=em, view = view)
                    return
                elif button == "button_prev":
                    index -= 1
                    if index == 0:
                        em.add_field(name= "Houses",value= "**Level 1 House - Dirt House**\n  id - _dirt_\n**Level 2 House - Wooden House**\n  id - _wooden_\n**Level 3 House - Stone Mansion**\n  id - _stone_\n**Level 4 House - Modern Apartment**\n  id - _modern_\n**Level 5 House - Castle-e-Minecraft**\n  id - _castle_")
                    else:
                        em.add_field(name= "Farm", value = "**Farm Level 1 - Miniature Farm**\n  id - _mini_\n**Farm Level 2 - Smol Farm**\n  id - _smol_\n**Farm Level 3 - Normal Farm**\n  id - _normal_\n**Farm Level 4 - Big Farm**\n  id - _big_\n**Farm Level 5 - Giant Farm**\n  id - _giant_" )
                else:
                    index += 1
                    if index == 2:
                        em.add_field(name= "Other", value= "**Nether Portal**\n  id - _nether_\n**Xp Farm**\n  id -  _xp_\n**Shaft Mine**\n  id - _shaft_")
                    else:
                        em.add_field(name= "Farm", value = "**Farm Level 1 - Miniature Farm**\n  id - _mini_\n**Farm Level 2 - Smol Farm**\n  id - _smol_\n**Farm Level 3 - Normal Farm**\n  id - _normal_\n**Farm Level 4 - Big Farm**\n  id - _big_\n**Farm Level 5 - Giant Farm**\n  id - _giant_" )
                button_prev.disabled = index == 0
                button_next.disabled = index == 2
                await interaction.response.edit_message(embed=em, view=view)
                    
            async def on_interaction2(interaction: discord.Interaction):
                nonlocal items, indexx
                button = interaction.data["custom_id"]
                name = items[indexx].replace("_", " ").capitalize()
                if button == "build":
                    data[str(ctx.user.id)["builds"]] += [items[indexx]]
                    if "farm" in items[indexx]:
                        await tool_manager(ctx, info["build"][items[indexx]][1], -random.randint(10,20))
                    else:
                        for item, val in info["build"][items[indexx]].items():
                            await add_item(ctx, ctx.author.id, item, -val)
                    await ctx.send(f"<@{ctx.author.id} you successfully built {name}\nUse m!profile command to see it on your profile")
                    log_cmd(ctx,"build")
                    return
                elif button == "button_prev":
                    indexx -= 1
                else:
                    indexx +=1
                button_prev2.disabled = indexx == 0
                button_next2.disabled = indexx == len(items)-1
                build2.disabled = False
                build2.style = ButtonStyle.green
                em.description = set_descrip()
                em.footer.text = f"Showing {indexx+1}//{len(items)}"
                await interaction.response.edit_message(embed=em, view=view)
            
            async def on_timeout():    
                for children in view.children:
                    children.disabled = True
                await msg.edit(view=view)
            
            build.callback = on_interaction
            button_prev.callback = on_interaction
            button_next.callback = on_interaction
            build2.callback = on_interaction2
            button_prev2.callback = on_interaction2
            button_next2.callback = on_interaction2
            view.on_timeout = on_timeout
        except Exception as e:
            print(e)

    @commands.command()
    @commands.cooldown(1, 5000, type = commands.BucketType.user)
    async def cave(self, ctx):
        places = data[str(ctx.author.id)]["places"]
        cave = ""
        blocks = []
        for place in places:
            if place == 'cave':
                cave = "cave"
                choices = ["cobblestone", "iron_ore", "coal", "diorite", "andesite", "gravel", "sand", "dirt"]
                blocks = random.choices(choices) 
                break 
            elif place == 'underground_cave':
                cave = "underground_cave"
                choices = ["cobblestone", "iron_ore", "coal", "diorite", "andesite", "gravel", "diamond", "gold_ore", "emerald", "restone_dust", "lapiz_lazuli"]
                blocks = random.choices(choices) 
                break
            elif place == 'ravine':
                cave = "ravine"
                choices = ["cobblestone", "iron_ore", "coal", "diorite", "andesite", "gravel", "diamond", "gold_ore", "emerald", "restone_dust", "lapiz_lazuli"]
                blocks = random.choices(choices) 
                break
        if cave == "":
            await ctx.reply("You haven't discovered any cave.")
            return
        #Adding item in inventory
        descrip = "You brought back" 
        for block in blocks:
            quantity = random.randint(1,110) 
            await add_item(ctx, ctx.author.id, block, quantity)
            block_name = block.replace("_"," ").cpitalize()
            descrip += f"\n{info["id"][block]} {block_name} X {quantity}"
        await ctx.reply(embed= Embed(title=f"{ctx.author.name} went on a {cave}",description=descrip,color=Color.green()).set_footer(icon_url= ctx.author.avatar,  text=f"Requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}"))
        log_cmd(ctx, "cave")

    @commands.command()
    @commands.cooldown(1, 150, type = commands.BucketType.user)
    async def chop(self, ctx):
        log_cmd(ctx,'chop')
        if inv_searcher(ctx, "wooden_axe"):
            quantity = random.randint(1,5)
            tool_manager(ctx, "wooden_axe", -random.randint(1,2)*quantity)
        elif inv_searcher(ctx, "stone_axe"):
            quantity = random.randint(3,8)
            await tool_manager(ctx, "stone_axe", -random.randint(1,2)*quantity)
        elif inv_searcher(ctx, "iron_axe"):
            quantity = random.randint(6,12)
            await tool_manager(ctx, "iron_axe", -random.randint(1,2)*quantity)
        if inv_searcher(ctx, "gold_axe"):
            quantity = random.randint(6,14)
            await tool_manager(ctx, "gold_axe", -random.randint(1,2)*quantity)
        if inv_searcher(ctx, "diamond_axe"):
            quantity = random.randint(8,16)
            await tool_manager(ctx, "diamond_axe", -random.randint(1,2)*quantity)
        if inv_searcher(ctx, "netherite_axe"):
            quantity = random.randint(10,20)
            await tool_manager(ctx, "netherite_axe", -random.randint(1,2)*quantity)
        else:
            quantity = random.randint(1,3)
        await add_item(ctx, ctx.author.id, "log", quantity)
        with open("info.json", "r")as f:
            data = json.load(f)
            emoji =  data["id"]["log"]
        await ctx.reply(f"You brought {quantity} logs {emoji}" )

    @commands.command()
    @commands.cooldown(1, 2000, type = commands.BucketType.user)
    async def crop(self, ctx):
        em = Embed(title= f"{ctx.author.name} Crop Production", description = "Your farm yielded this/n", colour= Color.green())
        em.set_footer(text=f"{ctx.author} croped their farm" , icon_url= ctx.author.avatar)
        tools = data[str(ctx.author.id)]["tools"]
        hoe = []
        for tool in tools:
            if "hoe" in tool:
                hoe.append(tool)
        if hoe == []:
            await ctx.reply("You need a hoe to harvest your crops stupid haha 😝😝")
            return
        crops = []
        crop_quantity = [] 
        if not build_searcher(ctx, "miniature_farm"):
            crops = ["wheat", "carrot"]
            crop_quantity = [ random.randint(1,5), random.randint(1,5)] 
        elif build_searcher(ctx, "smol_farm") :
            crops = ["wheat", "carrot"]
            crop_quantity = [ random.randint(1,10), random.randint(1,10)] 
        elif build_searcher(ctx, "normal_farm"):
            crops = ["wheat","carrot", "potato","beet", "pumpkin_pie"]
            crop_quantity = [ random.randint(1,10), random.randint(1,10) ,random.randint(1, 5), random.randint(1, 5), random.randint(1,2)]
        elif build_searcher(ctx, "big_farm"):
            crops = ["wheat","carrot", "potato", "beet", "sugarcane", "pumpkin_pie", "melon_slice"]
            crop_quantity = [ random.randint(1,15), random.randint(1,15), random.randint(1,15), random.randint(1,10), random.randint(1, 10), random.randint(1,3), random.randint(1,3)] 
        elif build_searcher(ctx, "giant_farm"):
            crops = ["wheat","carrot", "potato", "beet", "sugarcane", "pumpkin_pie", "melon_slice"]
            crop_quantity = [ random.randint(1,20), random.randint(1, 20), random.randint(1, 20), random.randint(1,15), random.randint(1, 20), random.randint(1, 8), random.randint(1, 8)] 
        else:
            await ctx.reply("You haven't build an farm")
            return
        for crop in crops:
            emoji = data["id"][crop]
            crop_name = crop.replace("_", " ").capitalize()
            crop_quantity = crop_quantity[crops.index(crop)] 
            em.description += f"{emoji} {crop_name} X {crop_quantity}\n"
            await add_item(ctx, ctx.author.id, crop, crop_quantity)
            await tool_manager(ctx, hoe[random.randint(0,len(hoe)-1)], -random.randint(10,20))
        log_cmd(ctx,"crop")
        await ctx.send(embed=em)
    
async def setup(bot):
    await bot.add_cog(Activity(bot))
    print("setup run")
