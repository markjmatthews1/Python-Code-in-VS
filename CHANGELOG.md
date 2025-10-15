# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-10-15

### Wishlist Tracker - Interface Improvements

#### Fixed
- **Three-Tier Sorting Algorithm**: Corrected sorting logic to properly prioritize:
  1. Uptrend tickers (positive price movement)
  2. Positive premium opportunities 
  3. Negative premium opportunities (sorted by most negative = best deals first)

#### Enhanced
- **Loading Spinner**: 
  - Enlarged spinner 5x for better visibility
  - Added colorized animation (red → green → blue → orange)
  - Implemented overlay positioning to prevent header expansion
  - Changed status text from "Ready" to "Working..." during operations

#### Improved
- **Data Presentation**:
  - Removed decorative stars (★) from Put Target column for cleaner appearance
  - Streamlined data format: `65.00 @ $10.15 (12/19)` (was `★ 65.00 @ $10.15 (12/19) ★`)
  - Natural column sizing achieved through content optimization
  - Reverted column header to simple "Put Target" from extended text

- **Column Management**:
  - Simplified Premium column from "Premium vs Current" to "Premium"
  - Optimized column width enforcement strategies
  - Improved manual resizing capability for user preference

#### Technical
- Enhanced GUI responsiveness and visual feedback
- Improved code maintainability and readability
- Better user experience with professional interface styling

### Impact
- Cleaner, more professional appearance
- Better data readability and comprehension
- Maintained all core functionality while improving usability
- Reduced visual clutter while preserving essential information

---

## [2.0.0] - 2025-10-14

### Wishlist Tracker - Core Implementation

#### Added
- **E*TRADE API Integration**: Complete OAuth authentication and data fetching
- **Options Analysis Engine**: Advanced put option evaluation with probability calculations
- **GUI Dashboard**: Professional tkinter interface with real-time data updates
- **Three-Tier Sorting**: Intelligent ranking system for optimal trade opportunities
- **Ticker Management**: Easy watchlist addition and removal functionality
- **Error Handling**: Robust network error management and retry logic

#### Features
- Real-time stock price and options data fetching
- Negative premium put identification and analysis
- Combined scoring system (premium yield + negative premium amount)
- Multi-expiration date support (current month + 2 additional)
- Professional data presentation with status monitoring

---

## [1.0.0] - Initial Release

### Core Applications

#### Enhanced Day Trader
- Live signals and market analysis
- Real-time data processing
- Technical indicator calculations

#### Dividend Tracker
- Portfolio dividend monitoring
- Income calculation and projections
- Historical dividend data analysis

#### E*TRADE Integration
- API client implementation
- Authentication management
- Market data retrieval

#### Price Tracker
- Multi-asset price monitoring
- Alert system implementation
- Historical price tracking

#### Recovery App
- Data recovery utilities
- Backup management systems
- File integrity verification

#### Weekly Pay Rotation App
- Work schedule management
- Pay calculation utilities
- Rotation tracking systems

---

## Development Notes

### Version Numbering
- **Major.Minor.Patch** format
- Major: Breaking changes or significant new features
- Minor: New features, improvements, UI enhancements
- Patch: Bug fixes, small improvements, documentation updates

### Commit Strategy
- Feature branches for development
- Descriptive commit messages
- Regular backup commits to GitHub
- Version tags for releases