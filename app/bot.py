# curl -s "https://data.gateio.co/api2/1/candlestick2/rem_usdt?group_sec=60&range_hour=1" | python -m json.tool > rem_usdt_ohlc

import plotly.graph_objects as go
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.write_html('first_figure.html', auto_open=True)
