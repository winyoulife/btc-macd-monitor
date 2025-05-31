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
        """分析移動平均線交叉信號"""
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
            
            signals = []
            strength = 0
            
            # 黃金交叉: MA7向上穿越MA25
            if ma7 > ma25 and prev_ma7 <= prev_ma25:
                signals.append('MA7向上穿越MA25 (黃金交叉)')
                strength += 40
                
            # 死亡交叉: MA7向下穿越MA25  
            elif ma7 < ma25 and prev_ma7 >= prev_ma25:
                signals.append('MA7向下穿越MA25 (死亡交叉)')
                strength -= 40
            
            # 長期趨勢確認
            if ma7 > ma25 > ma99:
                signals.append('多頭排列: MA7 > MA25 > MA99')
                strength += 30
            elif ma7 < ma25 < ma99:
                signals.append('空頭排列: MA7 < MA25 < MA99')
                strength -= 30
            
            # 價格與均線關係
            price = latest['close']
            if price > ma7 > ma25:
                signals.append('價格位於短中期均線上方')
                strength += 15
            elif price < ma7 < ma25:
                signals.append('價格位於短中期均線下方')
                strength -= 15
            
            # 判斷信號方向
            if strength > 20:
                signal_type = 'BULLISH'
            elif strength < -20:
                signal_type = 'BEARISH'
            else:
                signal_type = 'NEUTRAL'
                
            return {
                'signal': signal_type,
                'strength': abs(strength),
                'details': '; '.join(signals) if signals else '無明確信號',
                'ma_values': {'ma7': ma7, 'ma25': ma25, 'ma99': ma99}
            }
            
        except Exception as e:
            self.logger.error(f"MA交叉分析失敗: {e}")
            return {'signal': 'NEUTRAL', 'strength': 0, 'details': f'分析錯誤: {e}'}
    
    def analyze_macd_signals(self, df: pd.DataFrame) -> Dict:
        """增強版MACD分析"""
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
            
            # MACD線交叉信號
            if macd > signal and prev_macd <= prev_signal:
                signals.append('MACD黃金交叉')
                strength += 35
            elif macd < signal and prev_macd >= prev_signal:
                signals.append('MACD死亡交叉')
                strength -= 35
            
            # 直方圖變化
            if histogram > 0 and prev_histogram <= 0:
                signals.append('直方圖轉正')
                strength += 20
            elif histogram < 0 and prev_histogram >= 0:
                signals.append('直方圖轉負')
                strength -= 20
                
            # 背離檢測
            recent_data = df.tail(10)
            if self._detect_bullish_divergence(recent_data):
                signals.append('檢測到看漲背離')
                strength += 25
            elif self._detect_bearish_divergence(recent_data):
                signals.append('檢測到看跌背離')
                strength -= 25
            
            # 判斷信號方向
            if strength > 15:
                signal_type = 'BULLISH'
            elif strength < -15:
                signal_type = 'BEARISH'
            else:
                signal_type = 'NEUTRAL'
                
            return {
                'signal': signal_type,
                'strength': abs(strength),
                'details': '; '.join(signals) if signals else '無明確信號',
                'macd_values': {'macd': macd, 'signal': signal, 'histogram': histogram}
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
        """綜合AI技術分析"""
        try:
            self.logger.info("🤖 開始綜合AI技術分析...")
            
            # 計算所有技術指標
            df_with_indicators = self.calculate_all_indicators(df)
            if df_with_indicators is None:
                return self._get_default_analysis()
            
            # 各項指標分析
            ma_analysis = self.analyze_ma_cross_signals(df_with_indicators)
            macd_analysis = self.analyze_macd_signals(df_with_indicators)
            rsi_analysis = self.analyze_rsi_signals(df_with_indicators)
            bb_analysis = self.analyze_bollinger_signals(df_with_indicators)
            volume_analysis = self.analyze_volume_signals(df_with_indicators)
            
            # AI權重計算 - 修復置信度計算邏輯
            total_bullish_score = 0
            total_bearish_score = 0
            max_possible_score = sum(self.indicator_weights.values())
            
            analyses = {
                'ma_cross': ma_analysis,
                'macd': macd_analysis, 
                'rsi': rsi_analysis,
                'bollinger': bb_analysis,
                'volume': volume_analysis
            }
            
            # 詳細記錄各指標的貢獻
            indicator_contributions = {}
            
            for indicator, analysis in analyses.items():
                weight = self.indicator_weights.get(indicator, 0)
                strength = analysis['strength']
                
                if analysis['signal'] == 'BULLISH':
                    contribution = (strength / 100) * weight
                    total_bullish_score += contribution
                    indicator_contributions[indicator] = {'type': 'BULLISH', 'contribution': contribution, 'strength': strength}
                elif analysis['signal'] == 'BEARISH':
                    contribution = (strength / 100) * weight
                    total_bearish_score += contribution
                    indicator_contributions[indicator] = {'type': 'BEARISH', 'contribution': contribution, 'strength': strength}
                else:
                    indicator_contributions[indicator] = {'type': 'NEUTRAL', 'contribution': 0, 'strength': strength}
            
            # 計算最終信號
            net_score = total_bullish_score - total_bearish_score
            
            # 修復置信度計算 - 使用有效信號的總強度
            active_signals_strength = sum([contrib['strength'] for contrib in indicator_contributions.values() 
                                         if contrib['type'] != 'NEUTRAL'])
            total_active_indicators = len([contrib for contrib in indicator_contributions.values() 
                                         if contrib['type'] != 'NEUTRAL'])
            
            if total_active_indicators > 0:
                # 基於實際參與的指標計算置信度
                avg_signal_strength = active_signals_strength / total_active_indicators
                indicator_coverage = total_active_indicators / len(analyses)  # 指標覆蓋率
                confidence = (avg_signal_strength * indicator_coverage * abs(net_score) / max_possible_score) * 100
                confidence = min(95, max(15, confidence))
            else:
                confidence = 15  # 沒有明確信號時的最低置信度
            
            # 記錄調試信息
            self.logger.info(f"📊 指標分析結果:")
            self.logger.info(f"   看漲分數: {total_bullish_score:.2f}")
            self.logger.info(f"   看跌分數: {total_bearish_score:.2f}")
            self.logger.info(f"   淨分數: {net_score:.2f}")
            self.logger.info(f"   活躍指標: {total_active_indicators}/{len(analyses)}")
            self.logger.info(f"   平均強度: {avg_signal_strength:.1f}%" if total_active_indicators > 0 else "   平均強度: N/A")
            self.logger.info(f"   最終置信度: {confidence:.1f}%")
            
            if net_score > 15:
                final_signal = 'STRONG_BUY'
                recommendation = '強烈建議買進'
            elif net_score > 5:
                final_signal = 'BUY'
                recommendation = '建議買進'
            elif net_score < -15:
                final_signal = 'STRONG_SELL'
                recommendation = '強烈建議賣出'
            elif net_score < -5:
                final_signal = 'SELL'
                recommendation = '建議賣出'
            else:
                final_signal = 'HOLD'
                recommendation = '建議持有觀望'
            
            # 獲取最新技術指標值
            latest = df_with_indicators.iloc[-1]
            
            return {
                'recommendation': final_signal,
                'confidence': confidence,
                'bullish_score': total_bullish_score,
                'bearish_score': total_bearish_score,
                'net_score': net_score,
                'advice': recommendation,
                'detailed_analysis': analyses,
                'indicator_contributions': indicator_contributions,  # 新增詳細貢獻記錄
                'technical_values': {
                    'macd': latest['macd'],
                    'macd_signal': latest['macd_signal'],
                    'macd_histogram': latest['macd_histogram'],
                    'rsi': latest['rsi'],
                    'ma7': latest['ma7'],
                    'ma25': latest['ma25'],
                    'ma99': latest['ma99'],
                    'bb_position': latest['bb_position'],
                    'volume_ratio': volume_analysis.get('volume_ratio', 1.0)
                },
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"❌ 綜合分析失敗: {e}")
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