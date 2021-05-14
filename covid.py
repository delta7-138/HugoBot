import discord
import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from discord.ext import commands

class Covid(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(aliases = ['cvw' , 'covidwld' , 'covw' , 'covidw'])
    async def covidworld(self , ctx , *args):
        res = requests.get('https://covid-api.mmediagroup.fr/v1/cases')
        content = json.loads(res.text)
        param = ""
        if(len(args)<1):
            await ctx.send("Missin Arguments :nerd:")
            return ;

        if(args[0]=='-d'):
            param = "deaths"
        elif(args[0]=='-r'):
            param = "recovered"
        elif(args[0]=='-c'):
            param = "confirmed"
        else:
            await ctx.send("Send appropriate argument :rage:")
            return ;
        
        resDict = dict()
        for key,value in content.items():
            deaths = int(value["All"][param])
            resDict[key] = deaths
        
        resDict = sorted(resDict.items(), key=lambda item: item[1] , reverse= True)
        countries = list()
        numbers = list()
        for i in range(10):
            countries.append(resDict[i][0])
            numbers.append(resDict[i][1])
        
        fig, ax = plt.subplots(figsize =(16, 9))
        ax.barh(countries, numbers)
        ax.set_title("COVID " + param.upper()) 

        for s in ['top', 'bottom', 'left', 'right']:
            ax.spines[s].set_visible(False)
        
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.xaxis.set_tick_params(pad = 5)
        ax.yaxis.set_tick_params(pad = 10)

        for i in ax.patches:
            ax.text(i.get_width()+0.2, i.get_y()+0.5, str(round((i.get_width()), 2)),fontsize = 20, fontweight ='bold',color ='grey')
        buffer = BytesIO()
        plt.savefig(buffer , format = "png")
        buffer.seek(0)
        plt.close()
        fil = discord.File(filename = 'cvwd.png' , fp = buffer)
        await ctx.send(file = fil)

@commands.command(aliases = ['cvc'])
async def covidcountry(self , ctx , *args):
    res = requests.get('https://covid-api.mmediagroup.fr/v1/cases')
    content = json.loads(res.text)
    country = ""
    for i in range(len(args)-1):
        country = country + " " + args[i]
    
    print(country)
    country = country.strip()
    param = ""
    try:
        countrydata = content[country]
        if(len(args)<2):
            await ctx.send("Missin Arguments :nerd:")
            return ;

        if(args[-1]=='-d'):
            param = "deaths"
        elif(args[-1]=='-r'):
            param = "recovered"
        elif(args[-1]=='-c'):
            param = "confirmed"
        else:
            await ctx.send("Send appropriate argument :rage:")
            return ;
        
        resDict = dict()
        for key,value in countrydata.items():
            tmp = int(value[param])
            resDict[key] = tmp
        
        resDict = sorted(resDict.items(), key=lambda item: item[1] , reverse= True)
        states = list()
        numbers = list()
        maxrange = 10 if(len(resDict)>=10) else len(resDict) 

        for i in range(maxrange):
            states.append(resDict[i][0])
            numbers.append(resDict[i][1])
        
        fig, ax = plt.subplots(figsize =(16, 9))
        ax.barh(states, numbers)
        ax.set_title("COVID " + param.upper()) 

        for s in ['top', 'bottom', 'left', 'right']:
            ax.spines[s].set_visible(False)
        
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.xaxis.set_tick_params(pad = 5)
        ax.yaxis.set_tick_params(pad = 10)

        for i in ax.patches:
            ax.text(i.get_width()+0.2, i.get_y()+0.5, str(round((i.get_width()), 2)),fontsize = 20, fontweight ='bold',color ='grey')
        buffer = BytesIO()
        plt.savefig(buffer , format = "png")
        buffer.seek(0)
        plt.close()
        fil = discord.File(filename = 'cvc.png' , fp = buffer)
        embed = discord.Embed(title = "Summary for " + country.upper() , color = 0xff0000)
        embed.set_footer(text = 'data provided by https://covid-api.mmediagroup.fr/v1/')
        await ctx.send(file = fil , embed = embed)
    except:
        await ctx.send("Invalid Country name :rage:")

def setup(bot):
    bot.add_cog(Covid(bot))