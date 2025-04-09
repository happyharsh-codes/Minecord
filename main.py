import discord
from discord.ext import commands, tasks
import asyncio, os
from functions.events import Events
from functions.game_functions import*
from config import *
from keep_alive import keep_alive
from dotenv import load_dotenv
from datetime import datetime, UTC
load_dotenv()
    
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
    for msg in list(message):
        print("Updating messages")
        em = message[msg][2]
        words = em.description.split()
        message[msg][3] +=1
        words[1] = f"{info["id"]["progress_filled"]*message[msg][3]}{info["id"]["progress_empty"]*(10-message[msg][3])}"
        em.description = " ".join(words)
        em.set_footer(text=f"Updated at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=message[msg][4].author.avatar)
        #Updating messages
        await msg.channel.send(embed=em)
        food_level(message[msg][4], -random.randint(1,10))
        if message[msg][1] != None:
            await message[msg][1].edit(embed=em)
        if message[msg][3] == 10:
            data[str(message[msg][4].author.id)]["location"] = data[str(message[msg][4].author.id)]["location"].split()[-1]
            del message[msg]
    #changing health
    for id in data:
        if data[id]["health"] != data[id]["max_health"] and data[id]["food"] >= 90:
            data[id]["health"] += random.randint(1,10)
            if data[id]["health"] >= data[id]["max_health"]:
                data[id]["health"] = data[id]["max_health"]
        elif 0 < data[id]["food"] < 30:
            data[id]["food"] -= random.randint(1,7)
            data[id]["health"] -= random.randint(1,10)
            if data[id]["health"] <= 0:
                await kill(id)
        elif data[id]["food"] <= 0:
            await kill(id, message[msg][4].author, "You starved to death")

@tasks.loop(minutes=1)
async def dumping_loop():
    print("dumping files")
    with open("data.json", "w") as f:
        json.dump(data,f,indent=4)
    #with open("messages.json", "w") as f:
        #json.dump(message,f,indent=4)
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
    await client.load_extension("cogs.activity")
    await client.load_extension("cogs.help")

async def main():
    async with client:
        await load_cogs()  # Load cogs before running the bot
        await client.start(os.getenv("TOKEN"))  # Start the bot
keep_alive()
asyncio.run(main())