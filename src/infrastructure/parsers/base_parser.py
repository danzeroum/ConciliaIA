"""Base class for EDI parsers."""

from abc import ABC, abstractmethod
from typing import List
from src.domain.entities import AcquirerTransaction


class BaseEDIParser(ABC):
    """Abstract base parser for acquirer EDI files."""
    
    @abstractmethod
    def parse(self, content: str, tenant_id: str) -> List[AcquirerTransaction]:
        """
        Parse EDI content and return list of transactions.
        
        Args:
            content: Raw EDI file content
            tenant_id: Tenant identifier
            
        Returns:
            List of AcquirerTransaction entities
            
        Raises:
            ValueError: If content is invalid or cannot be parsed
        """
        pass
    
    @abstractmethod
    def validate(self, content: str) -> bool:
        """
        Validate EDI file structure.
        
        Args:
            content: Raw EDI file content
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @staticmethod
    def parse_date(date_str: str, format_type: str = "DDMMYYYY") -> str:
        """
        Convert date string to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to parse
            format_type: Format of input date
            
        Returns:
            Date in ISO format
        """
        from datetime import datetime
        
        if format_type == "DDMMYYYY" and len(date_str) == 8:
            day = date_str[:2]
            month = date_str[2:4]
            year = date_str[4:8]
            return f"{year}-{month}-{day}"
        
        return datetime.now().strftime("%Y-%m-%d")  # fallback
    
    @staticmethod
    def parse_amount(amount_str: str, is_cents: bool = True) -> float:
        """
        Convert amount string to float.
        
        Args:
            amount_str: Amount string (may include decimals or cents)
            is_cents: If True, divide by 100
            
        Returns:
            Amount as float
        """
        try:
            amount = float(amount_str.strip())
            return amount / 100 if is_cents else amount
        except (ValueError, AttributeError):
            return 0.0
