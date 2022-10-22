from prometheus_client import start_http_server, Gauge, Counter
from requests import get
import time
import json

def GetWeatherData(lat, lon):
    apiKey = #Insert your OpenWeatherMap api key here
    weather = get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apiKey}")
    return(json.loads(weather.text))

def GetHistoricalWeatherText(dateTime,lat,lon):
    apiKey = "0dfc8595ac7cb4ad99ca3b2c0154d0b4"
    histData = get(f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={dateTime}&appid={apiKey}")
    return(json.loads(histData.text)["current"]["weather"][0]["main"])

def GetTemperature(weatherData):
    return(weatherData["main"]["temp"]-272.15)

def GetWeatherText(weatherData):
    return(weatherData["weather"][0]["main"])

def GetWindSpeed(WeatherData):
    return(weatherData["wind"]["speed"])

def GetHumidity(weatherData):
    return(weatherData["main"]["humidity"])

cityCoordinates = {"Istanbul" : {"lat" : "41.0138", "lon" : "28.9497"} , "London" : {"lat" : "51.5085", "lon" : "-0.1257"}, "Beijing" : {"lat": "39.9075", "lon": "116.3972"}}

todayTime = int(time.time()) - (int(time.time())%86400) + (3600*10)

humidity = Gauge('current_humidity','Current humidity percentage',['city'])

wind = Gauge('current_wind_speed_kmh','Current wind speed in km/h',['city'])

temper = Gauge('current_temperature_celsius', 'Current Temperature Value',['city'])

eventsList = ['Clouds','Thunderstorm','Drizzle','Rain', 'Snow', 'Mist','Smoke','Haze','Dust','Fog','Sand','Ash','Squall','Tornado','Clear']

eventCounter = Counter('weather_events','Weather events counter',['event','city'])

for j in(cityCoordinates.keys()):
    for i in(eventsList):
        eventCounter.labels(i,j)

if(todayTime<=int(time.time())):
    countDownForEventSeconds = todayTime+86400-int(time.time())
    for j in(cityCoordinates.keys()):
        for i in range(todayTime-(86400*4),todayTime+1,86400):
            eventCounter.labels(GetHistoricalWeatherText(i,cityCoordinates[j]["lat"],cityCoordinates[j]["lon"]),j).inc()
else:
    countDownForEventSeconds = todayTime - int(time.time())

    for j in(cityCoordinates.keys()):
        for i in range(todayTime-(86400*4),todayTime-86400+1,86400):
            eventCounter.labels(GetHistoricalWeatherText(i,cityCoordinates[j]["lat"],cityCoordinates[j]["lon"]),j).inc()
start_http_server(8042)

countDownForEventLoop = int((countDownForEventSeconds//60)/15)

while(True):
    for i in(cityCoordinates.keys()):
        weatherData = GetWeatherData(cityCoordinates[i]["lat"], cityCoordinates[i]["lon"])
        temper.labels(i).set(round(GetTemperature(weatherData),2))
        wind.labels(i).set(GetWindSpeed(weatherData))
        humidity.labels(i).set(GetHumidity(weatherData))
    if(countDownForEventLoop == 0):
        eventCounter.labels(GetWeatherText(weatherData)).inc()
        countDownForEventLoop == 86400/60/15
    else:
        countDownForEventLoop -=1
    time.sleep(60*15)
