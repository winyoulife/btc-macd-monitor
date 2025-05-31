#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高級加密貨幣技術分析器
整合多重專業技術指標，提供世界級AI交易判斷
專為比特幣等虛擬貨幣交易設計
"""

import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedCryptoAnalyzer:
    """高級加密貨幣技術分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger('AdvancedCryptoAnalyzer')
        
        # 技術指標參數配置
        self.config = {
            # 移動平均線
            'ma_short': 7,      # 短期MA
            'ma_medium': 25,    # 中期MA  
            'ma_long': 99,      # 長期MA
            
            # MACD參數
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # RSI參數
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            
            # 布林帶參數
            'bb_period': 20,
            'bb_std': 2,
            
            # 隨機指標
            'stoch_k': 14,
            'stoch_d': 3,
            
            # 其他指標
            'atr_period': 14,
            'cci_period': 20,
            'williams_period': 14,
            'momentum_period': 10,
            
            # 成交量指標
            'volume_sma': 20,
            'vpt_period': 14
        }
        
        # AI權重系統
        self.indicator_weights = {
            'ma_cross': 25,        # 移動平均線交叉
            'macd': 20,           # MACD指標
            'rsi': 15,            # RSI超買超賣
            'bollinger': 15,      # 布林帶突破
            'stochastic': 10,     # 隨機指標
            'volume': 10,         # 成交量確認
            'momentum': 5         # 動量指標
        }
        
        # 信號歷史記錄
        self.signal_history = []
        
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算所有技術指標"""
        try:
            if df is None or len(df) < 100:
                self.logger.warning("資料不足，無法計算完整技術指標")
                return None
                
            df = df.copy()
            
            # 1. 移動平均線系統
            df['ma7'] = ta.trend.SMAIndicator(close=df['close'], window=self.config['ma_short']).sma_indicator()
            df['ma25'] = ta.trend.SMAIndicator(close=df['close'], window=self.config['ma_medium']).sma_indicator()
            df['ma99'] = ta.trend.SMAIndicator(close=df['close'], window=self.config['ma_long']).sma_indicator()
            
            # 指數移動平均線
            df['ema12'] = ta.trend.EMAIndicator(close=df['close'], window=12).ema_indicator()
            df['ema26'] = ta.trend.EMAIndicator(close=df['close'], window=26).ema_indicator()
            
            # 2. MACD系統
            macd = ta.trend.MACD(close=df['close'], 
                               window_fast=self.config['macd_fast'],
                               window_slow=self.config['macd_slow'], 
                               window_sign=self.config['macd_signal'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # 3. RSI 相對強弱指數
            df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=self.config['rsi_period']).rsi()
            
            # 4. 布林帶 (Bollinger Bands)
            bb = ta.volatility.BollingerBands(close=df['close'], 
                                            window=self.config['bb_period'], 
                                            window_dev=self.config['bb_std'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # 5. 隨機指標 (Stochastic)
            stoch = ta.momentum.StochasticOscillator(high=df['high'], low=df['low'], close=df['close'],
                                                   window=self.config['stoch_k'], 
                                                   smooth_window=self.config['stoch_d'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # 6. 威廉指標 (%R)
            df['williams_r'] = ta.momentum.WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close'],
                                                            lbp=self.config['williams_period']).williams_r()
            
            # 7. 商品通道指數 (CCI)
            df['cci'] = ta.trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close'],
                                            window=self.config['cci_period']).cci()
            
            # 8. 平均真實波動範圍 (ATR)
            df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'],
                                                     window=self.config['atr_period']).average_true_range()
            
            # 9. 動量指標
            df['momentum'] = ta.momentum.ROCIndicator(close=df['close'], window=self.config['momentum_period']).roc()
            
            # 10. 成交量指標
            if 'volume' in df.columns:
                try:
                    # 成交量移動平均 - 使用pandas rolling
                    df['volume_sma'] = df['volume'].rolling(window=self.config['volume_sma']).mean()
                    
                    # 成交量價格趨勢指標
                    df['vpt'] = ta.volume.VolumePriceTrendIndicator(
                        close=df['close'], volume=df['volume']
                    ).volume_price_trend()
                    
                    # 資金流量指數
                    df['mfi'] = ta.volume.MFIIndicator(
                        high=df['high'], low=df['low'], close=df['close'], 
                        volume=df['volume'], window=14
                    ).money_flow_index()
                    
                    # OBV 能量潮指標
                    df['obv'] = ta.volume.OnBalanceVolumeIndicator(
                        close=df['close'], volume=df['volume']
                    ).on_balance_volume()
                    
                except Exception as e:
                    self.logger.warning(f"部分成交量指標計算失敗: {e}")
                    # 使用最基本的方法
                    df['volume_sma'] = df['volume'].rolling(window=self.config['volume_sma']).mean()
                    df['vpt'] = 0  # 設置默認值
                    df['mfi'] = 50  # MFI 中性值
                    df['obv'] = 0
            else:
                # 如果沒有成交量數據，設置默認值
                df['volume_sma'] = 0
                df['vpt'] = 0
                df['mfi'] = 50
                df['obv'] = 0
            
            # 11. 趨勢強度指標
            try:
                df['adx'] = ta.trend.ADXIndicator(
                    high=df['high'], low=df['low'], close=df['close'], window=14
                ).adx()
            except Exception as e:
                self.logger.warning(f"ADX指標計算失敗: {e}")
            
            # 清理NaN值
            df = df.dropna()
            
            self.logger.info(f"✅ 成功計算 {len(df)} 條記錄的所有技術指標")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ 計算技術指標失敗: {e}")
            return None
    
    def analyze_ma_cross_signals(self, df: pd.DataFrame) -> Dict:
        """根據教學模板分析移動平均線信號 - 重點關注多頭排列和均線交叉"""
        try:
            if len(df) < 3:
                return {'signal': 'NEUTRAL', 'strength': 0, 'details': '資料不足'}
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            ma7 = latest['ma7']
            ma25 = latest['ma25'] 
            ma99 = latest['ma99']
            
            prev_ma7 = prev['ma7']
            prev_ma25 = prev['ma25']
            
            price = latest['close']
            
            signals = []
            strength = 0
            signal_type = 'NEUTRAL'
            
            # 根據教學模板：MA5/MA7向上穿越MA25 - 黃金交叉
            if ma7 > ma25 and prev_ma7 <= prev_ma25:
                signals.append('短期均線向上穿越中期均線 (黃金交叉)')
                strength += 60
                signal_type = 'BULLISH'
                
            # MA7向下穿越MA25 - 死亡交叉  
            elif ma7 < ma25 and prev_ma7 >= prev_ma25:
                signals.append('短期均線向下穿越中期均線 (死亡交叉)')
                strength += 60
                signal_type = 'BEARISH'
            
            # 根據教學模板：多頭排列 MA7 > MA25 > MA99
            if ma7 > ma25 > ma99:
                signals.append('多頭排列 (MA7 > MA25 > MA99) - 中期趨勢偏多')
                strength += 40
                if signal_type == 'NEUTRAL':
                    signal_type = 'BULLISH'
            
            # 空頭排列 MA7 < MA25 < MA99
            elif ma7 < ma25 < ma99:
                signals.append('空頭排列 (MA7 < MA25 < MA99) - 中期趨勢偏空')
                strength += 40
                if signal_type == 'NEUTRAL':
                    signal_type = 'BEARISH'
            
            # 根據教學模板：價格與均線關係
            if price > ma7 > ma25:
                signals.append('價格站上短期和中期均線')
                strength += 30
                if signal_type == 'NEUTRAL':
                    signal_type = 'BULLISH'
            elif price > ma7:
                signals.append('價格站上短期均線')
                strength += 20
                if signal_type == 'NEUTRAL':
                    signal_type = 'BULLISH'
            elif price < ma7 < ma25:
                signals.append('價格跌破短期和中期均線')
                strength += 30
                if signal_type == 'NEUTRAL':
                    signal_type = 'BEARISH'
            elif price < ma7:
                signals.append('價格跌破短期均線')
                strength += 20
                if signal_type == 'NEUTRAL':
                    signal_type = 'BEARISH'
            
            # MA25作為支撐壓力位置
            ma25_distance_pct = abs(price - ma25) / ma25 * 100
            if ma25_distance_pct < 1:  # 距離MA25很近
                if price > ma25:
                    signals.append('價格靠近MA25支撐，觀察能否守穩')
                else:
                    signals.append('價格測試MA25壓力，觀察能否突破')
                strength += 15
            
            # 均線斜率判斷趨勢強度
            if len(df) >= 5:
                ma7_slope = (ma7 - df.iloc[-5]['ma7']) / 5
                ma25_slope = (ma25 - df.iloc[-5]['ma25']) / 5
                
                if ma7_slope > 0 and ma25_slope > 0:
                    signals.append('短中期均線向上傾斜')
                    if signal_type == 'BULLISH':
                        strength += 15
                elif ma7_slope < 0 and ma25_slope < 0:
                    signals.append('短中期均線向下傾斜')
                    if signal_type == 'BEARISH':
                        strength += 15
                        
            return {
                'signal': signal_type,
                'strength': min(strength, 100),
                'details': '; '.join(signals) if signals else '無明確均線信號',
                'values': {
                    'ma7': ma7, 
                    'ma25': ma25, 
                    'ma99': ma99,
                    'price': price,
                    'bullish_alignment': ma7 > ma25 > ma99,
                    'bearish_alignment': ma7 < ma25 < ma99,
                    'price_above_ma7': price > ma7,
                    'price_above_ma25': price > ma25
                }
            }
            
        except Exception as e:
            self.logger.error(f"MA交叉分析失敗: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'分析錯誤: {e}'}
    
    def analyze_macd_signals(self, df: pd.DataFrame) -> Dict:
        """根據教學模板增強版MACD分析 - 重點關注交叉信號和柱狀圖"""
        try:
            if len(df) < 5:
                return {'signal': 'NEUTRAL', 'strength': 0, 'details': '資料不足'}
                
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            macd = latest['macd']
            signal = latest['macd_signal']
            histogram = latest['macd_histogram']
            
            prev_macd = prev['macd']
            prev_signal = prev['macd_signal']
            prev_histogram = prev['macd_histogram']
            
            signals = []
            strength = 0
            signal_type = 'NEUTRAL'
            
            # 根據教學模板：MACD黃金交叉 - 強力買入信號
            if macd > signal and prev_macd <= prev_signal:
                signals.append('MACD黃金交叉 - 動能轉多')
                strength += 70  # 提高權重
                signal_type = 'BULLISH'
            
            # 根據教學模板：MACD死亡交叉 - 強力賣出信號
            elif macd < signal and prev_macd >= prev_signal:
                signals.append('MACD死亡交叉 - 空方動能轉強')
                strength += 70  # 提高權重
                signal_type = 'BEARISH'
            
            # 柱狀圖分析 - 動能變化
            if histogram > 0 and prev_histogram <= 0:
                signals.append('柱狀圖轉正 - 多頭動能增強')
                strength += 45
                if signal_type == 'NEUTRAL':
                    signal_type = 'BULLISH'
            elif histogram < 0 and prev_histogram >= 0:
                signals.append('柱狀圖轉負 - 空頭動能增強')
                strength += 45
                if signal_type == 'NEUTRAL':
                    signal_type = 'BEARISH'
            
            # 柱狀圖放大 - 動能增強
            elif abs(histogram) > abs(prev_histogram):
                if histogram > 0:
                    signals.append('多頭動能放大')
                    strength += 25
                    if signal_type == 'NEUTRAL':
                        signal_type = 'BULLISH'
                else:
                    signals.append('空頭動能放大')
                    strength += 25
                    if signal_type == 'NEUTRAL':
                        signal_type = 'BEARISH'
            
            # 柱狀圖縮小 - 動能轉弱
            elif abs(histogram) < abs(prev_histogram):
                signals.append('動能轉弱，謹慎觀望')
                strength += 15
            
            # MACD在零軸上下的位置也很重要
            if macd > 0 and signal > 0:
                signals.append('MACD位於零軸上方')
                if signal_type == 'BULLISH':
                    strength += 10
            elif macd < 0 and signal < 0:
                signals.append('MACD位於零軸下方')
                if signal_type == 'BEARISH':
                    strength += 10
                    
            return {
                'signal': signal_type,
                'strength': min(strength, 100),  # 限制最大強度
                'details': '; '.join(signals) if signals else '無明確MACD信號',
                'values': {
                    'macd': macd,
                    'signal': signal, 
                    'histogram': histogram,
                    'golden_cross': macd > signal and prev_macd <= prev_signal,
                    'death_cross': macd < signal and prev_macd >= prev_signal
                }
            }
            
        except Exception as e:
            self.logger.error(f"MACD分析失敗: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'分析錯誤: {e}'}
    
    def analyze_rsi_signals(self, df: pd.DataFrame) -> Dict:
        """RSI超買超賣分析"""
        try:
            latest = df.iloc[-1]
            rsi = latest['rsi']
            
            signals = []
            strength = 0
            
            if rsi > self.config['rsi_overbought']:
                signals.append(f'RSI={rsi:.1f} 超買區域')
                strength -= 20
            elif rsi < self.config['rsi_oversold']:
                signals.append(f'RSI={rsi:.1f} 超賣區域')
                strength += 20
            else:
                signals.append(f'RSI={rsi:.1f} 中性區域')
            
            # RSI趨勢
            if len(df) >= 3:
                rsi_trend = df['rsi'].tail(3).diff().mean()
                if rsi_trend > 2:
                    signals.append('RSI上升趨勢')
                    strength += 10
                elif rsi_trend < -2:
                    signals.append('RSI下降趨勢')
                    strength -= 10
            
            # 判斷信號方向
            if strength > 10:
                signal_type = 'BULLISH'
            elif strength < -10:
                signal_type = 'BEARISH'
            else:
                signal_type = 'NEUTRAL'
                
            return {
                'signal': signal_type,
                'strength': abs(strength),
                'details': '; '.join(signals),
                'rsi_value': rsi
            }
            
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'RSI分析錯誤: {e}'}
    
    def analyze_bollinger_signals(self, df: pd.DataFrame) -> Dict:
        """布林帶分析"""
        try:
            latest = df.iloc[-1]
            price = latest['close']
            bb_upper = latest['bb_upper']
            bb_lower = latest['bb_lower']
            bb_position = latest['bb_position']
            bb_width = latest['bb_width']
            
            signals = []
            strength = 0
            
            # 布林帶位置分析
            if bb_position > 0.8:
                signals.append('價格接近布林帶上軌')
                strength -= 15
            elif bb_position < 0.2:
                signals.append('價格接近布林帶下軌')
                strength += 15
            
            # 布林帶寬度分析
            if bb_width < 0.05:
                signals.append('布林帶收窄，準備突破')
                strength += 10
            elif bb_width > 0.15:
                signals.append('布林帶擴張，波動加大')
                
            # 突破分析
            if price > bb_upper:
                signals.append('突破布林帶上軌')
                strength += 20
            elif price < bb_lower:
                signals.append('突破布林帶下軌')
                strength -= 20
                
            # 判斷信號方向
            if strength > 10:
                signal_type = 'BULLISH'
            elif strength < -10:
                signal_type = 'BEARISH'
            else:
                signal_type = 'NEUTRAL'
                
            return {
                'signal': signal_type,
                'strength': abs(strength),
                'details': '; '.join(signals) if signals else '價格在布林帶中軌附近',
                'bb_position': bb_position
            }
            
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'布林帶分析錯誤: {e}'}
    
    def analyze_volume_signals(self, df: pd.DataFrame) -> Dict:
        """成交量分析"""
        try:
            if 'volume' not in df.columns:
                return {'signal': 'NEUTRAL', 'strength': 0, 'details': '無成交量數據'}
                
            latest = df.iloc[-1]
            volume = latest['volume']
            volume_sma = latest.get('volume_sma', volume)
            
            signals = []
            strength = 0
            
            # 成交量放大
            volume_ratio = volume / volume_sma if volume_sma > 0 else 1
            if volume_ratio > 1.5:
                signals.append(f'成交量放大 {volume_ratio:.1f}倍')
                strength += 15
            elif volume_ratio < 0.5:
                signals.append('成交量萎縮')
                strength -= 5
                
            # 價量配合分析
            if len(df) >= 2:
                price_change = (latest['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']
                if price_change > 0.01 and volume_ratio > 1.2:
                    signals.append('量價齊升')
                    strength += 20
                elif price_change < -0.01 and volume_ratio > 1.2:
                    signals.append('量價齊跌')
                    strength -= 20
                    
            # 判斷信號方向
            if strength > 10:
                signal_type = 'BULLISH'
            elif strength < -10:
                signal_type = 'BEARISH'
            else:
                signal_type = 'NEUTRAL'
                
            return {
                'signal': signal_type,
                'strength': abs(strength),
                'details': '; '.join(signals) if signals else '成交量正常',
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'成交量分析錯誤: {e}'}
    
    def comprehensive_analysis(self, df: pd.DataFrame, current_price: float) -> Dict:
        """根據轉折點檢測框架進行多指標交叉確認分析"""
        try:
            # 計算基礎技術指標
            df = self.calculate_all_indicators(df)
            
            if len(df) < 50:
                return self._empty_analysis()
            
            # 獲取最新數據
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            prev2 = df.iloc[-3] if len(df) > 3 else prev
            
            # 初始化信號檢測
            bullish_reversal_signals = []  # 底部反彈信號
            bearish_reversal_signals = []  # 高點回測信號
            
            total_bullish_score = 0
            total_bearish_score = 0
            
            # ================== 底部反彈信號檢測 ==================
            
            # 1. MACD 金叉檢測
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            macd_hist = latest.get('macd_histogram', 0)
            prev_macd = prev.get('macd', 0)
            prev_macd_signal = prev.get('macd_signal', 0)
            
            # MACD金叉 + 柱狀圖轉綠
            if macd > macd_signal and prev_macd <= prev_macd_signal:
                bullish_reversal_signals.append("MACD金叉出現")
                total_bullish_score += 30
            if macd_hist > 0 and prev.get('macd_histogram', 0) <= 0:
                bullish_reversal_signals.append("MACD柱狀圖轉綠")
                total_bullish_score += 20
                
            # 2. RSI 超賣反彈檢測
            rsi = latest.get('rsi', 50)
            prev_rsi = prev.get('rsi', 50)
            
            if rsi < 30 and rsi > prev_rsi:
                bullish_reversal_signals.append("RSI超賣區向上反彈")
                total_bullish_score += 25
            elif rsi < 35 and rsi > prev_rsi + 2:
                bullish_reversal_signals.append("RSI接近超賣區反彈")
                total_bullish_score += 15
                
            # 3. 均線支撐檢測
            ma5 = latest.get('ma7', current_price)  # 使用ma7作為短期均線
            ma10 = latest.get('ma25', current_price)  # 使用ma25作為中期均線
            prev_ma5 = prev.get('ma7', current_price)
            
            # K線站回均線
            if current_price > ma5 and prev['close'] <= prev_ma5:
                bullish_reversal_signals.append("K線站回短期均線")
                total_bullish_score += 20
            if ma5 > ma10:  # 短期均線在中期均線之上
                bullish_reversal_signals.append("短期均線多頭排列")
                total_bullish_score += 15
                
            # 4. 布林通道支撐檢測
            bb_lower = latest.get('bb_lower', current_price * 0.95)
            bb_middle = latest.get('bb_middle', current_price)
            
            if prev['close'] < bb_lower and current_price > bb_lower:
                bullish_reversal_signals.append("跌破布林下軌後收回")
                total_bullish_score += 25
            elif current_price < bb_middle and current_price > bb_lower:
                bullish_reversal_signals.append("接近布林下軌支撐")
                total_bullish_score += 10
                
            # 5. 成交量確認（下跌縮量，反彈放量）
            volume = latest.get('volume', 0)
            avg_volume = df['volume'].tail(10).mean()
            
            if volume > avg_volume * 1.2:  # 放量
                bullish_reversal_signals.append("反彈伴隨放量")
                total_bullish_score += 15
                
            # ================== 高點回測信號檢測 ==================
            
            # 1. MACD 死叉檢測
            if macd < macd_signal and prev_macd >= prev_macd_signal:
                bearish_reversal_signals.append("MACD死叉出現")
                total_bearish_score += 30
            if macd_hist < 0 and prev.get('macd_histogram', 0) >= 0:
                bearish_reversal_signals.append("MACD柱狀圖轉紅")
                total_bearish_score += 20
                
            # 2. RSI 超買回調檢測
            if rsi > 70 and rsi < prev_rsi:
                bearish_reversal_signals.append("RSI超買區向下回調")
                total_bearish_score += 25
            elif rsi > 65 and rsi < prev_rsi - 2:
                bearish_reversal_signals.append("RSI接近超買區回調")
                total_bearish_score += 15
                
            # 3. 均線壓力檢測
            if current_price < ma5 and prev['close'] >= prev_ma5:
                bearish_reversal_signals.append("K線跌破短期均線")
                total_bearish_score += 20
            if ma5 < ma10:  # 短期均線在中期均線之下
                bearish_reversal_signals.append("短期均線空頭排列")
                total_bearish_score += 15
                
            # 4. 布林通道壓力檢測
            bb_upper = latest.get('bb_upper', current_price * 1.05)
            
            if prev['close'] > bb_upper and current_price < bb_upper:
                bearish_reversal_signals.append("衝破布林上軌後拉回")
                total_bearish_score += 25
            elif current_price > bb_middle and current_price < bb_upper:
                bearish_reversal_signals.append("接近布林上軌壓力")
                total_bearish_score += 10
                
            # 5. 高點爆量檢測
            if volume > avg_volume * 1.5 and current_price < prev['close']:
                bearish_reversal_signals.append("高點爆量回調")
                total_bearish_score += 15
                
            # ================== 綜合判斷邏輯 ==================
            
            net_score = total_bullish_score - total_bearish_score
            total_signals = len(bullish_reversal_signals) + len(bearish_reversal_signals)
            
            # 根據多指標交叉確認決定最終信號
            if len(bullish_reversal_signals) >= 3 and total_bullish_score >= 60:
                if len(bullish_reversal_signals) >= 4:
                    final_signal = 'STRONG_BUY'
                    recommendation = '多指標確認底部反彈 - 強烈建議買進'
                else:
                    final_signal = 'BUY'
                    recommendation = '轉折點信號確認 - 建議買進'
            elif len(bearish_reversal_signals) >= 3 and total_bearish_score >= 60:
                if len(bearish_reversal_signals) >= 4:
                    final_signal = 'STRONG_SELL'
                    recommendation = '多指標確認高點回測 - 強烈建議賣出'
                else:
                    final_signal = 'SELL'
                    recommendation = '轉折點信號確認 - 建議賣出'
            elif net_score > 20:
                final_signal = 'BUY'
                recommendation = '偏多信號 - 建議買進'
            elif net_score < -20:
                final_signal = 'SELL'
                recommendation = '偏空信號 - 建議賣出'
            else:
                final_signal = 'HOLD'
                recommendation = '信號不明確 - 建議持有觀望'
                
            # 置信度計算 - 基於信號數量和強度
            if total_signals >= 4:
                confidence = min(90, 40 + (total_signals * 8) + (abs(net_score) / 5))
            elif total_signals >= 2:
                confidence = min(75, 30 + (total_signals * 10) + (abs(net_score) / 8))
            else:
                confidence = min(50, 20 + (total_signals * 5) + (abs(net_score) / 10))
                
            # 交易建議
            if final_signal in ['STRONG_BUY', 'BUY']:
                advice = f"檢測到{len(bullish_reversal_signals)}個底部反彈信號：{', '.join(bullish_reversal_signals[:3])}。建議分批進場，設置止損。"
            elif final_signal in ['STRONG_SELL', 'SELL']:
                advice = f"檢測到{len(bearish_reversal_signals)}個高點回測信號：{', '.join(bearish_reversal_signals[:3])}。建議減倉或止盈。"
            else:
                advice = "轉折點信號不明確，建議觀望等待更明確的多指標確認信號。"
                
            self.logger.info(f"📊 轉折點分析結果:")
            self.logger.info(f"   底部反彈信號: {len(bullish_reversal_signals)}個 (得分: {total_bullish_score})")
            self.logger.info(f"   高點回測信號: {len(bearish_reversal_signals)}個 (得分: {total_bearish_score})")
            self.logger.info(f"   淨分數: {net_score}")
            self.logger.info(f"   最終置信度: {confidence:.1f}%")
            
            return {
                'signal': final_signal,
                'recommendation': recommendation,
                'confidence': round(confidence, 1),
                'advice': advice,
                'bullish_signals': bullish_reversal_signals,
                'bearish_signals': bearish_reversal_signals,
                'bullish_score': total_bullish_score,
                'bearish_score': total_bearish_score,
                'net_score': net_score,
                'technical_details': {
                    'macd': f"{macd:.2f}",
                    'rsi': f"{rsi:.1f}",
                    'ma_trend': "多頭" if ma5 > ma10 else "空頭",
                    'bb_position': "上軌" if current_price > bb_upper else "下軌" if current_price < bb_lower else "中軌"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ 轉折點分析錯誤: {e}")
            return self._get_default_analysis()
    
    def _detect_bullish_divergence(self, df: pd.DataFrame) -> bool:
        """檢測看漲背離"""
        try:
            if len(df) < 10:
                return False
                
            # 價格創新低但MACD未創新低
            price_lows = df['close'].rolling(window=5).min()
            macd_lows = df['macd'].rolling(window=5).min()
            
            recent_price_low = price_lows.iloc[-1]
            recent_macd_low = macd_lows.iloc[-1]
            
            prev_price_low = price_lows.iloc[-6:-1].min()
            prev_macd_low = macd_lows.iloc[-6:-1].min()
            
            return (recent_price_low < prev_price_low and recent_macd_low > prev_macd_low)
            
        except:
            return False
    
    def _detect_bearish_divergence(self, df: pd.DataFrame) -> bool:
        """檢測看跌背離"""
        try:
            if len(df) < 10:
                return False
                
            # 價格創新高但MACD未創新高
            price_highs = df['close'].rolling(window=5).max()
            macd_highs = df['macd'].rolling(window=5).max()
            
            recent_price_high = price_highs.iloc[-1]
            recent_macd_high = macd_highs.iloc[-1]
            
            prev_price_high = price_highs.iloc[-6:-1].max()
            prev_macd_high = macd_highs.iloc[-6:-1].max()
            
            return (recent_price_high > prev_price_high and recent_macd_high < prev_macd_high)
            
        except:
            return False
    
    def _get_default_analysis(self) -> Dict:
        """取得預設分析結果"""
        return {
            'recommendation': 'HOLD',
            'confidence': 0,
            'bullish_score': 0,
            'bearish_score': 0,
            'net_score': 0,
            'advice': '資料不足，建議等待',
            'detailed_analysis': {},
            'indicator_contributions': {},
            'technical_values': {},
            'timestamp': datetime.now()
        }
    
    def format_analysis_report(self, analysis: Dict) -> str:
        """格式化分析報告"""
        try:
            report = f"""
🤖 <b>AI多重技術指標分析報告</b>

🎯 <b>綜合建議:</b> {analysis['advice']}
📊 <b>信號強度:</b> {analysis['recommendation']}
🎪 <b>置信度:</b> {analysis['confidence']:.1f}%

📈 <b>各指標詳細分析:</b>
"""
            
            detailed = analysis.get('detailed_analysis', {})
            
            # MA分析
            if 'ma_cross' in detailed:
                ma = detailed['ma_cross']
                report += f"• 📏 均線系統: {ma['signal']} ({ma['strength']:.0f}%)\n"
                report += f"  └ {ma['details']}\n"
            
            # MACD分析  
            if 'macd' in detailed:
                macd = detailed['macd']
                report += f"• 📊 MACD: {macd['signal']} ({macd['strength']:.0f}%)\n"
                report += f"  └ {macd['details']}\n"
                
            # RSI分析
            if 'rsi' in detailed:
                rsi = detailed['rsi']
                report += f"• 📈 RSI: {rsi['signal']} ({rsi['strength']:.0f}%)\n"
                report += f"  └ {rsi['details']}\n"
                
            # 布林帶分析
            if 'bollinger' in detailed:
                bb = detailed['bollinger']
                report += f"• 📊 布林帶: {bb['signal']} ({bb['strength']:.0f}%)\n"
                report += f"  └ {bb['details']}\n"
                
            # 成交量分析
            if 'volume' in detailed:
                vol = detailed['volume']
                report += f"• 📊 成交量: {vol['signal']} ({vol['strength']:.0f}%)\n"
                report += f"  └ {vol['details']}\n"
            
            # 技術指標數值
            tech_values = analysis.get('technical_values', {})
            if tech_values:
                report += f"\n📊 <b>關鍵技術指標數值:</b>\n"
                if 'ma7' in tech_values:
                    report += f"• MA7: {tech_values['ma7']:.1f}\n"
                if 'ma25' in tech_values:
                    report += f"• MA25: {tech_values['ma25']:.1f}\n"
                if 'rsi' in tech_values:
                    report += f"• RSI: {tech_values['rsi']:.1f}\n"
                if 'macd' in tech_values:
                    report += f"• MACD: {tech_values['macd']:.2f}\n"
            
            return report.strip()
            
        except Exception as e:
            return f"報告生成失敗: {e}" 