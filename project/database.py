import aiosqlite

async def init_db():
    async with aiosqlite.connect("support.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                department TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def save_request(user_id, message, department):
    async with aiosqlite.connect("support.db") as db:
        await db.execute(
            "INSERT INTO requests (user_id, message, department) VALUES (?, ?, ?)",
            (user_id, message, department)
        )
        await db.commit()