import discord
import random 
import datetime
import urllib.parse as urlparse
import json
from discord.ext import commands
from .image import ImageClass
#from dotenv import load_dotenv

#load_dotenv()
class User(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command(aliases = ['av' , 'avtr'])
    async def avatar(self , ctx , member : discord.Member):
        obj = ImageClass()
        #domHex = await obj.getDomninantColor(member.avatar_url)
        embed = discord.Embed(title = "Member avatar" , color = 0xff0000)
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed , mention_author = True)

    @avatar.error
    async def avatar_err(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            obj = ImageClass()
            #domHex = await obj.getDomninantColor(member.avatar_url)
            embed = discord.Embed(title = "Member avatar" , color = 0xff0000)
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

    @commands.command(aliases = ['randmsg' , 'msg'])
    async def randommsg(self , ctx , member : discord.Member):
        channel = ctx.channel
        guild_id = ctx.message.guild.id
        channel_id = channel.id
        days = random.randint(0 , 200)
        random_date = datetime.datetime.now() - datetime.timedelta(days = days)
        messages = await channel.history(limit=500 , oldest_first = True , after = random_date).flatten()
        messages = list(filter(lambda m : m.author==member, messages))
        random.shuffle(messages)
        random.shuffle(messages)
        if(messages==None):
            await ctx.send("No Messages found :( try again")
            return; 

        msgobj = messages[0]
        embed = discord.Embed(title = "Random message sent by user" , description = msgobj.content , url = "https://discord.com/channels/{}/{}/{}".format(guild_id , channel_id , msgobj.id) ,  color = 0xff0000)
        if(len(msgobj.attachments)>0):
            embed.set_image(url = msgobj.attachments[0].url)
        embed.set_footer(text = "sent by {}".format(msgobj.author.name) , icon_url = msgobj.author.avatar_url)
        await ctx.send(embed = embed)
    
    @randommsg.error
    async def rdnmesgerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            channel = ctx.channel
            guild_id = ctx.message.guild.id
            channel_id = channel.id
            days = random.randint(0 , 200)
            random_date = datetime.datetime.now() - datetime.timedelta(days = days)
            messages = await channel.history(limit=500 , oldest_first = True , after = random_date).flatten()
            random.shuffle(messages)
            random.shuffle(messages)
            msgobj = messages[0]
            embed = discord.Embed(title = "Random message sent by user" , description = msgobj.content , url = "https://discord.com/channels/{}/{}/{}".format(guild_id , channel_id , msgobj.id) ,  color = 0xff0000)
            if(len(msgobj.attachments)>0):
                embed.set_image(url = msgobj.attachments[0].url)
            embed.set_footer(text = "sent by {}".format(msgobj.author.name) , icon_url = msgobj.author.avatar_url)
            await ctx.send(embed = embed)
        
        
def setup(bot):
    bot.add_cog(User(bot))
