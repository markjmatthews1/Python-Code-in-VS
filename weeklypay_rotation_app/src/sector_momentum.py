"""
Sector Momentum Tracker for WeeklyPay™ Rotation App
Tracks sector ETF momentum using RSI and SMA crossovers
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
import datetime
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SectorMomentum:
    """Sector momentum analysis data"""
    symbol: str
    name: str
    sector: str
    price: float
    rsi_14: float
    sma_5: float
    sma_20: float
    sma_50: float
    sma_crossover: bool  # True if 5-day > 20-day
    volume: int
    momentum_signal: str  # "BULLISH", "BEARISH", "NEUTRAL"
    confidence: float  # 0.0 to 1.0
    last_updated: str
    technical_notes: List[str]

class SectorMomentumTracker:
    """Tracks momentum for sector ETFs using technical indicators"""
    
    def __init__(self):
        self.sector_etfs = {
            'SMH': {
                'name': 'VanEck Semiconductor ETF',
                'sector': 'Semiconductors',
                'description': 'Tracks semiconductor companies'
            },
            'XLK': {
                'name': 'Technology Select Sector SPDR Fund',
                'sector': 'Technology',
                'description': 'Tracks technology sector'
            },
            'XLC': {
                'name': 'Communication Services Select Sector SPDR Fund',
                'sector': 'Communication Services',
                'description': 'Tracks communication services sector'
            }
        }
        
        self.momentum_data: Dict[str, SectorMomentum] = {}
        self.data_dir = Path("data")
        self.cache_file = self.data_dir / "sector_momentum_cache.json"
        
        # Technical analysis parameters
        self.rsi_period = 14
        self.sma_short = 5
        self.sma_medium = 20
        self.sma_long = 50
        
        # Momentum thresholds
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.rsi_bullish_threshold = 60
        self.rsi_bearish_threshold = 40
        
        print(f"📈 Sector Momentum Tracker initialized")
        print(f"   📊 Tracking: {', '.join(self.sector_etfs.keys())}")
        print(f"   🔧 RSI Period: {self.rsi_period}, SMA: {self.sma_short}/{self.sma_medium}/{self.sma_long}")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    def fetch_yahoo_data(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                print(f"⚠️  No data returned for {symbol}")
                return None
            
            print(f"📊 Yahoo Finance: Retrieved {len(data)} days for {symbol}")
            return data
            
        except Exception as e:
            print(f"❌ Yahoo Finance error for {symbol}: {e}")
            return None
    
    def fetch_alpha_vantage_data(self, symbol: str, api_key: str) -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage API"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': 'compact'  # Last 100 days
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"❌ Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"⚠️  Alpha Vantage rate limit for {symbol}")
                return None
            
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                print(f"⚠️  No time series data for {symbol}")
                return None
            
            # Convert to DataFrame
            df_data = []
            for date_str, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(date_str),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            print(f"📊 Alpha Vantage: Retrieved {len(df)} days for {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Alpha Vantage error for {symbol}: {e}")
            return None
    
    def analyze_sector_momentum(self, symbol: str, data: pd.DataFrame) -> SectorMomentum:
        """Analyze momentum for a sector ETF"""
        try:
            # Calculate technical indicators
            closes = data['Close']
            current_price = float(closes.iloc[-1])
            current_volume = int(data['Volume'].iloc[-1])
            
            # RSI calculation
            rsi_series = self.calculate_rsi(closes, self.rsi_period)
            current_rsi = float(rsi_series.iloc[-1])
            
            # SMA calculations
            sma_5_series = self.calculate_sma(closes, self.sma_short)
            sma_20_series = self.calculate_sma(closes, self.sma_medium)
            sma_50_series = self.calculate_sma(closes, self.sma_long)
            
            current_sma_5 = float(sma_5_series.iloc[-1])
            current_sma_20 = float(sma_20_series.iloc[-1])
            current_sma_50 = float(sma_50_series.iloc[-1])
            
            # SMA crossover (5-day > 20-day)
            sma_crossover = current_sma_5 > current_sma_20
            
            # Momentum signal analysis
            technical_notes = []
            momentum_signal = "NEUTRAL"
            confidence = 0.5
            
            # RSI analysis
            if current_rsi >= self.rsi_overbought:
                technical_notes.append(f"RSI overbought ({current_rsi:.1f})")
                if current_rsi >= 75:
                    momentum_signal = "BEARISH"
                    confidence = 0.8
                else:
                    confidence += 0.1
            elif current_rsi <= self.rsi_oversold:
                technical_notes.append(f"RSI oversold ({current_rsi:.1f})")
                momentum_signal = "BULLISH"
                confidence = 0.8
            elif current_rsi >= self.rsi_bullish_threshold:
                technical_notes.append(f"RSI bullish ({current_rsi:.1f})")
                momentum_signal = "BULLISH"
                confidence += 0.2
            elif current_rsi <= self.rsi_bearish_threshold:
                technical_notes.append(f"RSI bearish ({current_rsi:.1f})")
                momentum_signal = "BEARISH"
                confidence += 0.2
            
            # SMA crossover analysis
            if sma_crossover:
                technical_notes.append("5-day SMA > 20-day SMA (bullish)")
                if momentum_signal == "NEUTRAL":
                    momentum_signal = "BULLISH"
                confidence += 0.15
            else:
                technical_notes.append("5-day SMA < 20-day SMA (bearish)")
                if momentum_signal == "NEUTRAL":
                    momentum_signal = "BEARISH"
                confidence += 0.15
            
            # Price vs SMA analysis
            if current_price > current_sma_50:
                technical_notes.append("Price > 50-day SMA (uptrend)")
                confidence += 0.1
            else:
                technical_notes.append("Price < 50-day SMA (downtrend)")
                if momentum_signal == "BULLISH":
                    confidence -= 0.1
            
            # Volume analysis (simple)
            avg_volume = data['Volume'].tail(20).mean()
            if current_volume > avg_volume * 1.5:
                technical_notes.append("High volume (strong signal)")
                confidence += 0.1
            elif current_volume < avg_volume * 0.5:
                technical_notes.append("Low volume (weak signal)")
                confidence -= 0.1
            
            # Cap confidence
            confidence = min(max(confidence, 0.0), 1.0)
            
            return SectorMomentum(
                symbol=symbol,
                name=self.sector_etfs[symbol]['name'],
                sector=self.sector_etfs[symbol]['sector'],
                price=current_price,
                rsi_14=current_rsi,
                sma_5=current_sma_5,
                sma_20=current_sma_20,
                sma_50=current_sma_50,
                sma_crossover=sma_crossover,
                volume=current_volume,
                momentum_signal=momentum_signal,
                confidence=confidence,
                last_updated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                technical_notes=technical_notes
            )
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            # Return neutral momentum on error
            return SectorMomentum(
                symbol=symbol,
                name=self.sector_etfs[symbol]['name'],
                sector=self.sector_etfs[symbol]['sector'],
                price=0.0,
                rsi_14=50.0,
                sma_5=0.0,
                sma_20=0.0,
                sma_50=0.0,
                sma_crossover=False,
                volume=0,
                momentum_signal="NEUTRAL",
                confidence=0.0,
                last_updated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                technical_notes=["Analysis failed - using neutral values"]
            )
    
    def update_all_sectors(self, alpha_vantage_key: str = None) -> Dict[str, SectorMomentum]:
        """Update momentum data for all sector ETFs"""
        print(f"🔄 Updating sector momentum data...")
        
        for symbol in self.sector_etfs.keys():
            print(f"\n📊 Analyzing {symbol} ({self.sector_etfs[symbol]['name']})...")
            
            # Try Yahoo Finance first
            data = self.fetch_yahoo_data(symbol)
            
            # Fallback to Alpha Vantage if Yahoo fails
            if data is None and alpha_vantage_key:
                print(f"   🔄 Trying Alpha Vantage for {symbol}...")
                data = self.fetch_alpha_vantage_data(symbol, alpha_vantage_key)
            
            if data is not None:
                momentum = self.analyze_sector_momentum(symbol, data)
                self.momentum_data[symbol] = momentum
                
                signal_icon = "🟢" if momentum.momentum_signal == "BULLISH" else "🔴" if momentum.momentum_signal == "BEARISH" else "🟡"
                print(f"   {signal_icon} {symbol}: {momentum.momentum_signal} (RSI: {momentum.rsi_14:.1f}, Confidence: {momentum.confidence:.2f})")
            else:
                print(f"   ❌ Failed to get data for {symbol}")
        
        # Save to cache
        self.save_momentum_cache()
        
        return self.momentum_data
    
    def get_sector_signals(self) -> Dict[str, str]:
        """Get simplified sector signals for the signal engine"""
        signals = {}
        for symbol, momentum in self.momentum_data.items():
            signals[symbol] = momentum.momentum_signal
        return signals
    
    def get_sector_rsi_values(self) -> Dict[str, float]:
        """Get RSI values for the signal engine"""
        rsi_values = {}
        for symbol, momentum in self.momentum_data.items():
            rsi_values[symbol] = momentum.rsi_14
        return rsi_values
    
    def display_momentum_dashboard(self):
        """Display comprehensive momentum dashboard"""
        print("\n" + "="*80)
        print("📈 SECTOR MOMENTUM DASHBOARD")
        print("="*80)
        
        if not self.momentum_data:
            print("📝 No momentum data available. Run update_all_sectors() first.")
            return
        
        for symbol, momentum in self.momentum_data.items():
            signal_icon = "🟢" if momentum.momentum_signal == "BULLISH" else "🔴" if momentum.momentum_signal == "BEARISH" else "🟡"
            crossover_icon = "📈" if momentum.sma_crossover else "📉"
            
            print(f"\n{signal_icon} {symbol} - {momentum.name}")
            print(f"   💰 Price: ${momentum.price:.2f}")
            print(f"   📊 RSI (14): {momentum.rsi_14:.1f}")
            print(f"   📈 SMA 5/20/50: ${momentum.sma_5:.2f} / ${momentum.sma_20:.2f} / ${momentum.sma_50:.2f}")
            print(f"   {crossover_icon} SMA Crossover: {'Bullish' if momentum.sma_crossover else 'Bearish'}")
            print(f"   🎯 Signal: {momentum.momentum_signal} (Confidence: {momentum.confidence:.1%})")
            print(f"   🔧 Technical Notes:")
            for note in momentum.technical_notes:
                print(f"      • {note}")
            print(f"   ⏰ Updated: {momentum.last_updated}")
        
        # Summary
        bullish_count = sum(1 for m in self.momentum_data.values() if m.momentum_signal == "BULLISH")
        bearish_count = sum(1 for m in self.momentum_data.values() if m.momentum_signal == "BEARISH")
        neutral_count = len(self.momentum_data) - bullish_count - bearish_count
        
        print(f"\n📊 SECTOR SUMMARY:")
        print(f"   🟢 Bullish: {bullish_count} sectors")
        print(f"   🔴 Bearish: {bearish_count} sectors")
        print(f"   🟡 Neutral: {neutral_count} sectors")
        
        # Overall market sentiment
        if bullish_count > bearish_count:
            overall_sentiment = "🟢 BULLISH MARKET"
        elif bearish_count > bullish_count:
            overall_sentiment = "🔴 BEARISH MARKET"
        else:
            overall_sentiment = "🟡 NEUTRAL MARKET"
        
        print(f"   🌟 Overall Sentiment: {overall_sentiment}")
        print("="*80)
    
    def save_momentum_cache(self):
        """Save momentum data to cache file"""
        try:
            cache_data = {
                'last_updated': datetime.datetime.now().isoformat(),
                'momentum_data': {
                    symbol: {
                        'symbol': momentum.symbol,
                        'name': momentum.name,
                        'sector': momentum.sector,
                        'price': momentum.price,
                        'rsi_14': momentum.rsi_14,
                        'sma_5': momentum.sma_5,
                        'sma_20': momentum.sma_20,
                        'sma_50': momentum.sma_50,
                        'sma_crossover': momentum.sma_crossover,
                        'volume': momentum.volume,
                        'momentum_signal': momentum.momentum_signal,
                        'confidence': momentum.confidence,
                        'last_updated': momentum.last_updated,
                        'technical_notes': momentum.technical_notes
                    }
                    for symbol, momentum in self.momentum_data.items()
                }
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Sector momentum cache saved: {len(self.momentum_data)} sectors")
            
        except Exception as e:
            print(f"❌ Error saving momentum cache: {e}")
    
    def load_momentum_cache(self) -> bool:
        """Load momentum data from cache file"""
        try:
            if not self.cache_file.exists():
                print("📝 No sector momentum cache found")
                return False
            
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check cache age
            last_updated = datetime.datetime.fromisoformat(cache_data['last_updated'])
            age_hours = (datetime.datetime.now() - last_updated).total_seconds() / 3600
            
            if age_hours > 4:  # 4 hour cache expiry
                print(f"⏰ Sector momentum cache is {age_hours:.1f} hours old - refresh recommended")
            
            # Load momentum data
            self.momentum_data.clear()
            for symbol, data in cache_data['momentum_data'].items():
                momentum = SectorMomentum(
                    symbol=data['symbol'],
                    name=data['name'],
                    sector=data['sector'],
                    price=data['price'],
                    rsi_14=data['rsi_14'],
                    sma_5=data['sma_5'],
                    sma_20=data['sma_20'],
                    sma_50=data['sma_50'],
                    sma_crossover=data['sma_crossover'],
                    volume=data['volume'],
                    momentum_signal=data['momentum_signal'],
                    confidence=data['confidence'],
                    last_updated=data['last_updated'],
                    technical_notes=data['technical_notes']
                )
                self.momentum_data[symbol] = momentum
            
            print(f"📂 Loaded sector momentum cache: {len(self.momentum_data)} sectors")
            return True
            
        except Exception as e:
            print(f"❌ Error loading momentum cache: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Initialize tracker
    tracker = SectorMomentumTracker()
    
    # Try loading cache first
    cache_loaded = tracker.load_momentum_cache()
    
    if not cache_loaded:
        print("\n🔄 No cache found, fetching fresh data...")
        # Update all sectors (Yahoo Finance only for demo)
        tracker.update_all_sectors()
    
    # Display dashboard
    tracker.display_momentum_dashboard()
    
    # Get signals for signal engine integration
    print(f"\n🔧 SIGNAL ENGINE INTEGRATION:")
    sector_signals = tracker.get_sector_signals()
    sector_rsi = tracker.get_sector_rsi_values()
    
    for symbol in sector_signals:
        print(f"   {symbol}: {sector_signals[symbol]} (RSI: {sector_rsi[symbol]:.1f})")
    
    print(f"\n✅ Sector momentum analysis complete!")