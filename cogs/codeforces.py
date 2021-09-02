import discord 
import random
import requests
import urllib.parse
import json
from discord.ext import commands
# from dotenv import load_dotenv
# load_dotenv()

class Codeforces(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(aliases = ['cfhelp' , 'cfshelp'])
    async def codeforceshelp(self , ctx):
        embed = discord.Embed(title = "Codeforces problems help menu")
        embed.add_field(name = "Request random Codeforces problem" , value = "[h.cfrand , h.codefrand , h.codeforcesrandomprob]" , inline = False)
        embed.add_field(name = "Reqeust Codeforces problem by one tag" , value = "h.cft <tag>" , inline = False)
        embed.set_thumbnail(url = "https://codeforces.com/predownloaded/3b/86/3b8616d876e29762202e93e184d4373eb62e7274.png")
        embed.set_footer(text = "requested by a nerd")
        await ctx.reply(embed = embed , mention_author = True)

    @commands.command(aliases = ['codefrand' , 'cfrand'])
    async def codeforcesrandomprob(self , ctx):
        res = requests.get('http://codeforces.com/api/problemset.problems')
        content = json.loads(res.text)
        probNum = random.randint(0 , len(content["result"]["problems"]))
        prob = content["result"]["problems"][probNum]
        embed = discord.Embed(title = prob["name"] , url = "http://codeforces.com/problemset/problem/" + str(prob["contestId"]) + "/" + prob["index"] , description = 'Type : *' + prob["type"] + '*')
        embed.add_field(name = "points" , value = prob["points"], inline = False)
        embed.add_field(name = "rating" , value = prob["rating"], inline = False)
        tmpstr = ""
        for i in prob["tags"]:
            tmpstr = tmpstr + i + "\n"
        embed.add_field(name = "tags" , value = tmpstr)
        embed.set_footer(text = "Random codeforces problem requested by a nerd")
        embed.set_thumbnail(url = 'https://codeforces.com/predownloaded/3b/86/3b8616d876e29762202e93e184d4373eb62e7274.png')
        await ctx.send(embed = embed)

    @commands.command(aliases = ['cftag' , 'cft'])
    async def codeforcesprobwithtag(self , ctx , * , args):
        tags = urllib.parse.urlencode({'tags' : args})
        res = requests.get('http://codeforces.com/api/problemset.problems?' + tags)
        content = json.loads(res.text)
        if(len(content["result"]["problems"])==0):
            await ctx.message.add_reaction("😠")
            await ctx.send("Invalid tags :nerd:")
        else:
            probNum = random.randint(0 , len(content["result"]["problems"]))
            prob = content["result"]["problems"][probNum]
            points = "-"
            if("points" in prob and prob["points"]!=None):
                points = prob["points"]
            embed = discord.Embed(title = prob["name"] , url = "http://codeforces.com/problemset/problem/" + str(prob["contestId"]) + "/" + prob["index"] , description = 'Type : *' + prob["type"] + '*' , color = 0xfffbff)
            embed.add_field(name = "points" , value = points, inline = False)
            embed.add_field(name = "rating" , value = prob["rating"], inline = False)
            tmpstr = ""
            for i in prob["tags"]:
                tmpstr = tmpstr + i + "\n"
            embed.add_field(name = "tags" , value = tmpstr)
            embed.set_footer(text = "Random " + args + " problem requested by a nerd")
            embed.set_thumbnail(url = 'https://codeforces.com/predownloaded/3b/86/3b8616d876e29762202e93e184d4373eb62e7274.png')
            rating = int(prob["rating"])
            emoji = ""
            if(rating<=1200):
                emoji = "🚮"
            elif(rating<=2200):
                emoji = "😈"
            else:
                emoji = "😨"
            await ctx.message.add_reaction("✅")
            msg = await ctx.send(embed = embed)
            await msg.add_reaction(emoji)

def setup(bot):
    bot.add_cog(Codeforces(bot))
