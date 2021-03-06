import discord, asyncio
from os import system
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption, ButtonStyle
import json
import sqlite3
from datetime import datetime
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

def sql_join():
    try:
        sql = sqlite3.connect("base.db")
        me = sql.cursor()
        return sql, me
    except:
        return False, False

def check_q_channel(user_id, admin):
    sql, me = sql_join()
    if sql:
        me.execute(f"SELECT * FROM check_q_channel WHERE user_id = {user_id} AND admin = '{admin}'")
        sql.commit()
        result = me.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return True
    else:
        return True

def create_channel_db(channel_id, user_id, admin):
    sql, me = sql_join()
    if sql:
        me.execute(f"INSERT INTO check_q_channel (channel_id, user_id, admin) values ({channel_id}, {user_id}, '{admin}')")
        sql.commit()
        sql.close()

def delete_channel_db(channel_id, admin):
    sql, me = sql_join()
    if sql:
        me.execute(f"DELETE FROM check_q_channel WHERE channel_id = {channel_id} AND admin = '{admin}'")
        sql.commit()
        sql.close()

def get_channel_id(user_id):
    sql, me = sql_join()
    if sql:
        me.execute(f"SELECT * FROM check_q_channel WHERE user_id = {user_id}")
        sql.commit()
        result = me.fetchone()
        sql.close()
        if result is None:
            return 0
        return result[0]

def check_channel(channel_id):
    sql, me = sql_join()
    if sql:
        me.execute(f"SELECT * FROM check_q_channel WHERE channel_id = {channel_id}")
        sql.commit()
        result = me.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return True
    else:
        return False

def check_user(channel_id):
    sql, me = sql_join()
    if sql:
        me.execute(f"SELECT * FROM check_q_channel WHERE channel_id = {channel_id}")
        sql.commit()
        result = me.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return result[1]
    else:
        return False

@client.event
async def on_ready():
    print("READY")
    DiscordComponents(client)

@client.event
async def on_message(message):
    if message.author.bot:
        return None
    guild = client.get_guild(777206826420404225) #????????? ???????????????
    log_channel = client.get_channel(976041129176862740) #????????? ???????????????
    admin_role = discord.utils.get(guild.roles, name="???????KOR5M Admin") #????????? ??????????????? ????????? ???????????? ?????? ????????? ???????????????

    if admin_role in message.author.roles:
        if message.content.startswith("#??????"):
            with open("config.json", 'r', encoding='utf-8 sig') as file:
                data = json.load(file)
                components = []
                for i in data["config"]:
                    if data['config'][i]['color'] == "green":
                        style = ButtonStyle.green
                    elif data['config'][i]['color'] == "blue":
                        style = ButtonStyle.blue
                    elif data['config'][i]['color'] == "red":
                        style = ButtonStyle.red
                    else:
                        style = ButtonStyle.gray
                    components.append(Button(label=data["config"][i]["btn_name"], custom_id=data["config"][i]["btn_id"], style=style))
            await message.channel.send(
                embed=discord.Embed(description=f"> ????????? ???????????? ???????????? ???????????? ????????? ???????????????\n\n> ????????? ?????? ?????? ??? ????????? ??????????????????\n\n> ?????? ??????????????? ????????? ???????????? ??? ????????????"),
                components = [ 
                    components
                ]
            )
        elif message.content.startswith("#????????????"):
            admin = message.channel.category.name
            file = discord.File(f"log/{message.channel.id}.txt")
            now = datetime.now()
            new_author = client.get_user(int(check_user(message.channel.id)))
            embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), color=0x50bcdf, timestamp=message.created_at)
            embed.add_field(name="?????? ?????? ??????", value=f"????????? ?????? : <@{new_author.id}>\n\n?????? ?????? ????????? : <@{message.author.id}>", inline=True)
            embed.set_footer(text='SYSTEM', icon_url=client.user.avatar_url)
            await log_channel.send(embed=embed)
            log = await log_channel.send(file=file)
            os.remove(f"log/{message.channel.id}.txt")
            delete_channel_db(message.channel.id, admin)
            await message.channel.delete()
            await new_author.send(embed=discord.Embed(description=f"??????????????? {new_author.name}???\n\n> ?????? {admin}????????? ????????? ?????????????????? ?????? ??????????????????????????? ?????? ????????? ???????????? ??????????????????"))
    elif message.content.startswith("#????????????"):
        print(message.channel.category.id)
    elif message.content.startswith("#??????"):
        print(message.guild.id)
    if check_channel(message.channel.id) == True:
        if message.attachments:
            open(f"log/{message.channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{message.author.name}({message.author} | {message.author.id}) : {message.content}, {message.attachments[0].url}\n")
        else:
            open(f"log/{message.channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{message.author.name}({message.author} | {message.author.id}) : {message.content}\n")

@client.event
async def on_button_click(interaction):
    guild = client.get_guild(777206826420404225) #????????? ???????????????
    user1 = discord.utils.get(guild.roles, name="???????USER")
    user2 = discord.utils.get(guild.roles, name="??????? USER")
    user3 = discord.utils.get(guild.roles, name="??????? USER")
    if interaction.responded:
        return
    id = interaction.custom_id
    with open("config.json", 'r', encoding='utf-8 sig') as file:
        data = json.load(file)
        if data['config'][id]:
            if check_q_channel(interaction.author.id, id) == True:
                await interaction.send(embed=discord.Embed(description=f"?????? ?????? ??????????????? ??????????????? ????????? ??????????????????\n\n> ?????? : <#{get_channel_id(interaction.author.id)}>"))
            else:
                overwrites = {
                    user1: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                    user2: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                    user3: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                    interaction.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                channel = await interaction.guild.create_text_channel(interaction.author.name, category=client.get_channel(int(data['config'][id]['category'])))
                create_channel_db(channel.id, interaction.author.id, id)
                await channel.edit(overwrites=overwrites) 
                await interaction.send(embed=discord.Embed(description=f"?????? ??????????????? ????????? ????????? ????????? ?????????????????????\n\n> ?????? ?????? : <#{channel.id}>"))
                now = datetime.now()
                open(f"log/{channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{now.strftime('%Y - %m - %d')} ?????? ?????? ?????????\n")
                embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), description=f"{interaction.author.name}?????? ????????? ???????????????!", color=0x50bcdf)
                embed.set_footer(text='SYSTEM', icon_url=client.user.avatar_url)
                await channel.send(content="@everyone", embed=embed)
                

client.run("ODczODg4MzA1Njc3MjA1NTU1.GBy4w4.IvdHhl9jZ6M9dAn_p0BmBRQIh-Dc40o08SgQSk")
