import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import logging
import json
from config import MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD

class EnhancedMACDAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fast_period = MACD_FAST_PERIOD
        self.slow_period = MACD_SLOW_PERIOD
        self.signal_period = MACD_SIGNAL_PERIOD
        self.signal_history = []
        self.hourly_records = []
        
    def calculate_macd(self, df):
        """計算MACD指標 - 使用標準算法"""
        try:
            if df is None or len(df) < self.slow_period + self.signal_period:
                self.logger.warning("資料不足，無法計算MACD")
                return None
            
            df = df.copy()
            
            # 使用標準MACD計算方法
            # 計算EMA
            df['ema_12'] = ta.trend.EMAIndicator(close=df['close'], window=self.fast_period).ema_indicator()
            df['ema_26'] = ta.trend.EMAIndicator(close=df['close'], window=self.slow_period).ema_indicator()
            
            # MACD = EMA12 - EMA26
            df['macd'] = df['ema_12'] - df['ema_26']
            
            # Signal Line = EMA9 of MACD
            df['macd_signal'] = ta.trend.EMAIndicator(close=df['macd'], window=self.signal_period).ema_indicator()
            
            # Histogram = MACD - Signal
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # 清理NaN值
            df = df.dropna()
            
            return df
            
        except Exception as e:
            self.logger.error(f"計算MACD失敗: {e}")
            return None
    
    def is_bottom_rebound(self, df, lookback=5):
        """判斷是否為底部反彈"""
        try:
            if len(df) < lookback + 2:
                return False
            
            recent_data = df.tail(lookback + 2)
            macd_values = recent_data['macd'].values
            histogram_values = recent_data['macd_histogram'].values
            
            # 檢查MACD是否從低點回升
            min_idx = np.argmin(macd_values[:-1])  # 排除最新值
            if min_idx < len(macd_values) - 3:  # 低點不能太舊
                return False
            
            # 檢查直方圖是否轉正
            recent_histogram = histogram_values[-3:]
            if len(recent_histogram) >= 2:
                histogram_improving = recent_histogram[-1] > recent_histogram[-2]
                if histogram_improving and recent_histogram[-1] > 0:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"判斷底部反彈失敗: {e}")
            return False
    
    def is_top_breakdown(self, df, lookback=5):
        """判斷是否為高點下跌"""
        try:
            if len(df) < lookback + 2:
                return False
            
            recent_data = df.tail(lookback + 2)
            macd_values = recent_data['macd'].values
            histogram_values = recent_data['macd_histogram'].values
            
            # 檢查MACD是否從高點下跌
            max_idx = np.argmax(macd_values[:-1])
            if max_idx < len(macd_values) - 3:
                return False
            
            # 檢查直方圖是否轉負
            recent_histogram = histogram_values[-3:]
            if len(recent_histogram) >= 2:
                histogram_declining = recent_histogram[-1] < recent_histogram[-2]
                if histogram_declining and recent_histogram[-1] < 0:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"判斷高點下跌失敗: {e}")
            return False
    
    def analyze_enhanced_signal(self, df, current_price):
        """增強版信號分析"""
        try:
            if df is None or len(df) < 10:
                return {
                    'signal': 'HOLD',
                    'strength': 0,
                    'reason': '資料不足',
                    'macd_current': 0,
                    'macd_signal_current': 0,
                    'histogram_current': 0,
                    'confidence': 0,
                    'trigger_data': []
                }
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            macd_current = latest['macd'] if not pd.isna(latest['macd']) else 0
            macd_signal_current = latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0
            histogram_current = latest['macd_histogram'] if not pd.isna(latest['macd_histogram']) else 0
            
            signal = 'HOLD'
            strength = 0
            confidence = 0
            reasons = []
            
            # 主要信號邏輯 - 按照您的需求
            if macd_current > macd_signal_current and self.is_bottom_rebound(df):
                signal = 'BUY'
                strength += 70
                confidence = 85
                reasons.append('MACD黃金交叉且確認底部反彈')
            elif macd_current < macd_signal_current and self.is_top_breakdown(df):
                signal = 'SELL'
                strength += 70
                confidence = 85
                reasons.append('MACD死亡交叉且確認高點下跌')
            
            # 輔助判斷
            if signal != 'HOLD':
                # 直方圖強化信號
                if signal == 'BUY' and histogram_current > 0:
                    strength += 15
                    confidence += 5
                    reasons.append('直方圖轉正支持買入')
                elif signal == 'SELL' and histogram_current < 0:
                    strength += 15
                    confidence += 5
                    reasons.append('直方圖轉負支持賣出')
                
                # 趨勢確認
                ema_trend = latest['ema_12'] - latest['ema_26']
                if signal == 'BUY' and ema_trend > 0:
                    strength += 10
                    reasons.append('短期趨勢向上')
                elif signal == 'SELL' and ema_trend < 0:
                    strength += 10
                    reasons.append('短期趨勢向下')
            
            # 記錄觸發條件的5筆資料
            trigger_data = []
            if signal in ['BUY', 'SELL'] and strength >= 70:
                trigger_data = self.get_trigger_data(df, 5)
            
            return {
                'signal': signal,
                'strength': min(100, strength),
                'reason': '; '.join(reasons) if reasons else '無明確信號',
                'macd_current': macd_current,
                'macd_signal_current': macd_signal_current,
                'histogram_current': histogram_current,
                'confidence': min(100, confidence),
                'trigger_data': trigger_data,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"增強信號分析失敗: {e}")
            return {
                'signal': 'HOLD',
                'strength': 0,
                'reason': f'分析錯誤: {str(e)}',
                'macd_current': 0,
                'macd_signal_current': 0,
                'histogram_current': 0,
                'confidence': 0,
                'trigger_data': []
            }
    
    def get_trigger_data(self, df, count=5):
        """獲取觸發條件的資料"""
        try:
            recent_data = df.tail(count)
            trigger_records = []
            
            for _, row in recent_data.iterrows():
                trigger_records.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'close': row['close'],
                    'macd': row['macd'] if not pd.isna(row['macd']) else 0,
                    'signal': row['macd_signal'] if not pd.isna(row['macd_signal']) else 0,
                    'histogram': row['macd_histogram'] if not pd.isna(row['macd_histogram']) else 0
                })
            
            return trigger_records
            
        except Exception as e:
            self.logger.error(f"獲取觸發資料失敗: {e}")
            return []
    
    def record_hourly_data(self, df, count=10):
        """整點記錄MACD資料"""
        try:
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            
            # 檢查是否已經記錄過這個小時
            for record in self.hourly_records:
                if record['hour'] == current_hour:
                    return False  # 已經記錄過
            
            # 記錄最新的count筆資料
            recent_data = df.tail(count)
            hourly_record = {
                'hour': current_hour,
                'data': self.get_trigger_data(recent_data, count),
                'summary': {
                    'avg_macd': recent_data['macd'].mean(),
                    'avg_signal': recent_data['macd_signal'].mean(),
                    'avg_histogram': recent_data['macd_histogram'].mean()
                }
            }
            
            self.hourly_records.append(hourly_record)
            
            # 保持最近24小時的記錄
            if len(self.hourly_records) > 24:
                self.hourly_records = self.hourly_records[-24:]
            
            # 保存到文件
            self.save_hourly_records()
            
            self.logger.info(f"已記錄 {current_hour} 的MACD資料")
            return True
            
        except Exception as e:
            self.logger.error(f"整點記錄失敗: {e}")
            return False
    
    def save_hourly_records(self):
        """保存整點記錄到文件"""
        try:
            filename = f"macd_hourly_records_{datetime.now().strftime('%Y%m%d')}.json"
            
            # 轉換datetime為字符串以便JSON序列化
            records_to_save = []
            for record in self.hourly_records:
                record_copy = record.copy()
                record_copy['hour'] = record['hour'].strftime('%Y-%m-%d %H:%M:%S')
                records_to_save.append(record_copy)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(records_to_save, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存整點記錄失敗: {e}")
    
    def get_macd_summary(self, df):
        """獲取MACD摘要資訊"""
        if df is None or len(df) == 0:
            return None
            
        latest = df.iloc[-1]
        return {
            'macd': latest['macd'] if not pd.isna(latest['macd']) else 0,
            'signal': latest['macd_signal'] if not pd.isna(latest['macd_signal']) else 0,
            'histogram': latest['macd_histogram'] if not pd.isna(latest['macd_histogram']) else 0,
            'ema_12': latest['ema_12'] if not pd.isna(latest['ema_12']) else 0,
            'ema_26': latest['ema_26'] if not pd.isna(latest['ema_26']) else 0,
            'timestamp': latest['timestamp']
        } 