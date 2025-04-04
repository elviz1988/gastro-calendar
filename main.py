from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import os

app = FastAPI()

# Подключаем статические файлы (HTML/JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Функция для подключения к SQLite
def get_db():
    return sqlite3.connect("data/holidays.db")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def main_page():
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

# API для получения праздника по дате
@app.get("/api/holiday")
async def get_holiday(date: str):  # Формат: "YYYY-MM-DD"
    month_day = date[5:10]  # "MM-DD"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, description FROM holidays WHERE date=?", (month_day,))
    result = cursor.fetchone()
    conn.close()
    return {"holiday": result} if result else {"holiday": None}

# API для получения всех праздников (для календаря)
@app.get("/api/all_holidays")
async def get_all_holidays():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, name FROM holidays")
    holidays = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return holidays