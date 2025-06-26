import discord 
from discord.ext import commands
import asyncio, random
from datetime import datetime, UTC
from config import*
import discord.ext
from functions.game_functions import*

class Events:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user:
            return
        try:
            if isinstance(message.channel, discord.DMChannel):
                if message.author.id == 894072003533877279:
                    if (message.content[:17]).isdigit():
                        return
                    em = discord.Embed(title = "Do you want to send this message ?", description = message.content , colour = discord.Colour.red()) 
                    msg =  await message.channel.send(embed = em )           
                    await msg.add_reaction("✅")
                    await msg.add_reaction("❌")
                    def check(reaction, user):
                        return user == message.author and str(reaction.emoji) == '✅'
                    try:
                        react, user = await self.client.wait_for( "reaction_add",check = check, timeout=30)
                        await message.channel.send("Whom do you want to send ?")
                        try:
                            def check2(m): 
                                return m.author.id == message.author.id and m.channel.id == message.channel.id    
                            mess = await self.client.wait_for("message", check=check2,timeout = 30)
                        except asyncio.TimeoutError:
                            return
                        user =  self.client.get_user(int(mess.content))
                        await user.send(message.content)
                        em.set_footer(text="Sent" )
                        await msg.edit(embed=em)
                    except asyncio.TimeoutError:
                        return
                else:
                    await message.channel.send(message.content)        
                    return
            with open("server.json", "r") as f:
                data = json.load(f)
                allowed_channels = data.get(str(message.guild.id)).get("allowed_channels")
                if ( allowed_channels != []):
                    if message.channel.id not in allowed_channels:
                        print("Wrong channel")
                        return
                    
            if self.client.user.mention in message.content: 
                    if "activate" in message.content.lower():
                        if message.channel.permissions_for(message.author).manage_channels:
                            data[str(message.guild.id)]["allowed_channels"].append(message.channel.id)
                            with open("server.json", "w") as f:
                                json.dump(data, f)
                            await message.channel.send(embed=discord.Embed(title="Channel Activated",description=f"<#{message.channel.id}> was succesfully activated !! Start playing Minecord now.\n\n Use {self.client.user.mention} activate to use me in other channels", color= discord.Colour.green()))
                        else:
                            await message.channel.send("Ayoo user you need `manage channels` permission to user this command.")
                        return
                    em = discord.Embed(title= 'Minecord Bot', description= "Hi I am Minecord, The Discord Minecraft bot, my prefix is `m`", colour= discord.Colour.green())
                    em.set_thumbnail(url = self.client.user.avatar)
                    em.add_field(name= "Invite", value="To invite the bot use the `minvite` command")
                    em.add_field(name= "Bug Fix", value="Report bugs and suggestions using the `mbug` command")
                    em.add_field(name= "Activate Channele", value=f"Use {self.client.user.mention} activate to use minecord in a specific channel only")
                    await message.channel.send(embed=em)
                    return
            if not message.content.lower().startswith(("m", "m ")):
                return
            print(f"processing cmd {message.content}")
            if 'start' in message.content or 'help' in message.content:
                await self.client.process_commands(message)    
            if not has_profile(message.author.id):
                await message.channel.send(f"{message.author.mention} you haven't created your profile yet.\nCreate your profile with the `m start` command and start playing!")
                return
            await self.client.process_commands(message)
        except Exception as e:
            print(e)
      
    async def on_guild_remove(self, guild: discord.Guild):
        """Handling when Bot leaves a server"""
        print("left a server")
        user = self.client.get_user(894072003533877279)
        with open("server.json", "r") as f:
            data = json.load(f)
        invite = data[str(guild.id)]["invite_link"]
        if user != None:
            try:
                await user.send(f"Minecord left a server {guild.name}\n{invite}")
            except:
                pass
        with open("server.json", "w") as f:
            data.pop(str(guild.id))
            json.dump(data, f, indent=4)
     
    async def on_guild_join(self, guild: discord.Guild):
        '''Sends a welcome message on joining'''
        channels = guild.channels 
        invite = None
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                if "general" in channel.name or "chat" in channel.name:
                    try:         
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        await channel.send(embed= discord.Embed(title = "Minecord", description=f"Hello Everyone, Thanks for Inviting me\n\nI am Minecord the Minecraft Discord Game Bot\nMy prefisx is ``m``\nUse help command to get help\nCreate a profile using ``mstart`` command and start playing Minecord using ``chop`` ``hunt`` ``adv`` ``go`` ``eat`` ``mine`` and many more commands.\nUse {self.client.user.mention} activate to use minecord in a specific channel only",color = discord.Colour.green()))
                        break
                    except:
                        continue
        else:
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        invite = await channel.create_invite(max_age=0,max_uses=0)
                        await channel.send(embed= discord.Embed(title = "Minecord", description=f"Hello Everyone, Thanks for Inviting me\n\nI am Minecord the Minecraft Discord Game Bot\nMy prefisx is ``m``\nUse help command to get help\nCreate a profile using ``mstart`` command and start playing Minecord using ``chop`` ``hunt`` ``adv`` ``go`` ``eat`` ``mine`` and many more commands.\nUse {self.client.user.mention} activate to use minecord in a specific channel only",color = discord.Colour.green()))
                        break
                    except:
                        continue
        msg = discord.Embed(title=f"Minecord Joined {guild.name}",description=guild.description if guild.description else "No description", color=discord.Color.green(),url=invite)
        if guild.icon:
            msg.set_thumbnail(url=guild.icon.url)
        msg.set_footer(text=f"joined at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= self.client.user.avatar)
        me = self.client.get_user(894072003533877279)
        try:
            await me.send(embed=msg)
        except:
            pass
        with open("server.json", "r") as f:
            data = json.load(f)
        with open("server.json", "w") as f:
            data[str(guild.id)] = {"name": guild.name, "invite_link": str(invite.url), "premium": False, "mob": {}, "places": {}, "allowed_channels":[]}
            json.dump(data, f, indent=4)
        
    
    async def on_disconnect(self):
        with open("data.json", "w") as f:
            json.dump(data,f,indent=4)
        #with open("messages.json", "w") as f:
            #json.dump(message,f,indent=4)
        #with open("server.json", "w") as f:
            #json.dump(server,f,indent=4)

    async def on_command_completion(self, ctx):

        tip = random.randint(1,8)
        try:
            await xp_manager(ctx, random.randint(1,10))
            if tip == 8:
                tip = info["tips"]
                await ctx.send(f"**Quick Tip** : {random.choice(tip)}")
        except Exception as e:
            await self.client.get_user(894072003533877279).send(e)
        if (random.randint(1,10)) == 1:
            await spawn(ctx)

    async def on_command_error(self, ctx, error):
        '''Handelling errors'''
        if isinstance(error, commands.CommandNotFound):
            print("Ignoring command not found error")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("sorry I dont have perms to do that")
        elif isinstance(error, discord.Forbidden):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
          await ctx.reply(embed=discord.Embed(title="Command On Cooldown",description=f"Take a rest, try again after `{int(error.retry_after)}` seconds",color= discord.Color.red()).set_footer(text=f"requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        )
        else:
            print("Unknown error happened")
            user = self.client.get_user(894072003533877279)
            if user != None:
                await user.send(f"Crash report {error}")
            
    async def on_error(self, event_method, *args, **kwargs):
        print(f"Error in event: {event_method}")
        await self.client.get_user(894072003533877279).send(f"Error in event: {event_method}")
