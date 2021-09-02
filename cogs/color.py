import discord
from discord.ext import commands
import random
from PIL import Image
from io import BytesIO
# from dotenv import load_dotenv
# load_dotenv()

class Color(commands.Cog):
    def __init__(self , bot):
        self.bot = bot
    
    @commands.command(aliases = ['ch'])
    async def colorhelp(self , ctx):
        sender = ctx.message.author
        nick = sender.name
        if(sender.nick!=None):
            nick = sender.nick
        embed = discord.Embed(title = 'Hugo Color Help' , color = 0x00ffea)
        embed.add_field(name = "Random color" , value = "h.color aliases(h.col)")
        embed.add_field(name = "Generate color with hex code" , value = "h.genc `hexcode` aliases(h.gencolor)")
        embed.set_thumbnail(url = 'https://cdn.britannica.com/70/191970-131-A85628DA/Color-wheel-light-color-spectrum.jpg')
        embed.set_footer(text = 'requested by ' + nick)
        await ctx.send(embed = embed)

    @commands.command(aliases = ['col'])
    async def color(self , ctx):
        hex_number_string = '#'
        for i in range(6):
            randnum = random.randint(0 , 15)
            hexstr = str(hex(randnum)).upper()
            hexelem = hexstr[2:]
            hex_number_string = hex_number_string + hexelem
            
        hex_int = int(hex_number_string[1:] , 16)
        im = Image.new("RGB" , (100 , 100) , hex_number_string)
        buffer = BytesIO()
        im.save(buffer , "png")
        buffer.seek(0)
        file = discord.File(filename = 'randcolor.png' , fp = buffer)
        embed = discord.Embed(title = 'Random Color' , color = hex_int)
        embed.add_field(name = "Color" , value = hex_number_string)
        embed.set_image(url = 'attachment://randcolor.png')
        await ctx.send(file = file , embed = embed) 

    @commands.command(aliases = ['genc' , 'gencol' , 'gc'])
    async def gencolor(self , ctx , * , args):
        hex_number_string = args.upper()
        hex_int = 0
        if(len(hex_number_string)!=7):
            await ctx.send("invalid hex :rage:")
            return ;
        try:
            hex_int = int(hex_number_string[1:] , 16)
            im = Image.new("RGB" , (100 , 100) , hex_number_string)
            buffer = BytesIO()
            im.save(buffer , "png")
            buffer.seek(0)
            file = discord.File(filename = 'color.png' , fp = buffer)
            embed = discord.Embed(title = 'Color' , color = hex_int)
            embed.add_field(name = "Color" , value = hex_number_string)
            embed.set_image(url = 'attachment://color.png')
            await ctx.send(file = file , embed = embed) 
        except:
            await ctx.send("invalid hex :rage:")

def setup(bot):
    bot.add_cog(Color(bot))