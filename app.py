
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import calendar
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

app = Flask(__name__)

@app.template_filter("format_date")
def format_date_filter(value):
    date = datetime.strptime(value, "%Y-%m-%d")
    return date.strftime("%-d %B %Y")

def get_holidays_for_date(date_str):
    conn = sqlite3.connect('holidays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM holidays WHERE date = ?", (date_str,))
    holidays = cursor.fetchall()
    conn.close()
    return [h[0] for h in holidays]

def get_all_holiday_dates():
    conn = sqlite3.connect('holidays.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM holidays")
    dates = cursor.fetchall()
    conn.close()
    return set([d[0] for d in dates])

@app.route("/")
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    holidays = get_holidays_for_date(today)
    return render_template("index.html", date=today, holidays=holidays)

@app.route("/calendar")
def calendar_view():
    year = request.args.get("year", default=datetime.today().year, type=int)
    month = request.args.get("month", default=datetime.today().month, type=int)
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    month_calendar = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    holiday_dates = get_all_holiday_dates()

    marked_days = set()
    for date_str in holiday_dates:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            if d.year == year and d.month == month:
                marked_days.add(d.day)
        except:
            continue

    month_name = datetime(year, month, 1).strftime('%B')
    return render_template("calendar.html",
                           year=year,
                           month=month,
                           month_name=month_name,
                           month_calendar=month_calendar,
                           marked_days=marked_days)

@app.route("/date/<date_str>")
def show_date(date_str):
    holidays = get_holidays_for_date(date_str)
    return render_template("index.html", date=date_str, holidays=holidays)

if __name__ == "__main__":
    app.run(debug=True)
