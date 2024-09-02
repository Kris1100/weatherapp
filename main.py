from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
import requests
import datetime
import psycopg2
from consts import city, password

app = FastAPI()

url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'


def insertindb(temp):
    connection = psycopg2.connect(user="postgres",
                                  password=password,
                                  host="192.168.66.179",
                                  port="5432")
    cursor = connection.cursor()
    dt = datetime.datetime.now()

    # Проверка существования таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            DATETIME timestamp PRIMARY KEY, 
            TEMP smallint
        )
    """)

    # Вставка данных
    insert_query = """ INSERT INTO temperature (DATETIME, TEMP)
                                  VALUES (%s, %s)"""
    cursor.execute(insert_query, (dt, int(temp)))

    connection.commit()
    cursor.close()
    connection.close()


def getdb():
    connection = psycopg2.connect(user="postgres",
                                  password=password,
                                  host="192.168.66.179",
                                  port="5432")
    cursor = connection.cursor()

    # Проверка существования таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            DATETIME timestamp PRIMARY KEY, 
            TEMP smallint
        )
    """)

    cursor.execute("SELECT * FROM temperature")
    ex = cursor.fetchall()
    cursor.close()
    connection.close()
    result = []
    for i in ex:
        result.append(str(i[0]) + ' ' + str(i[1]))
    return result


@app.get("/")
def root():
    html_content = "<h2>Hello</h2>"
    return HTMLResponse(content=html_content)


@app.get("/weathernow")
def weather():
    weather_data = requests.get(url).json()
    temperature = round(weather_data['main']['temp'])
    insertindb(temperature)
    html_content = "<h2>Температура в " + city + ": " + str(temperature) + "</h2>"
    return HTMLResponse(content=html_content)


@app.get("/weatherindb")
def read_db():
    result = getdb()
    html_content = ('\n').join(result)
    return PlainTextResponse(content=html_content)
