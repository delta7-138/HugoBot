import discord
import os
import random
import requests
import lyricsgenius
from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image
from listofnames import first_names,last_names
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
client = commands.Bot(command_prefix = '+')
client.remove_command('help')
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def help(ctx):
    embed = discord.Embed(title = 'Hugo Help' , color=0x00ffea)
    embed.add_field(name = "Command to greet Hugo" , value = "+hello" , inline = False)
    embed.add_field(name = "Command to generate a random color" , value = "+color" , inline = False)
    embed.add_field(name = "Command to generate random name" , value = "+randomname" , inline = False)
    embed.add_field(name = "Command to get MARS rover(Curiosity)" , value = "+mars ``sol_number``" , inline = False)
    await ctx.send(embed = embed)

@client.command()
async def hello(ctx): 
    await ctx.send(f'Hello There!')

@client.command()
async def color(ctx):
    hex_number_string = '#'
    for i in range(6):
        randnum = random.randint(0 , 15)
        hexstr = str(hex(randnum)).upper()
        hexelem = hexstr[2:]
        hex_number_string = hex_number_string + hexelem
        
    hex_int = int(hex_number_string[1:] , 16)
    im = Image.new("RGB" , (100 , 100) , hex_number_string)
    im.save('randcolor.png')
    file = discord.File('randcolor.png')
    embed = discord.Embed(title = 'Random Color' , color = hex_int)
    embed.add_field(name = "Color" , value = hex_number_string)
    embed.set_image(url = 'attachment://randcolor.png')
    await ctx.send(file = file , embed = embed) 

@client.command(aliases = ['rand'])
async def randomname(ctx):
    f_ind = random.randint(0 , len(first_names)-1)
    l_ind = random.randint(0 , len(last_names)-1)
    random.shuffle(first_names)
    random.shuffle(last_names)
    await ctx.send(first_names[f_ind] + " " + last_names[l_ind])

@client.command()
async def mars(ctx , * , sol):
    try:
        gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=' + sol + '&api_key=' + API_TOKEN)
        gdata = gres.json()
        await ctx.send(gdata['photos'][0]['img_src'])
    except: 
        await ctx.send('Sol number out of range :pensive:')

client.run(TOKEN)
