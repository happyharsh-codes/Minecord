import discord
from discord.ext import commands, tasks
import asyncio, os
from functions.events import Events
from functions.game_functions import*
from config import *
from keep_alive import keep_alive
    
intents = discord.Intents(messages = True, guilds = True, dm_messages = True, members = True, presences = True, dm_reactions = True, reactions = True, emojis = True, emojis_and_stickers = True, message_content = True) 
client = commands.Bot(command_prefix= 'm!', case_insensitive=True, help_command=None, intents = intents )
event = Events(client)

#-----On Ready-----#
@client.event
async def on_ready():
    print(f"Bot is ready. Logged in as {client.user}")
    print("We are ready to go!")
    await client.change_presence(activity=discord.Game(name="Minecraft"))
    loop.start()
    dumping_loop.start()

#-----Loop-----#
@tasks.loop(seconds=20)
async def loop():
    print("Updating messages")
    for msg in message:
        if message[msg][2] == "loc_change":
            pass
        elif message[msg][2] == "health_change":
            pass
        em = message[msg][3]
        em.footer.text=f"Updated at {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        await msg.edit(embed=em)
        if message[msg][1] != None:
            await message[msg][1].edit(embed=em)

@tasks.loop(minutes=1)
async def dumping_loop():
    print("dumping files")
    with open("data.json", "w") as f:
        json.dump(data,f,indent=4)
    with open("messages.json", "w") as f:
        json.dump(message,f,indent=4)
    with open("server.json", "w") as f:
        json.dump(server,f,indent=4)

#-----Events-----#
client.event(event.on_message)
client.event(event.on_guild_join)
client.event(event.on_guild_leave)
client.event(event.on_command_error)
client.event(event.on_command_completion)
client.event(event.on_disconnect)
client.event(event.on_error)

async def load_cogs():
    await client.load_extension("cogs.Activity")
    await client.load_extension("cogs.Help")

async def main():
    async with client:
        await load_cogs()  # Load cogs before running the bot
        await client.start(os.getenv("TOKEN"))  # Start the bot

asyncio.run(main())