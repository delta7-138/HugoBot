import discord
from discord.ext import commands

class User(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(alises = ['uh' , 'userh'])
    async def userhelp(self , ctx):
        embed = discord.Embed(title = "User Info Help" , color = 0xff00ff)
        embed.add_field(name = "Get user avatar" , value = "h.av <mention member> or h.av" , inline = False)
        embed.set_footer(text = "requested by " + ctx.message.author.name)
        embed.set_thumbnail(url = "https://www.videogameschronicle.com/files/2021/05/discord-new-logo.jpg")
        await ctx.reply(embed = embed , mention_author = True)

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