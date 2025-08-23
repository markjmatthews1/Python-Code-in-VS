import datetime
import pytz

eastern = pytz.timezone('US/Eastern')
current_time = datetime.datetime.now(eastern).time()
market_open = datetime.time(4, 0)
market_close = datetime.time(20, 0)
is_market_hours = market_open <= current_time <= market_close

print(f'Current ET time: {current_time}')
print(f'Market hours (4:00-20:00): {is_market_hours}')
print('Market is', 'OPEN' if is_market_hours else 'CLOSED')
