from flask import Flask, request, jsonify, render_template 
import requests 
import yfinance as yf 
import wikipedia 
from google import genai 
from dotenv import load_dotenv 
import os 

# Load API keys 
GEMINI_API_KEY="AIzaSyDCGf6T3GlijotnC4gv9s36ZNHkBBKTBrQ" 
ALPHA_VANTAGE_API_KEY="JTPZF6JUQYTU18C3" 
client = genai.Client(api_key=GEMINI_API_KEY) 
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
    try: 
        stock = yf.Ticker(ticker) 
        history = stock.history(period="3mo") 
        time_labels = history.index.strftime('%Y-%m-%d').tolist() 
        stock_prices = [round(price, 2) for price in history['Close'].tolist()]  # Round prices to 2 decimal places
        return stock_prices, time_labels 
    except Exception as e: 
        return None, None

 
def get_ticker_from_alpha_vantage(company_name): 
    try: 
        url = "https://www.alphavantage.co/query" 
        params = { 
            "function": "SYMBOL_SEARCH", 
            "keywords": company_name, 
            "apikey": ALPHA_VANTAGE_API_KEY, 
        } 
        response = requests.get(url, params=params) 
        data = response.json() 
        if "bestMatches" in data: 
            for match in data["bestMatches"]: 
                if match["4. region"] == "United States": 
                    return match["1. symbol"] 
        return None 
    except Exception as e: 
        return None 
 
def fetch_market_cap(ticker): 
    try: 
        stock = yf.Ticker(ticker) 
        market_cap = stock.info.get('marketCap', None) 
        return market_cap 
    except Exception as e: 
        return None 
 
def get_stock_price_for_competitor(ticker): 
    try: 
        stock = yf.Ticker(ticker) 
        history = stock.history(period="3mo") 
        time_labels = history.index.strftime('%Y-%m-%d').tolist() 
        stock_prices = history['Close'].tolist() 
        return stock_prices, time_labels 
    except Exception as e: 
        return None, None 
 
def get_top_competitors(competitors): 
    competitor_data = [] 
    processed_tickers = set()  # To track processed tickers and avoid duplicates 
 
    for competitor in set(competitors):  # Remove duplicate names 
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
        response = client.models.generate_content( 
            model="gemini-1.5-flash", contents=prompt 
        ) 
        content = response.candidates[0].content.parts[0].text 
        sectors = [] 
        for line in content.split("\n\n"): 
            lines = line.strip().split("\n") 
            if len(lines) > 1: 
                sector_name = lines[0].strip() 
                competitors = [l.strip() for l in lines[1:]] 
                sectors.append({"name": sector_name, "competitors": competitors}) 
        return sectors 
    except Exception as e: 
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
    if not summary: 
        return jsonify(success=False, error="Could not find company description.") 
 
    ticker = get_ticker_from_alpha_vantage(company_name) 
    if not ticker: 
        return jsonify(success=False, error="Could not find ticker symbol.") 
 
    stock_prices, time_labels = fetch_stock_price(ticker) 
    if not stock_prices or not time_labels: 
        return jsonify(success=False, error="Could not fetch stock prices.") 
 
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