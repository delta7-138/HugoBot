import discord
import datetime
import requests
import json
import os
import time
import random
import urllib.request
from discord.ext import commands
# from dotenv import load_dotenv
# load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')   

class Mars(commands.Cog):
    def __init__(self , bot):
        self.bot = bot
    
    async def maxsol(self , rovername , today):
        startc = 1344191400 
        if(rovername=="c"):
            diff = time.mktime(today.timetuple()) - startc
            days_diff = diff/60/60/24 - 100
            return days_diff
        elif(rovername=="s"):
            diff = 2200
            return diff
        elif(rovername=="o"):
            return 5100

    @commands.command()
    async def apod(self , ctx):
        try:
            result = requests.get('https://api.nasa.gov/planetary/apod?api_key=' + API_TOKEN)
            content = result.json()
            url = ""
            date = content["date"]
            title = content["title"]
            description = content["explanation"]
            if("hdurl" in content):
                url = content["hdurl"]
            else:
                url = content["url"]
            
            embed = discord.Embed(title = "Astronomy picture of the day",  description = "**Title** : {} \n **Date** : {} \n **Description** : {} \n".format(title , date , description) , color = 0xffefef)
            embed.set_image(url = url)
            embed.set_footer(text = "requested by {}".format(ctx.message.author.name))
            await ctx.reply(embed = embed , mention_author = True)
        except:
            await ctx.reply("Image not available :pensive:" , mention_author = True)

    @commands.command()
    async def mars(self, ctx , *args):
        try:
            reference_args = {'o' : 'opportunity' , 'c' : 'curiosity' , 's' : 'spirit'}
            dict_params = {'rover' : ""  , 'camera type' : "" , 'sol' : 0 , 'url' : ""}
            list_vals = []
            for i in args:
                list_vals.append(i)
            
            for i in range(3 - len(args)):
                list_vals.append("")

            if(list_vals[0]==""):
                randrover = list(reference_args.keys())[random.randint(0 , 2)]
                dict_params['rover'] = randrover
            else:
                dict_params['rover'] = list_vals[0]
            
            if(list_vals[1]==""):
                dict_params['camera type'] = 'fhaz'
            else:
                dict_params['camera type'] = list_vals[1]
            
            if(list_vals[2]==""):
                today = datetime.datetime.today()
                maxlimit = await self.maxsol(dict_params['rover'] , today)
                randsol = random.randint(1 , int(maxlimit))
                dict_params['sol'] = randsol
            else:
                dict_params['sol'] = int(list_vals[2])
                
            gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/' + reference_args[dict_params['rover']]+ '/photos?sol=' + str(dict_params['sol']) + '&camera=' + dict_params['camera type'] + '&api_key=' + API_TOKEN)
            gdata = gres.json()
            ind = random.randint(0 , len(gdata['photos'])-1)
            dict_params['url'] = gdata['photos'][ind]['img_src']

            embed = discord.Embed(title = "MARS ROVER IMAGE" , color = 0x934838)
            embed.add_field(name = "Rover name" , value = reference_args[dict_params['rover']] , inline = False)
            embed.add_field(name = "Camera Type" , value = dict_params['camera type'] , inline = False)
            embed.add_field(name = "Sol" , value = dict_params['sol'] , inline = False)
            embed.set_image(url = dict_params['url'])
            embed.set_footer(text = "requested by a nerd")
            await ctx.reply(embed = embed , mention_author = True)
        except: 
            await ctx.reply("No image available :pensive:" , mention_author = True)

    @commands.command(aliases = ['e' , 'eimg'])
    async def earth(self , ctx , latitude, longitude):
        async with ctx.typing(): 
            today = datetime.datetime.today().strftime('2021-01-01')
            print(API_TOKEN)
            base_url = 'https://api.nasa.gov/planetary/earth/imagery?lon=' + longitude + '&lat='  + latitude + '&date=' + today + '&api_key=' + API_TOKEN + '&dim=0.15'
            urllib.request.urlretrieve(base_url, "earth.jpg")
            fil = discord.File('earth.jpg')
            embed = discord.Embed(title = 'Earth', color = 0x0000ff)
            embed.set_image(url = 'attachment://earth.jpg')
            embed.set_footer(text = 'provided by NASA APIs')
            await ctx.send(embed = embed , file = fil)

    @commands.command(aliases = ['marsh' , 'mh'])
    async def marshelp(self , ctx):
        embed = discord.Embed(title = "Mars Help" , description = "Basic Format of command is `h.mars <rover name> <camera type> <sol number>` \n **rover name** = 'c' 'o' or 's'\n **camera type** = 'fhaz' 'rhaz' 'navcam' 'mardi' 'mast' 'chemcam' \n **sol number** is an rover day number on mars ", color = 0x934838)
        embed.set_footer(text = "requested by a nerd")
        embed.set_thumbnail(url = "https://mars.nasa.gov/system/content_pages/main_images/418_marsglobe.jpg")
        await ctx.reply(embed = embed , mention_author = True)

def setup(bot):
    bot.add_cog(Mars(bot))