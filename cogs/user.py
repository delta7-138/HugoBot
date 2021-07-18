import discord
import urllib.parse as urlparse
import json
from discord.ext import commands
from .image import ImageClass

class User(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command(aliases = ['av' , 'avtr'])
    async def avatar(self , ctx , member : discord.Member):
        obj = ImageClass()
        domHex = await obj.getDomninantColor(member.avatar_url)
        embed = discord.Embed(title = "Member avatar" , color = int(domHex , 16))
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed , mention_author = True)

    @avatar.error
    async def avatar_err(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            obj = ImageClass()
            domHex = await obj.getDomninantColor(member.avatar_url)
            embed = discord.Embed(title = "Member avatar" , color = int(domHex , 16))
            embed.set_image(url = member.avatar_url)
            await ctx.reply(embed = embed ,mention_author = True)
        
        if isinstance(err , commands.BadArgument):
            await ctx.reply("Wrong argument" , mention_author = True)

    @commands.command(aliases = ['m' , 'avm' , 'mergeav'])
    async def avatarmerge(self , ctx , member:discord.Member):
        newobj = ImageClass()
        await newobj.mergeImages(ctx.message.author.avatar_url , member.avatar_url)
        fil = discord.File('out.png')
        embed = discord.Embed(title = "Merged Avatars")
        embed.set_image(url = 'attachment://out.png')
        await ctx.reply(embed = embed , file = fil , mention_author = True)

    @commands.command(aliases = ['invc' , 'ic' , 'iuc'])
    async def colorInvertUrl(self , ctx , url):
        newobj = ImageClass()
        await newobj.getColorInvert(url)
        fil = discord.File('outpic.png')
        await ctx.send(file = fil)
    
    @colorInvertUrl.error
    async def colorinv_error(self , ctx , err):
        if isinstance(err, commands.MissingRequiredArgument):
            url = ctx.message.author.avatar_url
            newobj = ImageClass()
            await newobj.getColorInvert(url)
            fil = discord.File('outpic.png')
            await ctx.send(file = fil)
    
    @commands.command(aliases = ['tl' , 's'])
    async def tellme(self , ctx , * , args): 
        queryString = urlparse.urlencode({'q' : args})
        baseUrl = 'https://api.duckduckgo.com/?format=json&pretty=1'
        res = requests.get(baseUrl , params = queryString)
        content = json.loads(res.text)
        
        
def setup(bot):
    bot.add_cog(User(bot))
