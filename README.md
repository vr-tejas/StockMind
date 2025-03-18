# StockMind 📈  

**StockMind** is a **Stock peer competitor and Stock Analysis** tool that identifies **peer competitors** for a company and fetches its **live stock prices**.  

## 🚀 Features  
✅ **Competitor Analysis** – Uses **Gemini LLM** to find peer competitors based on the company's industry.  
✅ **Real-Time Stock Prices** – Fetches **live stock data** using the **yfinance** library.  
✅ **Automated Ticker Retrieval** – Extracts the stock ticker symbol from **Alpha Vantage API**.  
✅ **Company Information Fetching** – Uses **Wikipedia API** to gather company details.  
✅ **US Market Focused** – Currently designed for **United States** stock exchanges.  

## 🔧 Tech Stack  
- **Python** 🐍  
- **Wikipedia API** – Fetches company descriptions  
- **Gemini LLM** – Identifies peer competitors  
- **Alpha Vantage API** – Retrieves stock ticker symbols  
- **yfinance** – Fetches real-time stock prices  

## 📜 Installation  

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/sharathchandra-patil/StockMind.git
cd StockMind
```  

2️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt
```  

3️⃣ **Set up API keys**  
- Get an **Alpha Vantage API Key** from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).  
- Store it in an **.env file** or set it in your environment variables:  
```bash
ALPHA_VANTAGE_API_KEY=your_api_key
```  

## 🚀 Usage  

Run the script and input a company name:  
```bash
python stockmind.py
```  

Example Output:  
```
Company: Apple Inc. (AAPL)  
Industry: Technology  
Peer Competitors: Microsoft, Google, Amazon  
Current Stock Price: $180.32  
```   

## 🤝 Contributing  
Contributions are welcome! Feel free to fork the repo and submit a pull request.  

## 📜 License  
This project is licensed under the **MIT License**.  
