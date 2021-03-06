import discord
import os
import random
import requests
import datetime as dt
from math import *
import numpy as np

from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image
from listofnames import first_names,last_names
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
client = commands.Bot(command_prefix = 'h.')
client.remove_command('help')
modes = [100 , 200 , 127 , 265 , 246 , 110 , 1 , 34 , 124 , 245]

def distortImage(im):
    pixels = im.load()
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            k = (random.randint(0 , int(floor(im.size[0]/66))))
            l = (random.randint(0 , int(floor(im.size[1]/66))))
            k = k**2
            if(i+k<im.size[0] and j+l<im.size[1]):
                tmp = list(pixels[i+k , j+l])
                im.putpixel((i , j) , tuple(tmp))    
    return im

def randomGen(num):
    val = (random.randint(1 , num))**2
    tmpvar = val
    ans = 0
    for i in range(2):
        ans = ans * 10 + tmpvar%10
        tmpvar = tmpvar/10

    return int(ans)
    
def randomizeImage(url):
    im = Image.open(requests.get(url , stream = True).raw)
    pixels = im.load()
    xmax = im.size[0]
    ymid = im.size[1]/2

    # xarr = list(range(0 , xmax-3))

    # yarr = list(map(sin , xarr))
    # for i in range(len(yarr)):
    #     yarr[i] = int(ymid + floor(ymid/3 * yarr[i]))
    #     print(yarr[i])

    
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            tmp = list(pixels[i , j]) 
            k = random.randint(0 , 2)
            l = random.randint(0 , 2)
            random.seed(modes[random.randint(0 , 9)])
            tmp[k] = randomGen(random.randint(156 , 255))
            tmp[l] = randomGen(random.randint(1 , 255))
            im.putpixel((i , j) , tuple(tmp))

    # for i in range(xmax-3):
    #     if(yarr[i]>=0 and yarr[i]<=2 * ymid):
    #         im.putpixel((xarr[i] , yarr[i]) , (0 , 0 ,0))
    return im

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    

@client.command()
async def help(ctx):
    embed = discord.Embed(title = 'Hugo Help' , color=0x00ffea)
    embed.add_field(name = "Command to greet Hugo" , value = "h.hello" , inline = False)
    embed.add_field(name = "Command to generate a random color" , value = "h.color" , inline = False)
    embed.add_field(name = "Command to generate random name" , value = "h.randomname ``number_of_names``" , inline = False)
    embed.add_field(name = "Command to get MARS rover(Curiosity) images as per sol" , value = "h.mars ``sol_number`` ``cameratype in [fhaz , rhaz , chemcam, mast ,mahli, mardi, navcam]`` ``rover_name as in [curiosity , spirit , opportunity]``" , inline = False)
    embed.add_field(name = "Command to get Astronomy picture of the Day" , value = "h.apod" , inline = False)
    embed.add_field(name = "Command to get random number" , value = "h.randomnum or h.nrand ``lowerbound`` ``upperbound``" , inline = False)
    embed.add_field(name = "Command to get shoegaze avatar" , value = "h.shoegaze or h.sg" , inline = False)
    embed.add_field(name = "Command to get shoegaze filter on an image" , value = "h.shoegazeimage or h.sgi" , inline = False)
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
    if(len(args)==1):
        sol = args[0]
        gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=' + sol + '&camera=fhaz&api_key=' + API_TOKEN)
        gdata = gres.json()
        ind = random.randint(0 , len(gdata['photos'])-1)
        await ctx.send(gdata['photos'][ind]['img_src'])
    else:
        try:
            reference_args = {'o' : 'opportunity' , 'c' : 'curiosity' , 's' : 'spirit'}
            sol = args[0]
            cam = args[1].lower()
            rover = reference_args[args[2].lower()]
            #print(rover)
            gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/' + rover + '/photos?sol=' + sol + '&camera=' + cam + '&api_key=' + API_TOKEN)
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
    # embed.add_field(name = gdata['title'] , value = gdata['explanation'])
    embed.set_image(url = gdata['hdurl'])
    await ctx.send(embed = embed)

@client.command(aliases = ['nrand'])
async def randomnum(ctx , *args):
    try:
        num1 = int(args[0])
        num2 = int(args[1])
        if(num1>num2):
            await ctx.send('First argument should be less than the second one')
        elif(num1==num2):
            await ctx.send('Do you really want a random number :|')
        else:
            randnum = random.randint(num1 , num2)
            await ctx.send(randnum)
    except:
        await ctx.send('Please send valid input :pleading_face:')

@client.command(aliases = ['sg'])
async def shoegaze(ctx , member :  discord.Member): 
    im = randomizeImage(member.avatar_url)   
    ext = 'png' 
    if(im.format=='GIF'):
        im.save('avatar.gif' , save_all = True)
        ext = 'gif'
    else:
        im.save('avatar.png')
    fil = discord.File('avatar.' + ext)
    embed = discord.Embed(title = "Here is a shoegaze version of the avatar")
    embed.set_image(url = 'attachment://avatar.' + ext)  
    await ctx.send(file = fil , embed = embed) 
             
@shoegaze.error
async def shoegaze_err(ctx , err):
     if isinstance(err , commands.MissingRequiredArgument):
        im = randomizeImage(ctx.message.author.avatar_url)    
        im.save('avatar.png')
        fil = discord.File('avatar.png')
        embed = discord.Embed(title = "Here is a shoegaze version of the avatar")
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 

     if isinstance(err , commands.BadArgument):
         await ctx.send('Dude atleast tag a valid member :unamused:')

@client.command(aliases = ['sgd'])
async def shoegazedistort(ctx , member :  discord.Member): 
    im = randomizeImage(member.avatar_url)   
    im = distortImage(im)
    ext = 'png' 
    if(im.format=='GIF'):
        im.save('avatar.gif' , save_all = True)
        ext = 'gif'
    else:
        im.save('avatar.png')
    fil = discord.File('avatar.' + ext)
    embed = discord.Embed(title = "Here is a shoegaze version of the avatar with distortion")
    embed.set_image(url = 'attachment://avatar.' + ext)  
    await ctx.send(file = fil , embed = embed) 
             
@shoegazedistort.error
async def shoegazed_err(ctx , err):
     if isinstance(err , commands.MissingRequiredArgument):
        im = randomizeImage(ctx.message.author.avatar_url)    
        im = distortImage(im)
        im.save('avatar.png')
        fil = discord.File('avatar.png')
        embed = discord.Embed(title = "Here is a shoegaze version of the avatar with distortion")
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 

     if isinstance(err , commands.BadArgument):
         await ctx.send('Dude atleast tag a valid member :unamused:')
@client.command(aliases = ['sgi'])
async def shoegazeimage(ctx , *args):
    #try: 
        im = randomizeImage(args[0])
        addage = ""
        if(len(args)==2 and args[1]=='-d'):
            im = distortImage(im)
            addage = " with distortion"
        im.save('avatar.png')
        fil = discord.File('avatar.png')
        embed = discord.Embed(title = "Here is a shoegaze version of the image" + addage)
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 
    #except:
    #   await ctx.send("invalid url :pensive:")
client.run(TOKEN)
