#!/env/bin/python
# bot.py
import os
import sqlite3 as sql
import random

from read_img import process_stats
from database_commands import database_operation, post_stats

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import csv
import chat_exporter
import io

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('TOKEN')
USER_TO_SEND = int(os.getenv('USER_TO_SEND'))
GUILD = int(os.getenv('GUILD'))
database_loc = 'amongus.db'

def read_wilk_data():
    with open('data.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        wilk_data = [i for i in csv_reader]
        return wilk_data[1]

def add_wilk_data(stats, wilk_base):
    stats["Bodies Reported"] += int(wilk_base[0])
    stats["Emergencies Called"] += int(wilk_base[1])
    stats["Tasks Completed"] += int(wilk_base[2])
    stats["All Tasks Completed"] += int(wilk_base[3])
    stats["Sabotages Fixed"]+= int(wilk_base[4])
    stats["Impostor Kills"]+= int(wilk_base[5])
    stats["Times Murdered"]+= int(wilk_base[6])
    stats["Times Ejected"]+= int(wilk_base[7])
    # stats["Crewmate Streak"]+= int(wilk_base[8])
    stats["Times Impostor"]+= int(wilk_base[9])
    stats["Times Crewmate"]+= int(wilk_base[10])
    stats["Games Started"]+= int(wilk_base[11])
    stats["Games Finished"]+= int(wilk_base[12])
    stats["Impostor Vote Wins"]+= int(wilk_base[13])
    stats["Impostor Kill Wins"]+= int(wilk_base[14])
    stats["Impostor Sabotage Wins"]+= int(wilk_base[15])
    stats["Crewmate Vote Wins"]+= int(wilk_base[16])
    stats["Crewmate Task Wins"]+= int(wilk_base[17])
    return stats


bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print("Logged In")
    change_status.start()
    chat_exporter.init_exporter(bot)


@bot.command(name='players', description='list of players in the database')
async def list_players(ctx):
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(''' SELECT name FROM players  ''') 
        results = cur.fetchall()

    players = [name[0].title() for name in results]
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
    player = random.choice(players)
    with sql.connect(database_loc) as db:
        cur = db.cursor()
        cur.execute(''' SELECT id, message FROM messages WHERE category  = 1 ''' )
        options = cur.fetchall()
        message = random.choice(options)
        await ctx.send(f"{player} {message[1]}")
        cur.execute(''' UPDATE messages SET use_count = use_count + 1 WHERE id = ? ''', (message[0],))



@bot.command(name='upload_stats', description='reads a screenshot attached to feed the database with stats')
async def upload_stats(ctx):
    players_roles = [role.id for role in ctx.author.roles]
    required_server = bot.get_guild(id=GUILD)
    role = discord.utils.get(required_server.roles, id=807475316477132871)
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = f"temp/{ctx.message.author.name}_{attachment.filename}"
            await attachment.save(file_name)
            stats = process_stats(file_name)
            if stats != None:
                if ctx.author.id == USER_TO_SEND:
                    wilk_base = read_wilk_data()
                    stats = add_wilk_data(stats, wilk_base)
                    await ctx.send('LaWilk is a special case')
                database_operation(ctx.author.id, ctx.author.name.lower(), stats)
                print(f"{ctx.author} stats added")
                if 807475316477132871 not in players_roles:
                    await ctx.author.add_roles(role)
                    await ctx.author.send(f"{ctx.author.mention} You have been added to the Crewmates")
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
        data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[1], reverse = True)} 
    response = ''
    for k, v in data.items():
        response += f'{k}: {v}%\n'
    print(f"{ctx.author} called wins")
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
        data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[1], reverse = True)} 
    response = ''
    for k, v in data.items():
        response += f'{k}: {v}\n'
    await ctx.send(response)

@bot.command(name="throw_sus")
async def throw_sus(ctx):
    print(f"{ctx.author.name} called throw_sus" )
    members = ctx.guild.members
    members_in_voice = [member.name for member in members if member.voice]
    if len(members_in_voice) > 1:            
        random_choices = random.sample(members_in_voice, k=2)
        string = f'{random_choices[0]} and {random_choices[1]} are defo the imposters! Kick em!'
        await ctx.send(string)
    else:
        await ctx.send("This meeting has been called illegally!")

@tasks.loop(seconds=20)
async def change_status():
    with open('tasks.txt') as f:
        tasks = f.readlines()
    tasks.append("Watching Jay Sleep")
    msg = f"Among Us: {random.choice(tasks).title()}"
    await bot.change_presence(activity=discord.Game(name=msg))


@bot.command(name="add_msg")
async def add_msg(ctx, *, args):
    #Check Roles:
    #target the user manually to get his roles in the event of a DM
    required_server = bot.get_guild(id=GUILD)
    target_user = discord.utils.get(required_server.members, id=ctx.author.id)

    role_id = 807475316477132871
    if role_id in [i.id for i in target_user.roles]:
        cut_string = args.split(' ', 1)
        category = cut_string[0]
        write_string = cut_string[1]

        with sql.connect(database_loc) as db:
            cur = db.cursor()
            cur.execute(''' SELECT * FROM categories WHERE name = ?''',(category,))
            cat = cur.fetchone()
            if cat != None:
                cur.execute(''' INSERT INTO messages (message, added_by, category) VALUES (?,?,?) ''',
                (write_string, ctx.author.id, cat[0]))
                print(f"{ctx.author.name} sent a message")
                await ctx.send('Added! If you want to add Easter messages. Use `easter` option')
            else:
                cur.execute(''' SELECT name FROM categories ''')
                names = [i[0] for i in cur.fetchall()]
                names_str = ', '.join(names)
                await ctx.send(f"The categories you can add to are: {names_str}")
   
    else:
        await ctx.send('You need Crewmate Role to post this!')


@bot.command(name="good_bot")
async def thanks(ctx):
    await ctx.send(f"Why, thanks {ctx.author.mention} :dog: :robot:")


@bot.command(name="export")
async def save(ctx, limit=7000):
    if ctx.author.guild_permissions.administrator == True:
        messages = await ctx.channel.history(limit=limit).flatten()
        transcript = await chat_exporter.raw_export(ctx.channel, messages)

        if transcript is None:
            return

        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                    filename=f"transcript-{ctx.channel.name}.html")

        await ctx.author.send(file=transcript_file)
    else:
        ctx.send("You have no authority here, Jackie Weaver")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        with open('errormsgs.txt') as f:
            msgs = f.readlines()
        r = f"{random.choice(msgs).strip()}, find commands by running `!help`"
        await ctx.send(r)
    raise error


bot.run(TOKEN)
