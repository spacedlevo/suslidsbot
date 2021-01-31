#!/env/bin/python
# bot.py
import os
import sqlite3 as sql
import random

from read_img import process_stats
from database_commands import database_operation, post_stats

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
database_loc = 'amongus.db'

bot = commands.Bot(command_prefix='!')

@bot.command(name='players', description='list of players in the database')
async def list_players(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(''' SELECT name FROM players  ''') 
        results = cur.fetchall()

    players = [name[0].title() for name in results]
    print(players)
    response = ' \n'.join(players)
    await ctx.send(response)

@bot.command(name='leaderboard', description='call a statistic from the database to order a leaderboard')
async def leaderboards(ctx, stat):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(f''' SELECT players.name, {stat} 
                        FROM stats 
                        JOIN players ON stats.player_id = players.id 
                        ORDER BY {stat} DESC
                        ''')
        results = cur.fetchall()
    data = {}
    response = ''
    for i in results:
        data[i[0].title()] = str(i[1])
    print(f"{ctx.author} called {stat} leaderboard")
    for k, v in data.items():
        response += f'{k}: {v}\n'


    await ctx.send(response)


@bot.command(name='percent', description='like leaderboard but %')
async def percent(ctx, stat='imp_kills'):
    imp_games = ['imp_vote_wins', 'imp_kill_wins', 'imp_sab_wins']
    if stat in imp_games:
        game_variable = 'times_imp'
    else:
        game_variable = 'games_started'
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(f''' SELECT players.name, {stat}, {game_variable}  
                        FROM stats 
                        JOIN players ON stats.player_id = players.id 
                        ORDER BY {stat} DESC
                        ''')
        results = cur.fetchall()
    data = {}
    response = ''
    for i in results:
        data[i[0].title()] = round((i[1] / i[2]) * 100)
    data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[1], reverse = True)} 
    print(f"{ctx.message.author} called % for {stat}")
    for k, v in data.items():
        response += f'{k}: {v}%\n'


    await ctx.send(response)

@bot.command(name='stats', description='shows a list of the stats columns')
async def stat_list(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute('SELECT * FROM stats')
        cols = [desc[0] for desc in cur.description]
    response = ' ,\n'.join(cols)

    await ctx.send(response)

@bot.command(name='whose_sus?', description='shoot in the dark to whose the imp')
async def whosus(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(''' SELECT name FROM players  ''') 
        results = cur.fetchall()

    players = [name[0].title() for name in results]
    response = random.choice(players)
    with open('options.txt') as f:
        options = f.readlines()
    await ctx.send(response + ' ' + random.choice(options).strip())


@bot.command(name='upload_stats', description='reads a screenshot attached to feed the database with stats')
async def upload_stats(ctx):
    if ctx.message.attachments:
        print(f"Got attachment: {ctx.message.attachments}")
        for attachment in ctx.message.attachments:
            file_name = f"temp/{ctx.message.author.name}_{attachment.filename}"
            await attachment.save(file_name)
            stats = process_stats(file_name)
            if stats != None:
                database_operation(ctx.author.id, ctx.author.name.lower(), stats)
                print(f"{ctx.author} stats added")
            else:
                print(f"{ctx.author} stats failed")
            os.remove(file_name)
        
        with open('tasks.txt') as f:
            tasks = f.readlines()
        await ctx.send(f"{ctx.message.author.name} {random.choice(tasks).strip()}... Task Complete!")

@bot.command(name='wins', description='calculates sum of ways to win either imp/crew and finds % times you win. add imposter or crewmate as argument')
async def win_rate(ctx, play_type):
    if play_type == 'imposter':
        cols = 'imp_vote_wins, imp_kill_wins, imp_sab_wins, times_imp'
    elif play_type == 'crewmate':
        cols = 'crew_vote_wins, crew_task_wins, times_crew'
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(f''' SELECT players.name, {cols}  
                        FROM stats 
                        JOIN players ON stats.player_id = players.id
                        ''')

        r = cur.fetchall()
    data = {}
    for i in r:
        data[i[0].title()] =  round((sum(i[1:-1]) / i[-1]) * 100)
        print(i)
        data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[1], reverse = True)} 
    print(data)
    response = ''
    for k, v in data.items():
        response += f'{k}: {v}%\n'
    await ctx.send(response)

@bot.command(name="kills_per_game", description="Leaderboard of how many kills per imp game")
async def kills_per_game(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(f''' SELECT players.name, imp_kills, times_imp  
                        FROM stats 
                        JOIN players ON stats.player_id = players.id
                        ''')

        r = cur.fetchall()
        data = {}

    for i in r:
        data[i[0].title()] =  round(i[1] / i[2],1)
        print(i)
        data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[1], reverse = True)} 
    print(data)
    response = ''
    for k, v in data.items():
        response += f'{k}: {v}\n'
    await ctx.send(response)

@bot.command(name="append_stats")
async def append_stats(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(''' SELECT * FROM stats WHERE player_id = ?''', (ctx.author.id,))
        q = cur.fetchone()
    if ctx.message.attachments:
        print(f"Got attachment: {ctx.message.attachments}")
        for attachment in ctx.message.attachments:
            file_name = f"temp/{ctx.message.author.name}_{attachment.filename}"
            await attachment.save(file_name)
            stats = process_stats(file_name)
            stats["Bodies Reported"] += q[0]
            stats["Emergencies Called"] += q[1]
            stats["Tasks Completed"] += q[2]
            stats["All Tasks Completed"] += q[3]
            stats["Sabotages Fixed"]+= q[4]
            stats["Impostor Kills"]+= q[5]
            stats["Times Murdered"]+= q[6]
            stats["Times Ejected"]+= q[7]
            stats["Crewmate Streak"]+= q[8]
            stats["Times Impostor"]+= q[9]
            stats["Times Crewmate"]+= q[10]
            stats["Games Started"]+= q[11]
            stats["Games Finished"]+= q[12]
            stats["Impostor Vote Wins"]+= q[13]
            stats["Impostor Kill Wins"]+= q[14]
            stats["Impostor Sabotage Wins"]+= q[15]
            stats["Crewmate Vote Wins"]+= q[16]
            stats["Crewmate Task Wins"]+= q[17]

    post_stats(ctx.author.id, stats)
    os.remove(file_name)
        



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        with open('errormsgs.txt') as f:
            msgs = f.readlines()
        r = f"{random.choice(msgs).strip()}, find commands by running `!help`"
        await ctx.send(r)
    raise error
bot.run(TOKEN)
