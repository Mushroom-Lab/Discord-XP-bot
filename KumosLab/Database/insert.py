import os
import sqlite3

import discord
from pymongo import MongoClient
from ruamel import yaml

with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

if config['Database_Type'].lower() == 'mongodb':
    MONGODB_URI = os.environ['MONGODB_URI']
    COLLECTION = os.getenv("COLLECTION")
    DB_NAME = os.getenv("DATABASE_NAME")
    cluster = MongoClient(MONGODB_URI)
    levelling = cluster[COLLECTION][DB_NAME]
async def message(message_id, author, guild_id):
    levelling.insert_one({"message_id": message_id, "author": author, "guild_id":guild_id}
                         )
async def userField(member: discord.Member, guild: discord.Guild):
    db_type = config["Database_Type"]
    if db_type.lower() == "mongodb":
        levelling.insert_one(
            {"guild_id": guild.id, "user_id": member.id, "name": str(member), "level": 1, "xp": 0,
             "background": config['Default_Background'], "xp_colour": config['Default_XP_Colour'], "blur": 0,
             "border": config['Default_Border']})
async def userFieldSync(member: discord.Member, guild: discord.Guild, xp, level):
    levelling.insert_one(
            {"guild_id": guild.id, "user_id": member.id, "name": str(member), "level": level, "xp": xp,
             "background": config['Default_Background'], "xp_colour": config['Default_XP_Colour'], "blur": 0,
             "border": config['Default_Border']})
   