import discord
import requests
import json
import urllib.parse
from discord.ext import commands
# from dotenv import load_dotenv
# load_dotenv()
class Teleport(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(aliases = ['sol'])
    async def standardofliving(self , ctx , * , args):
        queryCity = urllib.parse.urlencode({'search' : args})
        res1 = requests.get('https://api.teleport.org/api/cities/?' + queryCity)
        content1 = json.loads(res1.text)
        nextUrl = content1['_embedded']['city:search-results'][0]['_links']['city:item']['href']

        if(nextUrl):
            try:
                res2 = requests.get(nextUrl)
                content2 = json.loads(res2.text)
                nextnextUrl = content2['_links']['city:urban_area']['href'] + 'scores'
                res3 = requests.get(nextnextUrl)
                content3 = json.loads(res3.text)
                city_score = content3['teleport_city_score']
                embed = discord.Embed(title = 'Teleport City Summary for ' + args.upper(), color = 0x00ffea)
                embed.add_field(name = 'Teleport City Score' , value = str(city_score) , inline = False)
                categories = content3['categories']
                flip = True
                ctr = 1
                for i in content3['categories']:
                    if(ctr%3==0):
                        flip = False
                    else:
                        flip = True

                    ctr+=1
                    embed.add_field(name = i['name'] , value = i['score_out_of_10'] , inline = flip)

                embed.set_footer(text = 'data provided by Teleport api')
                embed.set_thumbnail(url = 'https://www.plantemoran.com/-/media/images/insights-images/2018/04/thinking-about-becoming-a-smart-city.jpg?h=704&w=1100&la=en&hash=0F4F54BBECD3E501765A064202A24F8851D74E04')
                await ctx.send(embed = embed)
            except: 
                await ctx.send("City not available :pensive: :v:")
        else:
            await ctx.send('invalid input :pensive:')

def setup(bot):
    bot.add_cog(Teleport(bot))