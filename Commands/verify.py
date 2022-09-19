#import hashlib
import discord
from discord.ext import commands
from ruamel.yaml import YAML

import KumosLab.Database.get
import KumosLab.Database.Create.RankCard.custom
import KumosLab.Database.Create.RankCard.vacefron_gen
import KumosLab.Database.Create.RankCard.text

#import vacefron

salt = "CREMINI".encode()

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class verify(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Rank Command
    @commands.command()
    async def verifyMushroom(self, ctx):
        member = ctx.author
        guild = ctx.guild
        print(guild)
        #toHash = str(member) + str(guild)
        #hashResult = hashlib.pbkdf2_hmac('sha256', toHash.encode(), salt, 100000).hex()
        try:
            embed = discord.Embed(description="`Please check your dm`")
            await ctx.send(embed=embed)
            await KumosLab.Database.add.verifyGuild(user=member,  guild=guild)
            await member.send('You want to be cool on Server: `{}` Please authorize Mushroom Card to access your member ID : https://discord.com/api/oauth2/authorize?client_id=1019309208258236416&redirect_uri=https%3A%2F%2Fconnect.mushroom.social%3A3333%2Fapi%2Fauth%2Fdiscord%2Fredirect&response_type=code&scope=identify'.format(guild.name))
           # rank = await KumosLab.Database.Create.RankCard.vacefron_gen.generate(user=member, guild=ctx.guild)
                ##await ctx.reply(file=rank, embed=embed)
        except Exception as e:
            print(f"{e}")
            embed = discord.Embed(description="`Something went wrong`")
            await ctx.send(embed=embed)
            raise e


# Sets-up the cog for rank
def setup(client):
    client.add_cog(verify(client))
