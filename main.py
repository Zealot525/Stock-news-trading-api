import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os

STOCK = "NVDA"
COMPANY_NAME = "NVIDIA"
emoji = ""

#Your own api key and auth key
news_api = os.environ.get("news_api")
student_ALPHA_VANTAGE_API = os.environ.get("student_ALPHA_VANTAGE_API")
twilio_auth_key = os.environ.get("twilio_auth_key")
twilio_acct_sid = os.environ.get("twilio_acct_sid")


def get_percentage_difference(latest_closing_price,  previous_closing_price):
    percent_diff = (latest_closing_price - previous_closing_price) / latest_closing_price * 100
    return round(percent_diff,2)

# =======================================GETTING THE DATES==============================================#
latest_stock_date =  datetime.now().date()

todays_day = datetime.weekday(latest_stock_date)
if todays_day == 0:
    latest_stock_date -= timedelta(days=3)
elif todays_day == 6:
    latest_stock_date -= timedelta(days=2)
else:
    latest_stock_date -= timedelta(days=1)

day_before_latest_stock_date  = latest_stock_date - timedelta(days=1)
one_month_ago = latest_stock_date - timedelta(days=20)
one_month_ago = str(one_month_ago)


# # =======================================STOCKS API==============================================#
stock_api_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey":  student_ALPHA_VANTAGE_API
}
response = requests.get("https://www.alphavantage.co/query", params=stock_api_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
data_list = [value for (key,value) in data.items()]
latest_closing = float(data_list[0]["4. close"])
previous_closing = float(data_list[1]["4. close"])


# =======================================NEWS API==============================================#
news_params = {
    "q":COMPANY_NAME,
    "from_param":one_month_ago,
    "to":latest_stock_date,
    "language":'en',
    "sort_by":'relevancy',
    "apiKey": news_api
}
news_response = requests.get(url="https://newsapi.org/v2/everything",params=news_params)
news_response.raise_for_status()
articles = news_response.json()["articles"]

most_relevant_articles = articles[1:4]
# ===================================GETTING THE DIFFERENCE IN STOCK PRICES==========================================#
percent_diff = get_percentage_difference(latest_closing, previous_closing)
if percent_diff  >= 0:
    emoji ="🔺"
elif percent_diff  < 0 :
    emoji ="🔻"
    percent_diff *= -1

# =======================================TWILIO SMS==============================================#
if   percent_diff>= 5:
    client = Client(twilio_acct_sid, twilio_auth_key)
    message = client.messages.create(
        body=f"{STOCK}:{emoji}{percent_diff}%\nHeadline:    {most_relevant_articles[0]['title']}\n\nDescription:  {most_relevant_articles[0]['description']}\n\n\n\nHeadline:   {most_relevant_articles[1]['title']}\n\nDescription:    {most_relevant_articles[1]['description']}",
        from_="+12513698647",
        to="+8108064255612"
    )
    print(message.status)

else:
    print("small fluctuations in stock price")