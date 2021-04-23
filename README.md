# top-volume-email-bot

Top volume email bot gets  24h volumes of top 100 coins and tokens.
It is comparing new data with previous data that was gotten 6 hours ago and compared data is sent to desired email. Furthermore, email contains a text file which has a table about volume information and row numbers of coins or tokens.

CoinMarketCap API is used.

I use Crontab for running the email.py every 6 hours.
