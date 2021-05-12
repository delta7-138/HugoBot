import discord
from discord.ext import commands

class User(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command(aliases = ['av' , 'avtr'])
    async def avatar(self , ctx , member : discord.Member):
        embed = discord.Embed(title = "Member avatar" , color = 0xff00ff)
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed , mention_author = True)

    @avatar.error
    async def avatar_err(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            embed = discord.Embed(title = "Member avatar" , color = 0xff00ff)
            embed.set_image(url = member.avatar_url)
            await ctx.reply(embed = embed ,mention_author = True)
        
        if isinstance(err , commands.BadArgument):
            await ctx.reply("Wrong argument" , mention_author = True)

def setup(bot):
    bot.add_cog(User(bot))
