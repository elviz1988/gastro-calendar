from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    return sqlite3.connect("data/holidays.db")

# Всегда возвращаем HTML-интерфейс (и для Telegram, и для браузера)
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# API для получения праздника
@app.get("/api/holiday")
async def get_holiday(date: str):
    try:
        month_day = date[5:10]  # Получаем "MM-DD"
        conn = get_db()
        conn.row_factory = sqlite3.Row  # Важно: для доступа по именам колонок
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, description FROM holidays WHERE date = ?",
            (month_day,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "holiday": {
                    "name": result["name"],
                    "description": result["description"]
                }
            }
        return {"holiday": None}

    except Exception as e:
        print(f"Ошибка при запросе к БД: {e}")
        return {"holiday": None}

# API для всех праздников
@app.get("/api/all_holidays")
async def get_all_holidays():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, name FROM holidays")
    holidays = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return holidays