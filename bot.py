import discord
import os
import random
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$randommsg'):
        channel = discord.utils.get(message.guild.text_channels, name="general")
        messages = await channel.history(limit=1000).flatten()
        if(len(messages)!=0):
            while(True):
                ind = random.randint(0 , len(messages))
                if(messages[ind].author.bot):
                    continue
                elif(messages[ind].content=='$random'):
                    continue
                else:
                    embed=discord.Embed(title='Jump', url='https://discord.com/channels/' + str(messages[ind].guild.id) + "/" + str(messages[ind].channel.id) + "/" + str(messages[ind].id), description=messages[ind].content)
                    embed.set_author(name=messages[ind].author.name, icon_url=messages[ind].author.avatar_url)
                    if(messages[ind].attachments):
                        embed.set_image(url = messages[ind].attachments[0].url)
                    await message.channel.send(embed = embed)
                    break

    if message.content=='$help':
        embed = discord.Embed(title = 'Hugo Help' , color=0x00ffea)
        embed.add_field(name = "Command to greet Hugo" , value = "stfu hugo" , inline = False)
        embed.add_field(name = "Command to print out random message" , value = "$random" , inline = False)
        embed.add_field(name = "Command to generate a random color" , value = "$color" , inline = False)
        await message.channel.send(embed = embed)

    if message.content=='$color':
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
        await message.channel.send(file = file , embed = embed)

client.run(TOKEN)