def go_to_menu(b):
    CLS()
    display(HTML(button_style))
    display(HTML("<h1>Etrade Update Menu</h1>"))  # Redraw menu title - line 359
    display(grid)  # Redraw menu grid - line 362

def Stock_ETF_Quote():
    global update_triggered, widgets, display, time, account_dropdown, access_token, consumer_key, consumer_secret, HTML, button_style, POLYGON_API_KEY, pyetrade, clear_output

    CLS()
    display(HTML(button_style))

    symbol_input = widgets.Text(
        description="Enter Symbol:",
        placeholder="e.g., AAPL",
        layout=widgets.Layout(width='200px')
    )
    display(symbol_input)  # Display the symbol input box initially


    def get_quote_data(b):
        global access_token, consumer_key, consumer_secret, HTML, POLYGON_API_KEY, pyetrade  # Include pyetrade here as well
        symbol = symbol_input.value.upper()  # Update symbol_input.value to upper case
        try:
            if access_token is None:  # or check for expiration if needed
                access_token, consumer_key, consumer_secret = authorize_etrade()  # Re-authenticate

            market = pyetrade.ETradeMarket(
                consumer_key,
                consumer_secret,
                access_token['oauth_token'],
                access_token['oauth_token_secret'],
                dev=False
            )
            try:
                quote_response = market.get_quote([symbol], resp_format='json')
                time.sleep(1)  # Wait for 1 second before the next request
            except Exception as e:
                logging.error(f"Error retrieving quote for {symbol}: {e}")
                print(f"An error occurred: {e}. Please try again later.")
                return  # Exit if there's an error

            import yfinance as yf  # Import yfinance

            # Get data using yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info  # Get ticker information
            recommendations = ticker.recommendations  # Get analyst recommendations

            # Access new data points from ticker.info
            recommendation_mean = info.get("recommendationMean", "N/A")
            number_of_analyst_opinions = info.get("numberOfAnalystOpinions", "N/A")
            recommendation_key = info.get("recommendationKey", "N/A")
            most_recent_quarter = info.get("earningsTimestamp", "N/A")

            import pandas as pd  # Import pandas before using pd.to_datetime
            if info.get('earningsTimestamp') is not None:
                try:
                    most_recent_quarter_dt = pd.to_datetime(info.get('earningsTimestamp'), unit='s', errors='coerce')
                    most_recent_quarter = most_recent_quarter_dt.strftime('%m/%d/%Y')
                except (ValueError, TypeError) as e:
                    print(f"Error converting earningsTimestamp to datetime: {e}")
                    most_recent_quarter = "N/A"
            else:
                most_recent_quarter = "N/A"

            trailing_eps = info.get("trailingEps", "N/A")  # Add trailingEps
            forward_eps = info.get("forwardEps", "N/A")  # Add forwardEps
            volume = info.get("volume", "N/A")  # Add volume
            average_volume_10days = info.get("averageVolume10days", "N/A")  # Add averageVolume10days

            # Access analyst ratings from recommendations DataFrame
            if recommendations is not None and not recommendations.empty:
                average_rating = recommendations.get('To Grade', recommendations.get('Action', 'N/A'))
                if not isinstance(average_rating, str):
                    average_rating = average_rating.iloc[-1]  # Get last value if it's a Series

            # For displaying recent news (modified)
            news_html = ""
            news = ticker.news
            #print(f"Raw news data: {news}")  # Print for inspection
            #time.sleep(10)
            if news:
                for article in news:
                    #print(article)
                    if article and 'content' in article and 'title' in article['content']:  # Check if 'content' and 'title' exist
                        title = article['content']['title']
                        publisher = article['content'].get('provider', {}).get('displayName', 'N/A')  # Access publisher from 'provider'
                        summary = article['content'].get('summary', 'N/A')
                        published_date = article['content'].get('pubDate', 'N/A')  # Access published date from 'pubDate'
                        link = article['content'].get('canonicalUrl', {}).get('url', '#')  # Access link from 'canonicalUrl'
                        #print(title)
                        #print(summary)
                        #time.sleep(10)
                        news_html += f"""
                            <p><b><a href="{link}" target="_blank">{title}</a></b></p>
                            <p>Publisher: {publisher}</p>
                            <p>Summary: {summary}</p>
                            <p>Published: {published_date}</p>
                            <br>
                        """
                if not news_html:
                    news_html = "<p>No recent news available for this symbol.</p>"
            else:
                news_html = "<p>News not available for this symbol.</p>"  # If no news data at all

            # Incorporate data into formatted_quote
            formatted_quote = f"""
                <div style="background-color: lightblue; padding: 10px; color: black; margin: 0 auto; width: fit-content;">
                    <div style="display: inline-block; vertical-align: top;">
                        <p>Symbol: {symbol}</p>
                        <p>Previous Close: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('previousClose', 'N/A')}</p>
                        <p>Last Trade: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('lastTrade', 'N/A')}</p>
                        <p>Change: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('changeClose', 'N/A')}</p>
                        <p>Change Percent: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('changeClosePercentage', 'N/A')}%</p>
                        <p>52 Week Low: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('low52', 'N/A'):.2f}</p>
                        <p>52 Week Low Date: {datetime.datetime.fromtimestamp(int(quote_response['QuoteResponse']['QuoteData'][0]['All'].get('week52LowDate', 0))).strftime('%m-%d-%Y') if quote_response['QuoteResponse']['QuoteData'][0]['All'].get('week52LowDate') else 'N/A'}</p>
                        <p>52 Week Hi: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('high52', 'N/A'):.2f}</p>
                        <p>52 Week HI Date: {datetime.datetime.fromtimestamp(int(quote_response['QuoteResponse']['QuoteData'][0]['All'].get('week52HiDate', 0))).strftime('%m-%d-%Y') if quote_response['QuoteResponse']['QuoteData'][0]['All'].get('week52HiDate') else 'N/A'}</p>
                        <p>Yield: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('yield', 'N/A'):.2f}%</p>
                        <p>Declared Dividend: {quote_response['QuoteResponse']['QuoteData'][0]['All'].get('declaredDividend', 'N/A') / 100:.2f}</p>
                    </div>
                    <div style="display: inline-block; vertical-align: top; margin-left: 20px;">
                        <p>Average Rating from 1 to 5: {recommendation_mean}</p>
                        <p>Number of Analyst Opinions: {number_of_analyst_opinions}</p>
                        <p>Recommendation Key: {recommendation_key}</p>
                        <p>Current Quarter: {most_recent_quarter}</p>
                        <p>Current EPS: {trailing_eps}</p>
                        <p>Expected EPS: {forward_eps}</p>
                        <p>Volume: {volume}</p>
                        <p>10 Day Average Volume: {average_volume_10days}</p>
                    </div>
                    <div style="display: inline-block; vertical-align: top; margin-left: 20px;">
                        <h2>Recent News</h2>
                        {news_html}
                    </div>
                </div>
            """

            display(HTML(formatted_quote))

        except Exception as e:
            print(f"An error occurred in Stock_ETF_Quote: {e}")


     # *** Create and display get_quote_button and menu_button outside get_quote_data ***
    display(HTML(button_style))  # Call display for button_style once before get_quote_button
    get_quote_button = widgets.Button(description="Get Quote")
    get_quote_button.add_class("get_quote_button")
    get_quote_button.style.button_color = 'lightcoral'
    get_quote_button.on_click(get_quote_data)  # Now get_quote_data is defined and accessible

    menu_button = widgets.Button(description="Menu", layout=widgets.Layout(width='auto', margin='10px'))
    menu_button.style.button_color = 'lightcoral'  # keep button colors the same
    menu_button.on_click(go_to_menu)  # Attach the go_to_menu function

    # Create a container for buttons and style its positioning
    button_container = widgets.HBox([get_quote_button, menu_button])
    button_container.layout.margin = '0px'  # Remove default margin
    button_container.layout.justify_content = 'flex-start'  # Align to the left
    display(button_container)  # Display the buttons initially



# **** End of Stock ETF Quote section ****