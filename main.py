from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
app = FastAPI()

origins = [
    "0.0.0.0:5173",
    "0.0.0.0:5174",
    "http://localhost:5175",
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:5172",
    "http://localhost:5171",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_game_table():
    sql_create_game_table = """ Create TABLE IF NOT EXISTS game (
                                                 game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 date INTEGER UNIQUE,
                                                 winner text
    );"""
    
    conn = sqlite3.connect('./master.db')
    c = conn.cursor()
    c.execute(sql_create_game_table)
    conn.commit()
    conn.close()

def create_turns_table():
    sql_create_turns_table = """ Create TABLE IF NOT EXISTS turns (
                                                 turn_id INTEGER,
                                                 game_id INTEGER,
                                                 red_score INTEGER,
                                                 black_score INTEGER,
                                                 active_player TEXT,
                                                 move_start TEXT,
                                                 move_end TEXT
    )"""
    
    conn = sqlite3.connect('./master.db')
    c = conn.cursor()
    c.execute(sql_create_turns_table)
    conn.commit()
    conn.close()

@app.get('/fetch_game_ids')
async def fetch_game_ids():
    print('testing fetch_game_ids')
    conn = sqlite3.connect("./master.db")
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM game""")
        results = c.fetchall()
        return results
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()

@app.post('/fetch_replays')
async def fetch_replay(request: Request):
    print('/fetch_replays')
    data = await request.json()
    game_id = data['game_id']
    conn = sqlite3.connect("./master.db")
    c = conn.cursor()
    try:
        c.execute("""SELECT * FROM turns WHERE game_id = ?""", (game_id,))
        results = c.fetchall()
        return results
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()

@app.post('/export_replay')
async def insert_replay(request: Request):

    print('export_replay')
    conn = sqlite3.connect("./master.db")
    c = conn.cursor()
    batch_insert = []
    
    try:
        data = await request.json()
        winner = data['winner']
        date = data['date']
        print('Received JSON data:', data)
        c.execute("""INSERT INTO game (date, winner) VALUES (?, ?)""", (date, winner))
        print(date)
        print(winner)

        game_id = c.lastrowid

        print(game_id)
        for turn in data['data']:
            print((game_id, turn['turn_id'], turn['red_score'], turn['black_score'], turn['active_player'], turn['move_start'], turn['move_end']))
            batch_insert.append((game_id, turn['turn_id'], turn['red_score'], turn['black_score'], turn['active_player'], turn['move_start'], turn['move_end']))
        
        c.executemany("INSERT INTO turns (game_id, turn_id, red_score, black_score, active_player, move_start, move_end) VALUES (?, ?, ?, ?, ?, ?, ?)", batch_insert)
        conn.commit()
        return 'success'
    except Exception as e:
        print('Error:', e)
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    finally:
        conn.close()
    
@app.post('/delete_game')
async def delete_replay(body: dict):
    game_id = body['game_id']
    print('/delete_game')
    conn = sqlite3.connect("./master.db")
    c = conn.cursor()
    try:
        c.execute("""DELETE FROM game WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM turns WHERE game_id = ?""", (game_id,))
        conn.commit()
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()
    
create_game_table()
create_turns_table()




    
    



