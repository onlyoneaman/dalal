"""URLs, headers, and configuration constants."""

# --- NSE ---
NSE_BASE = "https://www.nseindia.com"
NSE_API = f"{NSE_BASE}/api"
NSE_COOKIE_URL = f"{NSE_BASE}/option-chain"
NSE_RATE_LIMIT = 3  # requests per second
NSE_TIMEOUT = 15  # seconds

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) "
        "Gecko/20100101 Firefox/118.0"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=HDFCBANK",
    "Connection": "keep-alive",
}

# --- BSE ---
BSE_API = "https://api.bseindia.com/BseIndiaAPI/api"
BSE_RATE_LIMIT = 8  # requests per second
BSE_TIMEOUT = 10  # seconds

BSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.bseindia.com",
    "Referer": "https://www.bseindia.com/",
    "Connection": "keep-alive",
}
