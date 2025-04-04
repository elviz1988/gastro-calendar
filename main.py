from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from datetime import datetime

# Инициализация FastAPI
app = FastAPI()

# Настройка CORS (для работы с Telegram Web App)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов (HTML/CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Функция для работы с базой данных
def get_db():
    conn = sqlite3.connect("data/holidays.db")
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    return conn


# Главная страница (открывается из Telegram Web App)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Проверяем, что запрос пришел из Telegram
    user_agent = request.headers.get("User-Agent", "")
    if "TelegramBot" in user_agent or "tgWebAppData" in user_agent:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())

    # Если запрос не из Telegram - можно вернуть API-документацию
    return HTMLResponse("""
        <h1>Гастрономический календарь API</h1>
        <p>Используйте Telegram бота для доступа к интерфейсу</p>
        <p>API endpoints:</p>
        <ul>
            <li>/api/holiday?date=YYYY-MM-DD</li>
            <li>/api/all_holidays</li>
        </ul>
    """)


# API для получения праздника по дате
@app.get("/api/holiday")
async def get_holiday(date: str):
    try:
        # Проверка формата даты
        datetime.strptime(date, "%Y-%m-%d")
        month_day = date[5:10]  # Получаем "MM-DD"

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, description FROM holidays WHERE date = ?",
            (month_day,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "date": date,
                "holiday": dict(result)
            }
        return {"message": "Праздников на эту дату нет"}

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Используйте YYYY-MM-DD"
        )


# API для получения всех праздников (для календаря)
@app.get("/api/all_holidays")
async def get_all_holidays():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, name FROM holidays ORDER BY date")
    holidays = {row["date"]: row["name"] for row in cursor.fetchall()}
    conn.close()
    return holidays


# Проверка работоспособности API
@app.get("/health")
async def health_check():
    return {"status": "OK", "timestamp": datetime.now().isoformat()}


# Если файл запускается напрямую (для локальной разработки)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)