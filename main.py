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
        ctx = message[msg][4]
        if "Travelling" in em.title:
            ter = " "
        elif "Mining" in em.title:
            ter = "\n"
        words = em.description.split(ter)
        message[msg][3] +=1
        words[1] = f"{info["id"]["progress_filled"]*message[msg][3]}{info["id"]["progress_empty"]*(10-message[msg][3])}"
        em.description = ter.join(words)
        em.set_footer(text=f"Updated at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        #Updating messages
        await msg.channel.send(embed=em)
        food_level(ctx, -random.randint(1,10))
        if message[msg][1] != None:
            await message[msg][1].edit(embed=em)
        if message[msg][3] == 10:
            if "Travelling" in em.title:
                data[str(ctx.author.id)]["location"] = data[str(ctx.author.id)]["location"].split()[-1]
            elif "Mining" in em.title:
                blocks_mined = mining_result(ctx, message[msg][5])
                descrip = "You mined out: \n"
                for block in blocks_mined:
                    descrip += f"{info["id"][block]} {block.replace("_", " ").capitalize()} x {blocks_mined[block]}\n"
                    await add_item(ctx, ctx.author.id, block, blocks_mined[block])
                    await tool_manager(ctx,message[msg][5], random.randint(1,3)*blocks_mined[block])
                em = discord.Embed(title="Mining Result", description=descrip, color=discord.Color.green())
                await ctx.send(content=f"<@{ctx.author.id}> your mining results", embed=em)

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
            try:
                user = client.get_user(int(id))
                await user.send("Ayoo your health is very low!!\nTry eating something with the *m!eat* command")
            except:
                pass
            if data[id]["health"] <= 0:
                await kill(id)
        elif data[id]["food"] <= 0:
            data[id]["health"] -= random.randint(1,10)
            if data[id]["health"] <= 0:
                await kill(id, client.get_user(int(id)), "You starved to death")
            else:
                try:
                    await client.get_user(int(id)).send("Ayoo you are starving to death!!\nEat something quickly using the *m!eat* command")
                except:
                    pass
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