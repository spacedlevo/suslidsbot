#!/env/bin/python3
# bot.py
import os
import sqlite3 as sql
import random

from read_img import process_stats
from database_commands import database_operation

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
database_loc = 'amongus.db'

bot = commands.Bot(command_prefix='!')

def find_percentage(stats):
    pass


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
    for i in results:
        data[i[0].title()] = str(i[1])
    print(data)
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
    print(data)
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
    await ctx.send(response)


@bot.command(name='upload_stats', description='reads a screenshot attached to feed the database with stats')
async def upload_stats(ctx):
    if ctx.message.attachments:
        print(f"Got attachment: {ctx.message.attachments}")
        print(ctx.author.id)
        for attachment in ctx.message.attachments:
            file_name = f"temp/{ctx.message.author.name}_{attachment.filename}"
            await attachment.save(file_name)
            stats = process_stats(file_name)
            database_operation(ctx.author.id, ctx.author.name.lower(), stats)
            os.remove(file_name)
            await ctx.send(f"I read {ctx.message.author.name}'s stats as {str(stats)}")

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

bot.run(TOKEN)
