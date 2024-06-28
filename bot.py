#actual python modules
import discord, os, json, subprocess
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

#my own python files
from geminillm import gemrequest
from urlextract import URLExtract
from cfradar import urlScan
from cfsd import sdgen
from htmlify import makePage
from UploadFile import uploadFileToCloud
import localconverters, nltocommand, cfllm, whispercf

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command()
async def llmreq(ctx, *, msg):
    async with ctx.typing():
        try:
            resp = gemrequest(msg)
        except:
            resp = cfllm.llmrequest("You are a helpful assistant that doesn't use emoji", msg)

        if resp[0] == True:
            await ctx.send(resp[1])
        else:
            await ctx.send("Prompt likely blocked: "+resp[1])

#We should make a "short term memory" and long term memory feature

@bot.command()
async def talk(ctx, *, msg):
    usr = ctx.message.author

    #short term memory: list (gemini API)
    #long term memory: ???

    if not Path("stmemories/"+usr+".json").exists():
        with open("stmemories/"+usr+".json", "w", encoding="utf-8") as mem:
            mem.write("")
            shortTermMemory = ""
    else: 
        with open("stmemories/"+usr+".json", "r", encoding="utf-8") as mem:
            shortTermMemory = json.load(mem)#read short term memory

    async with ctx.typing():
        construct = []
        if shortTermMemory == "":
            construct.append({'role':'user',
        'parts': ["You are a helpful assistant."]})
        else:
            construct = shortTermMemory

        construct.append({'role':'user',
        'parts': [msg]})

        try:
            modelReply = gemrequest(construct)
            await ctx.send(modelReply)
        except:
            await ctx.send("Sorry, something seems to have gone wrong. Please try again. This conversation wasn't recorded into memory.")
            return
        
        construct.append({'role':'model', 'parts': [modelReply]})

        with open("stmemories/"+usr+".json", "w", encoding="utf-8") as mem:
            json.dump(construct, mem)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

bot.run(os.getenv("DISCORD_BOT_TOKEN"))