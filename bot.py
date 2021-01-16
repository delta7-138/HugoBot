import discord
import os
import random
import requests

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
    embed.add_field(name = "Command to generate random name" , value = "+randomname ``number_of_names``" , inline = False)
    embed.add_field(name = "Command to get MARS rover(Curiosity) images as per sol" , value = "+mars ``sol_number`` ``cameratype in [fhaz , rhaz , chemcam, mast ,mahli, mardi, navcam]``" , inline = False)
    embed.add_field(name = "Command to get Astronomy picture of the Day" , value = "+apod" , inline = False)
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
async def randomname(ctx , *args):
    if(len(args)==1):
        num = int(args[0])
        if(num<=5 and num>0):
            final_msg = ""
            for i in range(num):
                f_ind = random.randint(0 , len(first_names)-1)
                l_ind = random.randint(0 , len(last_names)-1)
                random.shuffle(first_names)
                random.shuffle(last_names)
                name = first_names[f_ind] + " " + last_names[l_ind]
                final_msg = final_msg + name + "\n"
                    
            await ctx.send(final_msg)

        elif(num==0):
            await ctx.send("Do you really want a name or you just want to waste my time?") 
        else:
            await ctx.send("How many names do you need man! :nerd:")
    elif(len(args)==0):
        f_ind = random.randint(0 , len(first_names)-1)
        l_ind = random.randint(0 , len(last_names)-1)
        random.shuffle(first_names)
        random.shuffle(last_names)
        name = first_names[f_ind] + " " + last_names[l_ind]
        await ctx.send(name)
    else:
        await ctx.send("Send valid arguments ya :nerd:")

@client.command()
async def mars(ctx , *args):
    try:
        sol = args[0]
        cam = args[1].lower()
        gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=' + sol + '&camera=' + cam + '&api_key=' + API_TOKEN)
        gdata = gres.json()
        ind = random.randint(0 , len(gdata['photos'])-1)
        await ctx.send(gdata['photos'][ind]['img_src'])
    except: 
        await ctx.send('Image not available :pensive:')

@client.command()
async def apod(ctx):
    gres = requests.get('https://api.nasa.gov/planetary/apod?api_key=' + API_TOKEN)
    gdata = gres.json()
    embed = discord.Embed(title = 'Astronomy Picture Of the Day' , color = 0x0000ff)
    embed.add_field(name = 'Date' , value = gdata['date'])
    embed.add_field(name = gdata['title'] , value = gdata['explanation'])
    embed.set_image(url = gdata['hdurl'])
    await ctx.send(embed = embed)
client.run(TOKEN)
