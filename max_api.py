import requests
import pandas as pd
import time
from datetime import datetime
import logging
from config import MAX_API_BASE_URL

class MaxAPI:
    def __init__(self):
        self.base_url = MAX_API_BASE_URL
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def get_ticker(self, market='btctwd'):
        """獲取即時價格資訊"""
        try:
            url = f"{self.base_url}/tickers/{market}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'symbol': market.upper(),
                'price': float(data['last']),
                'volume': float(data['vol']),
                'high': float(data['high']),
                'low': float(data['low']),
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"獲取價格失敗: {e}")
            return None
    
    def get_klines(self, market='btctwd', period=1, limit=200):
        """獲取K線資料"""
        try:
            url = f"{self.base_url}/k"
            params = {
                'market': market,
                'period': period,  # 1分鐘K線
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 轉換為DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
            
            # 轉換資料類型
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
            
        except Exception as e:
            self.logger.error(f"獲取K線資料失敗: {e}")
            return None
    
    def get_market_status(self):
        """獲取市場狀態"""
        try:
            url = f"{self.base_url}/markets"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            markets = response.json()
            
            btc_market = next((m for m in markets if m['id'] == 'btctwd'), None)
            return btc_market is not None
            
        except Exception as e:
            self.logger.error(f"獲取市場狀態失敗: {e}")
            return False 