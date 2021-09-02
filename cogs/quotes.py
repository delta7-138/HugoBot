import discord
import requests
import random
import json
from discord.ext import commands
# from dotenv import load_dotenv
# load_dotenv()
class Quotes(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(aliases = ['adv'])
    async def advice(self , ctx):
        member = ctx.message.author
        uname = member.name
        if(member.nick!=None):
            uname = member.nick
        res = requests.get('https://api.adviceslip.com/advice')
        content = json.loads(res.text)
        adviceMsg = content["slip"]["advice"]
        embed = discord.Embed(title = "Advice for stupid people" , description = adviceMsg , color = 0x00ffea)
        embed.set_thumbnail(url = 'https://i0.wp.com/www.brainpickings.org/wp-content/uploads/2014/10/nietzsche1.jpg?w=680&ssl=1')
        embed.set_footer(text = 'requested by ' + uname)
        await ctx.send(embed = embed)

    @commands.command(aliases = ['aniq'])
    async def animequote(self , ctx):
        res = requests.get('https://animechan.vercel.app/api/random')
        content =json.loads(res.text)
        quote = content["quote"]
        character = content["character"]
        anime = content["anime"]
        embed = discord.Embed(title = "Anime Quote" , description = '*' + quote + '*'  , color = 0x00ffea)
        embed.set_footer(text = 'by - ' + character + '\n from - ' + anime)
        embed.set_thumbnail(url = 'https://i.pinimg.com/474x/89/08/61/8908616ffb91db2dbd1b640a374a1ee2.jpg')
        await ctx.send(embed = embed)

    @commands.command(aliases = ['ronq'])
    async def ronswansonquote(self , ctx):
        urls = ['https://hips.hearstapps.com/digitalspyuk.cdnds.net/17/18/1493816780-ron-swanson.jpg' , 'https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F13%2F2016%2F10%2F16%2FRon-Swanson-e1476642015275.jpg&q=85' , 'https://i.pinimg.com/originals/50/26/8f/50268f506228d83a5253f57225672c42.png']
        member = ctx.message.author
        name = member.name
        if(member.nick!=None):
            name = member.nick
        res = requests.get("https://ron-swanson-quotes.herokuapp.com/v2/quotes")
        content = json.loads(res.text)
        embed = discord.Embed(title = "Ron Swanson Quote" , description = content[0] , color = 0xff0000)
        embed.set_thumbnail(url = urls[random.randint(0 , len(urls)-1)])
        embed.set_footer(text = "requested by " + name)
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Quotes(bot))