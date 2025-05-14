import json
import discord
import datetime
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def help(self, ctx,*, cmd=None):
        with open ("help.json", 'r') as f:
            help = json.load(f)
        if cmd is None:
            cmd = "Help" 
            fields_dict = {"Activity Commands": "`eat`, `health`, `go`, `craft`, `mine`, `adventure`, `inventory`, `profile`",
            "Over World Commands": "`cave`, `fish`, `crop`, `enchant`, `trade`, `take`, `chest`, `build`",
            "Game Settings Commands": "`start`, `delete`"}
        else:    
            if not cmd in help:
                await ctx.send(f"No help command for {cmd} found.")
                return
            for help_cmd in list(help.keys()):
                if cmd.lower() in help_cmd:
                    fields_dict = {help_cmd: help[help_cmd]}
                    break                 
        em = discord.Embed(title="Help",color=discord.Color.green())
        for i in fields_dict:
            em.add_field(name=i, value= fields_dict[i])
        em.set_footer(text=f"requested by {ctx.author.name} at  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
        
async def setup(bot):
    await bot.add_cog(Help(bot))