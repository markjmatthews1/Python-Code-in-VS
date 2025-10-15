"""
Data Models for RecoveryApp
Contains TickerPosition and TradeEntry classes for tracking underwater positions and recovery trades
"""
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json

@dataclass
class TradeEntry:
    """
    Represents a single trade entry for recovery strategy
    """
    type: str  # 'short_put', 'short_call', 'covered_call', 'synthetic', etc.
    strike: float
    expiry: str  # Format: 'YYYY-MM-DD'
    premium: float
    status: str  # 'open', 'assigned', 'closed', 'expired'
    entry_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    quantity: int = 1
    commission: float = 0.0
    notes: str = ""
    
    def __post_init__(self):
        """Validate trade entry data"""
        valid_types = ['short_put', 'short_call', 'covered_call', 'protective_put', 'synthetic', 'buy_write']
        valid_statuses = ['open', 'assigned', 'closed', 'expired']
        
        if self.type not in valid_types:
            raise ValueError(f"Invalid trade type: {self.type}. Must be one of {valid_types}")
        
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")
        
        if self.strike <= 0:
            raise ValueError("Strike price must be positive")
        
        # Premium can be negative for protective trades (buying options)
        # Positive premium = collected (selling), Negative premium = paid (buying)
    
    def is_active(self) -> bool:
        """Check if trade is still active"""
        return self.status == 'open'
    
    def net_premium(self) -> float:
        """Calculate net premium per share after commission
        
        Premium is per share, but commission is for the entire trade.
        For options: quantity represents number of contracts (each = 100 shares)
        So total shares = quantity * 100
        """
        if self.quantity <= 0:
            return self.premium  # Avoid division by zero
        
        # For options trades, each contract represents 100 shares
        total_shares = self.quantity * 100
        commission_per_share = self.commission / total_shares
        
        return self.premium - commission_per_share
    
    def total_net_premium(self) -> float:
        """Calculate total net premium for the entire trade after commission"""
        total_gross_premium = self.premium * self.quantity * 100  # Premium per share * total shares
        return total_gross_premium - self.commission
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.type,
            'strike': self.strike,
            'expiry': self.expiry,
            'premium': self.premium,
            'status': self.status,
            'entry_date': self.entry_date,
            'quantity': self.quantity,
            'commission': self.commission,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TradeEntry':
        """Create TradeEntry from dictionary"""
        return cls(**data)

@dataclass
class TickerPosition:
    """
    Represents an underwater stock position that needs recovery
    """
    ticker: str
    cost_basis: float
    qty: int
    purchase_date: str  # Format: 'YYYY-MM-DD'
    trades: List[TradeEntry] = field(default_factory=list)
    notes: str = ""
    target_recovery_price: Optional[float] = None
    
    def __post_init__(self):
        """Validate ticker position data"""
        if not self.ticker or not self.ticker.strip():
            raise ValueError("Ticker symbol cannot be empty")
        
        self.ticker = self.ticker.upper().strip()
        
        if self.cost_basis <= 0:
            raise ValueError("Cost basis must be positive")
        
        if self.qty <= 0:
            raise ValueError("Quantity must be positive")
        
        # Set default target recovery price to cost basis if not specified
        if self.target_recovery_price is None:
            self.target_recovery_price = self.cost_basis
    
    def total_investment(self) -> float:
        """Calculate total investment in this position"""
        return self.cost_basis * self.qty
    
    def add_trade(self, trade: TradeEntry) -> None:
        """Add a recovery trade to this position"""
        if not isinstance(trade, TradeEntry):
            raise ValueError("Trade must be a TradeEntry instance")
        self.trades.append(trade)
    
    def remove_trade(self, trade_index: int) -> bool:
        """Remove a trade by index"""
        if 0 <= trade_index < len(self.trades):
            self.trades.pop(trade_index)
            return True
        return False
    
    def get_active_trades(self) -> List[TradeEntry]:
        """Get all active trades for this position"""
        return [trade for trade in self.trades if trade.is_active()]
    
    def total_premium_collected(self) -> float:
        """Calculate total premium collected from all trades"""
        return sum(trade.net_premium() for trade in self.trades)
    
    def effective_cost_basis(self) -> float:
        """Calculate effective cost basis after premium collection"""
        total_premium = self.total_premium_collected()
        return max(0, self.cost_basis - (total_premium / self.qty))
    
    def unrealized_loss(self, current_price: float) -> float:
        """Calculate unrealized loss at current price"""
        if current_price >= self.cost_basis:
            return 0.0
        return (self.cost_basis - current_price) * self.qty
    
    def recovery_needed(self, current_price: float) -> float:
        """Calculate how much price needs to recover to break even"""
        effective_basis = self.effective_cost_basis()
        return max(0, effective_basis - current_price)
    
    def recovery_percentage_needed(self, current_price: float) -> float:
        """Calculate percentage recovery needed from current price"""
        if current_price <= 0:
            return float('inf')
        
        recovery_amount = self.recovery_needed(current_price)
        return (recovery_amount / current_price) * 100
    
    def is_underwater(self, current_price: float) -> bool:
        """Check if position is underwater"""
        return current_price < self.effective_cost_basis()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.ticker,
            'cost_basis': self.cost_basis,
            'qty': self.qty,
            'purchase_date': self.purchase_date,
            'trades': [trade.to_dict() for trade in self.trades],
            'notes': self.notes,
            'target_recovery_price': self.target_recovery_price
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TickerPosition':
        """Create TickerPosition from dictionary"""
        trades_data = data.pop('trades', [])
        position = cls(**data)
        position.trades = [TradeEntry.from_dict(trade_data) for trade_data in trades_data]
        return position

class PortfolioManager:
    """
    Manages a collection of underwater positions
    """
    def __init__(self):
        self.positions: List[TickerPosition] = []
    
    def add_position(self, position: TickerPosition) -> None:
        """Add a new position to the portfolio"""
        if not isinstance(position, TickerPosition):
            raise ValueError("Position must be a TickerPosition instance")
        
        # Check if ticker already exists
        existing = self.get_position(position.ticker)
        if existing:
            raise ValueError(f"Position for {position.ticker} already exists")
        
        self.positions.append(position)
    
    def remove_position(self, ticker: str) -> bool:
        """Remove a position by ticker"""
        ticker = ticker.upper().strip()
        for i, position in enumerate(self.positions):
            if position.ticker == ticker:
                self.positions.pop(i)
                return True
        return False
    
    def get_position(self, ticker: str) -> Optional[TickerPosition]:
        """Get position by ticker symbol"""
        ticker = ticker.upper().strip()
        for position in self.positions:
            if position.ticker == ticker:
                return position
        return None
    
    def get_all_tickers(self) -> List[str]:
        """Get list of all ticker symbols"""
        return [position.ticker for position in self.positions]
    
    def total_investment(self) -> float:
        """Calculate total investment across all positions"""
        return sum(position.total_investment() for position in self.positions)
    
    def total_premium_collected(self) -> float:
        """Calculate total premium collected across all positions"""
        return sum(position.total_premium_collected() for position in self.positions)
    
    def save_to_file(self, filename: str) -> None:
        """Save portfolio to JSON file"""
        data = {
            'positions': [position.to_dict() for position in self.positions],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """Load portfolio from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.positions = []
            for position_data in data.get('positions', []):
                position = TickerPosition.from_dict(position_data)
                self.positions.append(position)
        
        except FileNotFoundError:
            print(f"Portfolio file {filename} not found. Starting with empty portfolio.")
        except json.JSONDecodeError as e:
            print(f"Error loading portfolio file: {e}")
    
    def __len__(self) -> int:
        """Return number of positions"""
        return len(self.positions)
    
    def __iter__(self):
        """Make portfolio iterable"""
        return iter(self.positions)