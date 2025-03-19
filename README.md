# StockMind 📈  

**StockMind** is a web-based **Stock Competitor Analysis and Market Comparison** tool that helps investors identify peer competitors for companies and analyze their stock performance in comparison.

## 🚀 Features  
✅ **Competitor Analysis** – Uses **Gemini LLM** to find peer competitors based on the company's sector and industry.  
✅ **Real-Time Stock Data** – Fetches **historical stock price data** using the **yfinance** library.  
✅ **Automated Ticker Retrieval** – Extracts the stock ticker symbol from **Alpha Vantage API**.  
✅ **Company Information** – Uses **Wikipedia API** to gather company descriptions.  
✅ **Market Cap Comparison** – Compares market capitalization of top competitors.
✅ **Interactive Charts** – Visualizes stock price trends for better comparison.
✅ **US Market Focused** – Currently designed for **United States** stock exchanges.  

## 🔧 Tech Stack  
- **Backend**: Python with Flask 🐍  
- **Frontend**: HTML, CSS, JavaScript with interactive charts
- **APIs**:
  - **Wikipedia API** – Fetches company descriptions  
  - **Gemini 1.5 Flash LLM** – Identifies peer competitors by sector  
  - **Alpha Vantage API** – Retrieves stock ticker symbols  
  - **yfinance** – Fetches historical stock price data and market cap information

## 📜 Installation  

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/yourusername/StockMind.git
cd StockMind
```  

2️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt
```  

3️⃣ **API Keys**  
The application uses the following API keys that are already included in the code:
- Alpha Vantage API Key
- Gemini API Key

You may want to replace them with your own keys for production use by updating the variables in BACK.py or moving them to environment variables.

## 🚀 Usage  

1. Run the Flask application:
```bash
python BACK.py
```  

2. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

3. Enter a company name in the search box and click "Analyze" to see:
   - Company description
   - Stock price history
   - Competitive sectors
   - Top competitors with their market capitalization and stock performance

## 📊 How It Works

1. The application takes a company name as input
2. Retrieves the company description from Wikipedia
3. Uses Gemini LLM to identify sectors and competitors
4. Fetches stock ticker symbols from Alpha Vantage
5. Gets historical stock data and market cap using yfinance
6. Presents the analysis in an interactive web interface

## 🤝 Contributing  
Contributions are welcome! Feel free to fork the repo and submit a pull request.  

## 📜 License  
This project is licensed under the **MIT License**.  
