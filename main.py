from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
import requests
import httpx
import asyncio
from dotenv import main
import os
import datetime
import psycopg2

app = FastAPI()
city = 'Тамбов'

url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
main.load_dotenv()

PASSWORD = os.getenv('POSTGRES_PASSWORD')
async def get_tempature():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


def insertindb(temp):
    connection = psycopg2.connect(user="postgres",
                                  password=PASSWORD,
                                  host="postgres",
                                  port="5432")
    cursor = connection.cursor()
    dt = datetime.datetime.now()

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
                                  password=PASSWORD,
                                  host="postgres",
                                  port="5432")
    cursor = connection.cursor()

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
async def weather():
    weather_data = await get_tempature()
    temperature = round(weather_data['main']['temp'])
    insertindb(temperature)
    html_content = "<h2>Температура в " + city + ": " + str(temperature) + "</h2>"
    return HTMLResponse(content=html_content)


@app.get("/weatherindb")
def read_db():
    result = getdb()
    html_content = ('\n').join(result)
    return PlainTextResponse(content=html_content)
