# Price Tracker - Multi-Vendor Product Price Monitoring

## Quick Start
```bash
# Navigate to price tracker directory
cd "C:\Users\mjmat\Python Code in VS\price_tracker"

# Run the app (super easy!)
python pt.py
```

**Or even faster:**
- Just double-click `pt.bat` for instant launch!

## What It Does
🛒 **Tracks prices** across Amazon, Home Depot, Lowes, Walmart, and other major retailers  
📊 **Price history charts** similar to your trading apps but for products  
🎯 **Price alerts** when items hit your target price  
📱 **Simple GUI** with product watchlist management  

## Pre-configured Products
The app comes ready to track your requested items:
- **Ryobi 40V Snow Shovel** (Target: $200)
- **Ryobi 40V Snow Blower** (Target: $400)  
- **Battery Handheld Seeder/Spreader** (Target: $100)

## Main Features

### 🔍 Check Prices
- Click "Check Prices" to scan all your tracked products
- See current prices from multiple vendors
- Automatic price history logging

### ➕ Add Products
- Add any product you want to track
- Set your target price for alerts
- Categorize by type (Tools, Garden, Electronics, etc.)

### 📊 View History
- See price trends over time
- Compare vendor pricing
- Track price drops and spikes

### 🌐 Quick Amazon Search
- Select any product and click "Amazon Search"
- Opens Amazon directly to that product search

## Current Status
- ✅ **GUI Framework**: Complete and working
- ✅ **Product Management**: Add, track, and organize products
- ✅ **Price Simulation**: Demo pricing for your Ryobi tools
- 🚧 **Real API Integration**: Coming next (Amazon, Home Depot, Lowes)
- 🚧 **Email Alerts**: Planned feature
- 🚧 **Advanced Charts**: Price trend visualization

## Files Structure
```
price_tracker/
├── pt.py              # Main application (short name for easy typing!)
├── pt.bat             # Windows batch launcher
├── apis.py            # API integrations (Amazon, Home Depot, etc.)
├── requirements.txt   # Python dependencies
├── config.json        # Your tracked products (auto-created)
└── price_data.csv     # Price history (auto-created)
```

## Next Steps
1. **Test the current demo** - Try adding/removing products, checking simulated prices
2. **Real API integration** - Connect to actual Amazon/Home Depot APIs
3. **Price alerts** - Email notifications when targets are hit
4. **Advanced features** - Price predictions, deal alerts, stock notifications

## Usage Tips
- The app name is **super short** (`pt.py`) so it's easy to type for testing
- All your data is saved locally in CSV and JSON files
- Add products with specific model numbers for better tracking
- Set realistic target prices for meaningful alerts

**Ready to track those Ryobi tools and find the best deals!** 🔧⚡