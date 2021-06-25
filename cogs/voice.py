import discord
import datetime 
from discord.ext import commands

data = {}
class User(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command(aliases = ['j'])
    async def join(self , ctx):
        channel = ctx.message.author.voice.channel
        if(channel==None):
            await ctx.reply('Join a VC first :nerd:' , mention_author = True)
        else:
            await channel.connect()
            now = datetime.datetime.now()

    @commands.command(aliases = ['dc'])
    async def disconnect(self , ctx):
        await ctx.voice_client.disconnect()
        now = datetime.datetime.now()

def setup(bot):
    bot.add_cog(User(bot))
