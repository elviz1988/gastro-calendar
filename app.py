from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import calendar

app = Flask(__name__)

@app.template_filter("format_date")
def format_date_filter(value):
    date = datetime.strptime(value, "%Y-%m-%d")
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    return f"{date.day} {months[date.month - 1]} {date.year}"

def get_fixed_holidays(date_str):
    conn = sqlite3.connect('holidays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM holidays WHERE date = ?", (date_str,))
    holidays = [row[0] for row in cursor.fetchall()]
    conn.close()
    return holidays

def get_all_holiday_dates(year, month):
    conn = sqlite3.connect('holidays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM holidays")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return [d for d in dates if d.startswith(f"{year}-{month:02d}")]

@app.route("/")
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    holidays = get_fixed_holidays(today)
    return render_template("index.html", date=today, holidays=holidays, today=today)

@app.route("/calendar")
def calendar_view():
    year = request.args.get("year", default=datetime.today().year, type=int)
    month = request.args.get("month", default=datetime.today().month, type=int)
    if month < 1:
        month, year = 12, year - 1
    elif month > 12:
        month, year = 1, year + 1

    cal = calendar.Calendar(firstweekday=0)
    month_calendar = cal.monthdayscalendar(year, month)
    marked_days = set()
    for date in get_all_holiday_dates(year, month):
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            marked_days.add(d.day)
        except:
            continue

    months = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
    ]
    month_name = months[month - 1]

    return render_template("calendar.html",
                           year=year, month=month,
                           month_name=month_name,
                           month_calendar=month_calendar,
                           marked_days=marked_days)

@app.route("/date/<date_str>")
def show_date(date_str):
    holidays = get_fixed_holidays(date_str)
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template("index.html", date=date_str, holidays=holidays, today=today)

if __name__ == "__main__":
    app.run(debug=True)
