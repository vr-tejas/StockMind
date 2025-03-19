from flask import Flask, request, jsonify, render_template 
import requests 
import yfinance as yf 
import wikipedia 
import google.generativeai as genai
from dotenv import load_dotenv 
import os 

# Load API keys 
GEMINI_API_KEY="AIzaSyDCGf6T3GlijotnC4gv9s36ZNHkBBKTBrQ" 
ALPHA_VANTAGE_API_KEY="JTPZF6JUQYTU18C3" 
genai.configure(api_key=GEMINI_API_KEY)
app = Flask(__name__, static_folder="static", template_folder="templates") 

def fetch_wikipedia_summary(company_name): 
    try: 
        search_results = wikipedia.search(company_name) 
        if search_results: 
            page_title = search_results[0] 
            summary = wikipedia.summary(page_title, sentences=2) 
            return page_title, summary 
    except Exception as e: 
        return None, f"Error fetching Wikipedia summary: {str(e)}" 
    return None, "No Wikipedia page found for the given company." 
 
def fetch_stock_price(ticker): 
    # Try Yahoo Finance first
    try: 
        print(f"Attempting to fetch stock price data from Yahoo Finance for ticker: {ticker}")
        
        # First try using period="1d" for a quick test to see if the ticker is valid
        stock = yf.Ticker(ticker)
        # Force info download to verify the ticker is valid
        try:
            info = stock.info
            if not info or len(info) == 0:
                print(f"No info found for ticker {ticker}, it may be invalid")
                raise Exception("No ticker info found")
        except Exception as info_e:
            print(f"Error getting info for ticker {ticker}: {str(info_e)}")
            raise
            
        # If we got here, the ticker is valid, now fetch history
        for period in ["3mo", "1mo", "1wk", "5d"]:
            try:
                print(f"Trying to fetch history with period={period} for {ticker}")
                history = stock.history(period=period)
                
                if history.empty or len(history) == 0:
                    print(f"Empty history returned for {ticker} with period={period}")
                    continue
                    
                time_labels = history.index.strftime('%Y-%m-%d').tolist()
                stock_prices = [round(price, 2) for price in history['Close'].tolist()]
                
                if not stock_prices or len(stock_prices) == 0:
                    print(f"No price data found in history for {ticker} with period={period}")
                    continue
                    
                print(f"Successfully fetched {len(stock_prices)} data points for {ticker} from Yahoo Finance")
                return stock_prices, time_labels
            except Exception as inner_e:
                print(f"Error fetching history for {ticker} with period={period}: {str(inner_e)}")
                
        print(f"Couldn't get history for {ticker} with any period")
        raise Exception(f"No valid history found for ticker {ticker}")
            
    except Exception as e: 
        print(f"Yahoo Finance lookup failed for {ticker}: {str(e)}")
        # Try Alpha Vantage as a fallback
        print(f"Trying Alpha Vantage as a fallback for {ticker}")
        return fetch_stock_price_from_alpha_vantage(ticker)

def fetch_stock_price_from_alpha_vantage(ticker):
    try:
        print(f"Attempting to fetch stock price from Alpha Vantage for: {ticker}")
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
            "apikey": ALPHA_VANTAGE_API_KEY,
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys())[-90:]  # Last ~3 months of data
            stock_prices = [float(time_series[date]["4. close"]) for date in dates]
            stock_prices = [round(price, 2) for price in stock_prices]
            
            print(f"Successfully fetched {len(stock_prices)} data points from Alpha Vantage for {ticker}")
            return stock_prices, dates
        else:
            if "Error Message" in data:
                print(f"Alpha Vantage API error for {ticker}: {data['Error Message']}")
            elif "Note" in data:
                print(f"Alpha Vantage API note for {ticker}: {data['Note']}")  # Often rate limit message
            else:
                print(f"Unknown Alpha Vantage response format for {ticker}: {data}")
            return None, None
    except Exception as e:
        print(f"Error fetching from Alpha Vantage for {ticker}: {str(e)}")
        return None, None

def get_ticker_from_alpha_vantage(company_name): 
    try: 
        # Common company name to ticker mappings for popular companies
        common_tickers = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "amazon": "AMZN", 
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "facebook": "META",
            "meta": "META",
            "tesla": "TSLA",
            "netflix": "NFLX",
            "nvidia": "NVDA",
            "walmart": "WMT",
            "disney": "DIS",
            "coca cola": "KO",
            "coca-cola": "KO",
            "pepsi": "PEP",
            "pepsico": "PEP",
            "johnson & johnson": "JNJ",
            "jp morgan": "JPM",
            "jpmorgan": "JPM",
        }
        
        # First check our common tickers dictionary
        normalized_name = company_name.lower().strip()
        for name, ticker in common_tickers.items():
            if name in normalized_name or normalized_name in name:
                print(f"Found ticker {ticker} for {company_name} in common tickers dictionary")
                return ticker
        
        # Then try Alpha Vantage API
        url = "https://www.alphavantage.co/query" 
        params = { 
            "function": "SYMBOL_SEARCH", 
            "keywords": company_name, 
            "apikey": ALPHA_VANTAGE_API_KEY, 
        } 
        response = requests.get(url, params=params) 
        data = response.json() 
        
        if "bestMatches" in data and len(data["bestMatches"]) > 0: 
            # First try to find US stocks
            for match in data["bestMatches"]: 
                if match["4. region"] == "United States": 
                    print(f"Found ticker {match['1. symbol']} for {company_name} in Alpha Vantage API (US)")
                    return match["1. symbol"] 
            
            # If no US stocks found, just return the first match
            print(f"Found ticker {data['bestMatches'][0]['1. symbol']} for {company_name} in Alpha Vantage API (non-US)")
            return data["bestMatches"][0]["1. symbol"]
        
        # If all else fails, try a direct yfinance lookup (sometimes works for major tickers)
        try:
            # Try a simple ticker based on company name (for well-known companies)
            possible_ticker = ''.join(word[0] for word in company_name.upper().split()[:4])
            if len(possible_ticker) >= 2:
                stock = yf.Ticker(possible_ticker)
                # Verify it's valid by trying to get info
                if stock.info and 'regularMarketPrice' in stock.info:
                    print(f"Found ticker {possible_ticker} for {company_name} using direct yfinance lookup")
                    return possible_ticker
        except Exception:
            pass
            
        print(f"Could not find ticker symbol for: {company_name}")
        return None 
    except Exception as e: 
        print(f"Error finding ticker for {company_name}: {str(e)}")
        return None 
 
def fetch_market_cap(ticker): 
    try: 
        stock = yf.Ticker(ticker) 
        market_cap = stock.info.get('marketCap', None) 
        return market_cap 
    except Exception as e: 
        return None 
 
def get_stock_price_for_competitor(ticker): 
    # Try Yahoo Finance first
    try: 
        print(f"Attempting to fetch competitor stock price data from Yahoo Finance for ticker: {ticker}")
        
        # First try using period="1d" for a quick test to see if the ticker is valid
        stock = yf.Ticker(ticker)
        # Force info download to verify the ticker is valid
        try:
            info = stock.info
            if not info or len(info) == 0:
                print(f"No info found for competitor ticker {ticker}, it may be invalid")
                raise Exception("No ticker info found")
        except Exception as info_e:
            print(f"Error getting info for competitor ticker {ticker}: {str(info_e)}")
            raise
            
        # If we got here, the ticker is valid, now fetch history
        for period in ["3mo", "1mo", "1wk", "5d"]:
            try:
                print(f"Trying to fetch competitor history with period={period} for {ticker}")
                history = stock.history(period=period)
                
                if history.empty or len(history) == 0:
                    print(f"Empty history returned for competitor {ticker} with period={period}")
                    continue
                    
                time_labels = history.index.strftime('%Y-%m-%d').tolist()
                stock_prices = [round(price, 2) for price in history['Close'].tolist()]
                
                if not stock_prices or len(stock_prices) == 0:
                    print(f"No price data found in history for competitor {ticker} with period={period}")
                    continue
                    
                print(f"Successfully fetched {len(stock_prices)} data points for competitor {ticker} from Yahoo Finance")
                return stock_prices, time_labels
            except Exception as inner_e:
                print(f"Error fetching history for competitor {ticker} with period={period}: {str(inner_e)}")
                
        print(f"Couldn't get history for competitor {ticker} with any period")
        raise Exception(f"No valid history found for competitor ticker {ticker}")
            
    except Exception as e: 
        print(f"Yahoo Finance lookup failed for competitor {ticker}: {str(e)}")
        # Try Alpha Vantage as a fallback
        print(f"Trying Alpha Vantage as a fallback for competitor {ticker}")
        return get_stock_price_for_competitor_alpha_vantage(ticker)

def get_stock_price_for_competitor_alpha_vantage(ticker):
    return fetch_stock_price_from_alpha_vantage(ticker)

def get_top_competitors(competitors): 
    competitor_data = [] 
    processed_tickers = set()  # To track processed tickers and avoid duplicates 
 
    for competitor in set(competitors): 
        ticker = get_ticker_from_alpha_vantage(competitor) 
        if ticker and ticker not in processed_tickers: 
            market_cap = fetch_market_cap(ticker) 
            stock_prices, time_labels = get_stock_price_for_competitor(ticker) 
            if market_cap and stock_prices and time_labels: 
                competitor_data.append({ 
                    "name": competitor, 
                    "ticker": ticker, 
                    "market_cap": market_cap, 
                    "stock_prices": stock_prices, 
                    "time_labels": time_labels, 
                    "stock_price": stock_prices[-1], 
                }) 
                processed_tickers.add(ticker)  # Add ticker to the processed set 
 
    # Sort competitors by market cap and return the top 3 
    top_competitors = sorted(competitor_data, key=lambda x: x["market_cap"], reverse=True)[:3] 
    return top_competitors 
 
def query_gemini_llm(description): 
    try: 
        prompt = f""" 
        Provide a structured list of sectors and their competitors for the following company description: 
        {description[:500]} 
        Format: 
        Sector Name : 
            Competitor 1 
            Competitor 2 
            Competitor 3 
 
        Leave a line after each sector. Do not use bullet points. 
        """ 
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        content = response.text
        sectors = [] 
        for line in content.split("\n\n"): 
            lines = line.strip().split("\n") 
            if len(lines) > 1: 
                sector_name = lines[0].strip() 
                competitors = [l.strip() for l in lines[1:]] 
                sectors.append({"name": sector_name, "competitors": competitors}) 
        return sectors 
    except Exception as e: 
        print(f"Error in query_gemini_llm: {str(e)}")
        return None 
 
@app.route("/") 
def home(): 
    return render_template("FRONT.html") 
 
@app.route("/analyze_company", methods=["GET"]) 
def analyze_company(): 
    company_name = request.args.get("company_name") 
    if not company_name: 
        return jsonify(success=False, error="No company name provided.") 
 
    _, summary = fetch_wikipedia_summary(company_name) 
    if not summary or "Error fetching Wikipedia summary" in summary: 
        return jsonify(
            success=False, 
            error=f"Could not find company description for '{company_name}'. Please try a more specific company name.",
            company_name=company_name
        ) 
 
    ticker = get_ticker_from_alpha_vantage(company_name) 
    if not ticker: 
        # If we have a summary but no ticker, we can still try to get competitors
        competitors = query_gemini_llm(summary)
        if competitors:
            return jsonify(
                success=False, 
                error=f"Could not find ticker symbol for '{company_name}'. Try a different company name or one of these competitors.",
                company_name=company_name,
                description=summary,
                competitors=competitors,
            )
        else:
            return jsonify(
                success=False, 
                error=f"Could not find ticker symbol for '{company_name}'. Try using the full company name (e.g., 'Apple Inc.' instead of 'Apple').",
                company_name=company_name,
                description=summary
            )
 
    stock_prices, time_labels = fetch_stock_price(ticker) 
    if not stock_prices or not time_labels: 
        return jsonify(
            success=False, 
            error=f"Found ticker symbol '{ticker}' for '{company_name}', but could not fetch stock prices. The company may be delisted or data may be temporarily unavailable.",
            company_name=company_name,
            ticker=ticker,
            description=summary
        ) 
 
    competitors = query_gemini_llm(summary) 
    if not competitors: 
        competitors = [{"name": "No Sectors", "competitors": ["No competitors found."]}] 
 
    all_competitors = [comp for sector in competitors for comp in sector["competitors"]] 
    top_competitors = get_top_competitors(all_competitors) 
 
    return jsonify( 
        success=True, 
        description=summary, 
        ticker=ticker, 
        stock_prices=stock_prices, 
        time_labels=time_labels, 
        competitors=competitors, 
        top_competitors=top_competitors, 
    ) 
 
if __name__ == "__main__": 
    app.run(debug=True)