import sqlite3 as sql

db_loc = 'amongus.db'

def add_user(user_id, name):
    with sql.connect(db_loc) as db:
        cur = db.cursor()
        cur.execute('''SELECT id FROM players WHERE id = ? ''', (user_id, ))
        r = cur.fetchone()
        if r != None:
            print(f'{user_id} already in database')
            return None
        else:
            cur.execute(''' INSERT INTO players VALUES (?, ?) ''',(user_id, name))
            db.commit()


def post_stats(user_id, stats):
    with sql.connect(db_loc) as db:
        cur = db.cursor()
        cur.execute(
            f'''
            INSERT OR REPLACE INTO stats VALUES ({"?," * 18}?)
            ''',
            (
            stats["Bodies Reported"],
            stats["Emergencies Called"],
            stats["Tasks Completed"],
            stats["All Tasks Completed"],
            stats["Sabotages Fixed"],
            stats["Impostor Kills"],
            stats["Times Murdered"],
            stats["Times Ejected"],
            stats["Crewmate Streak"],
            stats["Times Impostor"],
            stats["Times Crewmate"],
            stats["Games Started"],
            stats["Games Finished"],
            stats["Impostor Vote Wins"],
            stats["Impostor Kill Wins"],
            stats["Impostor Sabotage Wins"],
            stats["Crewmate Vote Wins"],
            stats["Crewmate Task Wins"],
            user_id
            )
        )

def database_operation(user_id, name, stats):
    add_user(user_id, name)
    post_stats(user_id, stats)
