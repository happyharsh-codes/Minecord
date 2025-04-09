import discord 
from discord.ext import commands
import asyncio, datetime, random
from config import*
from functions.game_functions import*

class Events:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message):
        cmd = message.content.lower()[2:]
        if message.author == self.client.user:
            return
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
        #if await func.is_restricted_channel(message):
            #return       
        if self.client.user.mentioned_in(message):
                em = discord.Embed(title= 'Minecord Bot', description= "Hi I am Minecord, The Discord Minecraft bot, my prefix is ```m!```", colour= discord.Colour.green())
                em.set_thumbnail(url = self.client.user.avatar)
                em.add_field(name= "Invite", value="To invite the bot use the ```m!invite``` command")
                em.add_field(name= "Bug Fix", value="Report bugs and suggestions using the ```m!bug``` command")
                await message.channel.send(embed=em)
                return
        if not message.content.startswith("m!"):
            return
        if 'start' in cmd or 'help' in cmd:
            print(f"processing cmd {cmd}")
            await self.client.process_commands(message)        
            return
        if not has_profile(message.author.id):
            await message.channel.send(f"{message.author.mention} you haven't created your profile yet.\nCreate your profile with the ```start``` command and start playing!")
            return
        print(f"processing cmd {cmd}")
        await self.client.process_commands(message)        
      
    async def on_guild_leave(self, guild):
        """Handling when Bot leaves a server"""
        print("left a server")
        user = self.client.get_user(894072003533877279)
        if user != None:
            await user.send(f"Minecord left a server {guild.name}")
    
    async def on_guild_join(self, guild):
        '''Sends a welcome message on joining'''
        channels = guild.channels 
        for channel in channels:
            if "general" in channel.name or "chat" in channel.name:              
                invite = await channel.create_invite()
                await channel.send(embed= discord.Embed(title = "Minecord", description="Hello Everyone, Thanks for Inviting me\n\nI am Minecord the Minecraft Discord Game Bot\nMy prefisx is ```mi!```\nUse help command to get help\n\nSetup the channels automatically using the ```auto_setup``` command or create channels for over world, nether world and end and use ```quick_setup``` command to set up the channels",colour = discord.Colour.green()))
                break
        else:
            for channel in channels:
                try:
                    invite = await channel.create_invite()
                    await channel.send(embed= discord.Embed(title = "Minecord", description="Hello Everyone, Thanks for Inviting me\n\nI am Minecord the Minecraft Discord Game Bot\nMy prefisx is ```mi!```\nUse help command to get help\n\nSetup the channels automatically using the ```auto_setup``` command or create channels for over world, nether world and end and use ```quick_setup``` command to set up the channels",colour = discord.Colour.green()))
                    break
                except:
                    continue
        msg = discord.Embed(title=f"Minecord Joined {guild.name}",description=guild.description, color=discord.Color.green(),url=invite)
        msg.set_thumbnail = guild.icon.url
        msg.set_footer(text=f"joined at {datetime.datetime}", icon_url= self.client.avatar_url)
        me = self.client.get_user(894072003533877279)  
        await me.send(embed=msg)
        
    
    async def on_disconnect(self):
        with open("data.json", "w") as f:
            json.dump(data,f,indent=4)
        with open("messages.json", "w") as f:
            json.dump(message,f,indent=4)
        with open("server.json", "w") as f:
            json.dump(server,f,indent=4)

    async def on_command_completion(self, ctx):
        chance = random.randint(1,3)
        tip = random.randint(1,10)
        if chance == 2:       
            await xp_manager(ctx, random.randint(1,10))
        if tip == 10:
            tip = info["tips"]
            await ctx.send(f"**Quick Tip** : {random.choice(tip)}")
        if (random.randint(1,15)) == 1:
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
          await ctx.reply(embed=discord.Embed(title="Command On Cooldown",description=f"Take a rest, try again after ```{int(error.retry_after)}``` seconds",color= discord.Color.red()).set_footer(text=f"requested by {ctx.author.name} at  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        )
        else:
            print("Unknown error happened")
            user = self.client.get_user(894072003533877279)
            if user != None:
                await user.send(f"Crash report {error}")
                raise error
            
    async def on_error(self, ctx, error):
        await ctx.send("Unfortunate error occured :/\nWe are very sorry")
        raise error
        
    async def on_command_completion(self, ctx):
        pass