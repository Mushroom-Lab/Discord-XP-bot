# Imports
import random
import requests
from discord.ext import commands
from pymongo import MongoClient
from ruamel.yaml import YAML
import os
from dotenv import load_dotenv
import sqlite3

import KumosLab.Database.get
import KumosLab.Database.set
import KumosLab.Database.add
import KumosLab.Database.check
import KumosLab.Database.insert

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

# Loads the .env file and gets the required information
load_dotenv()
if config['Database_Type'].lower() == 'mongodb':
    MONGODB_URI = os.environ['MONGODB_URI']
    COLLECTION = os.getenv("COLLECTION")
    DB_NAME = os.getenv("DATABASE_NAME")
    cluster = MongoClient(MONGODB_URI)
    levelling = cluster[COLLECTION][DB_NAME]
    CERAMIC_BE = os.getenv("CERAMIC_BE")
    CERAMIC_BE_PORT = os.getenv("CERAMIC_BE_PORT")
    


class levelsys(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    # @commands.Cog.listener()
    # async def on_reaction_add(self, ctx):
    #     print(ctx, "CTXX")
        
    # @commands.Cog.listener()
    # async def on_reaction_remove(self, ctx):
    #     print(ctx, "CTXXX")
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        event_type = ctx.event_type
        event_id = ctx.message_id
        user_id = ctx.user_id
        if event_type == 'REACTION_ADD':
            preReaction = await levelling.find_one({"message_id": event_id, user_id: {"$exists": True}})
            if preReaction is None:
                #add a field
                addone = await levelling.update_one({"message_id": event_id}, {"$set": {user_id: 1}})
                #add popularity
                findMessage = await levelling.find_one({"message_id": event_id})
                levelling.update_one({"user_id": findMessage.author, "guild_id": findMessage.guild_id}, {"$inc": {'popularity' + 1}} )
            else:
                plus_one = preaction = await levelling.update_one({"message_id": event_id, user_id: {"$exists": True}}, {"$inc" : { user_id: + 1}})
        elif event_type == 'REACTION_REMOVE':
            findMessage = await levelling.find_one({"message_id": event_id, user_id: {"$exists": True}})
            # case as the last emoji from this supporter, minus popularity
            if findMessage.user_id == 1:
                levelling.update_one({"user_id": findMessage.author, "guild_id": findMessage.guild_id}, {"$inc": {'popularity' - 1}} )
            # minus the emoji count    
            await levelling.update_one({"message_id": event_id}, {"user_id" - 1 })
        else:
            pass
        
    @commands.Cog.listener()
    async def on_message(self, ctx):
        print(ctx, "CTX")
        if not ctx.author.bot:
            if ctx.content.startswith(config["Prefix"]):
                return
            
            if config['loader_type'].lower() == 'message':
                user_check = await KumosLab.Database.get.xp(user=ctx.author, guild=ctx.guild)
                if user_check == "User Not Found!":
                    await KumosLab.Database.insert.userField(member=ctx.author, guild=ctx.guild)
            # @TODO write message func
            insert_message = await KumosLab.Database.insert.message(message_id=ctx.id, user_id=ctx.author.user_id, guild_id=ctx.guild_id)
            # filter for MESSAGE_REACTION_ADD
            
            if config['XP_Chance'] is True:
                chance_rate = config['XP_Chance_Rate']
                random_num = random.randint(1, chance_rate)
                if random_num != chance_rate:
                    return

            channels = await KumosLab.Database.get.talkchannels(guild=ctx.guild)
            channel_Array = []
            channel_List = []
            for channel in channels:
                channel_Array.append(channel)
            if len(channel_Array) < 1 or channel_Array[0] is None:
                pass
            else:
                for x in channel_Array:
                    channel = self.client.get_channel(int(x))
                    channel_List.append(channel.name)

            if str(channel_List) == "[]":
                pass
            elif channel_List is not None:
                if ctx.channel.name in channel_List:
                    pass
                else:
                    return

            xp_type = config['xp_type']
            if xp_type.lower() == "normal":
                to_add = config['xp_normal_amount']
                await KumosLab.Database.add.xp(user=ctx.author, guild=ctx.guild, amount=to_add)
            elif xp_type.lower() == "words":
                # get the length of the message
                res = len(ctx.content.split())
                message_length = int(res)
                await KumosLab.Database.add.xp(user=ctx.author, guild=ctx.guild, amount=message_length)
            elif xp_type.lower() == "ranrange":
                # get ranges from config
                min = config['xp_ranrange_min']
                max = config['xp_ranrange_max']
                num = random.randint(min, max)
                await KumosLab.Database.add.xp(user=ctx.author, guild=ctx.guild, amount=num)

            await KumosLab.Database.check.levelUp(user=ctx.author, guild=ctx.guild)

    # on guild join
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # get database type from config file
        db_type = config["Database_Type"]
        if db_type.lower() == "mongodb":
            levelling.insert_one({"guild": guild.id, "main_channel": None, "admin_role": None, "roles": [],
                                  "role_levels": [], 'talkchannels': []})
            for member in guild.members:
                # check if member is a bot
                if not member.bot:
                    levelling.insert_one(
                        {"popularity":0, "guild_id": guild.id, "user_id": member.id, "name": str(member), "level": 1, "xp": 0,
                         "background": config['Default_Background'], "xp_colour": config['Default_XP_Colour'],
                         "blur": 0, "border": config['Default_Border']})

    # on guild leave
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # get database type from config file
        db_type = config["Database_Type"]
        if db_type.lower() == "mongodb":
            levelling.delete_one({"guild": guild.id})
            for member in guild.members:
                levelling.delete_one({"guild_id": guild.id, "user_id": member.id})
        elif db_type.lower() == "local":
            db = sqlite3.connect("KumosLab/Database/Local/serverbase.sqlite")
            cursor = db.cursor()
            sql = "DELETE FROM levelling WHERE guild_id = ?"
            val = (guild.id,)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            for member in guild.members:
                db = sqlite3.connect("KumosLab/Database/Local/userbase.sqlite")
                cursor = db.cursor()
                sql = "DELETE FROM levelling WHERE guild_id = ? AND user_id = ?"
                val = (guild.id, member.id)
                cursor.execute(sql, val)
                db.commit()
            cursor.close()

    # on member join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        def get_from_ceramic(user_id, guild_id):
            url = 'http://{}:{}'.format(CERAMIC_BE, CERAMIC_BE_PORT)
            endpoint = '/ceramic/get_profile'
            data = {'guild_id': guild_id, "user_id": user_id }
            r = requests.get(url+endpoint, params=data)
            return r.json()
        xp_per_level = config['xp_per_level']
        level = get_from_ceramic(member.id, member.guild.id)
        if level['status'] == 1:
            xp = 0
        elif level['status'] == 0:
            level = int(level['profile']['level'])
        xp = sum([i for i in range(level)]) * xp_per_level
        await KumosLab.Database.insert.userFieldSync(member=member, guild=member.guild, xp=xp, level=level)
        

    # on member leave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # get database type from config file
        db_type = config["Database_Type"]
        if db_type.lower() == "mongodb":
            print(member, " ========")
            levelling.delete_one({"guild_id": member.guild.id, "user_id": member.id})
        elif db_type.lower() == "local":
            db = sqlite3.connect("KumosLab/Database/Local/userbase.sqlite")
            cursor = db.cursor()
            sql = "DELETE FROM levelling WHERE guild_id = ? AND user_id = ?"
            val = (member.guild.id, member.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()


def setup(client):
    client.add_cog(levelsys(client))

# End Of Level System
