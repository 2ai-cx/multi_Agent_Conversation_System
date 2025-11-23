"""
Tenant Key Manager

Manages OpenRouter API keys per tenant for:
- Isolated rate limiting and cost tracking
- Per-tenant credit limits
- Usage monitoring
- Key lifecycle management
"""

import httpx
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TenantKeyInfo:
    """Information about a tenant's OpenRouter API key"""
    tenant_id: str
    api_key: str
    key_hash: str
    credit_limit: float
    limit_reset: str  # 'daily', 'weekly', 'monthly'
    created_at: datetime
    disabled: bool = False


@dataclass
class TenantUsage:
    """Usage statistics for a tenant"""
    tenant_id: str
    usage_daily: float
    usage_weekly: float
    usage_monthly: float
    limit_remaining: float
    last_updated: datetime


class TenantKeyManager:
    """
    Manage OpenRouter API keys per tenant
    
    Features:
    - Create unique API key per tenant
    - Cache keys in memory (avoid repeated API calls)
    - Track usage per tenant
    - Disable/enable keys
    - Support key rotation
    
    Usage:
        manager = TenantKeyManager(provisioning_key)
        
        # Get or create key for tenant
        api_key = await manager.get_or_create_key("tenant-123")
        
        # Check usage
        usage = await manager.get_usage("tenant-123")
        
        # Disable key
        await manager.disable_key("tenant-123")
    """
    
    def __init__(
        self,
        provisioning_key: str,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize tenant key manager
        
        Args:
            provisioning_key: OpenRouter provisioning API key
            base_url: OpenRouter API base URL
        """
        self.provisioning_key = provisioning_key
        self.base_url = base_url
        
        # In-memory cache: tenant_id -> TenantKeyInfo
        self.key_cache: Dict[str, TenantKeyInfo] = {}
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
    
    async def get_or_create_key(
        self,
        tenant_id: str,
        credit_limit: float = 1000.0,
        limit_reset: str = "daily"
    ) -> str:
        """
        Get existing key or create new one for tenant
        
        Args:
            tenant_id: Unique tenant identifier
            credit_limit: Daily/weekly/monthly credit limit in USD
            limit_reset: Reset period ('daily', 'weekly', 'monthly')
        
        Returns:
            OpenRouter API key for tenant
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        # Check cache first
        if tenant_id in self.key_cache:
            key_info = self.key_cache[tenant_id]
            if not key_info.disabled:
                self.logger.debug(f"Using cached key for tenant {tenant_id}")
                return key_info.api_key
        
        # Create new key via OpenRouter Provisioning API
        self.logger.info(f"Creating new OpenRouter key for tenant {tenant_id}")
        
        headers = {
            "Authorization": f"Bearer {self.provisioning_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": f"Tenant-{tenant_id}",
            "limit": credit_limit,
            "limitReset": limit_reset
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/keys",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Failed to create tenant key: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"Request error creating tenant key: {str(e)}")
                raise
        
        # Extract key data
        api_key = data.get("label") or data.get("key")
        key_hash = data.get("hash") or data.get("id")
        
        if not api_key:
            raise ValueError(f"OpenRouter API did not return key: {data}")
        
        # Cache key info
        key_info = TenantKeyInfo(
            tenant_id=tenant_id,
            api_key=api_key,
            key_hash=key_hash,
            credit_limit=credit_limit,
            limit_reset=limit_reset,
            created_at=datetime.utcnow(),
            disabled=False
        )
        self.key_cache[tenant_id] = key_info
        
        self.logger.info(f"Created OpenRouter key for tenant {tenant_id} (hash: {key_hash})")
        return api_key
    
    async def get_usage(self, tenant_id: str) -> Optional[TenantUsage]:
        """
        Get usage statistics for tenant
        
        Args:
            tenant_id: Tenant identifier
        
        Returns:
            TenantUsage with current usage stats, or None if not found
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        # Get key info from cache
        key_info = self.key_cache.get(tenant_id)
        if not key_info:
            self.logger.warning(f"No key found for tenant {tenant_id}")
            return None
        
        # Query OpenRouter API for usage
        headers = {
            "Authorization": f"Bearer {self.provisioning_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/keys/{key_info.key_hash}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Failed to get usage for tenant {tenant_id}: {e.response.status_code}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"Request error getting usage: {str(e)}")
                raise
        
        # Extract usage data
        usage_data = data.get("data", {})
        
        return TenantUsage(
            tenant_id=tenant_id,
            usage_daily=float(usage_data.get("usage_daily", 0.0)),
            usage_weekly=float(usage_data.get("usage_weekly", 0.0)),
            usage_monthly=float(usage_data.get("usage_monthly", 0.0)),
            limit_remaining=float(usage_data.get("limit_remaining", 0.0)),
            last_updated=datetime.utcnow()
        )
    
    async def disable_key(self, tenant_id: str):
        """
        Disable key for tenant
        
        Use this to temporarily block a tenant (e.g., non-payment)
        
        Args:
            tenant_id: Tenant identifier
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        key_info = self.key_cache.get(tenant_id)
        if not key_info:
            self.logger.warning(f"No key found for tenant {tenant_id}")
            return
        
        # Update key via OpenRouter API
        headers = {
            "Authorization": f"Bearer {self.provisioning_key}",
            "Content-Type": "application/json"
        }
        
        payload = {"disabled": True}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/keys/{key_info.key_hash}",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Failed to disable key for tenant {tenant_id}: {e.response.status_code}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"Request error disabling key: {str(e)}")
                raise
        
        # Update cache
        key_info.disabled = True
        self.logger.info(f"Disabled OpenRouter key for tenant {tenant_id}")
    
    async def enable_key(self, tenant_id: str):
        """
        Enable previously disabled key for tenant
        
        Args:
            tenant_id: Tenant identifier
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        key_info = self.key_cache.get(tenant_id)
        if not key_info:
            self.logger.warning(f"No key found for tenant {tenant_id}")
            return
        
        # Update key via OpenRouter API
        headers = {
            "Authorization": f"Bearer {self.provisioning_key}",
            "Content-Type": "application/json"
        }
        
        payload = {"disabled": False}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/keys/{key_info.key_hash}",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"Failed to enable key for tenant {tenant_id}: {e.response.status_code}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"Request error enabling key: {str(e)}")
                raise
        
        # Update cache
        key_info.disabled = False
        self.logger.info(f"Enabled OpenRouter key for tenant {tenant_id}")
    
    def get_cached_key_info(self, tenant_id: str) -> Optional[TenantKeyInfo]:
        """
        Get cached key info for tenant (no API call)
        
        Args:
            tenant_id: Tenant identifier
        
        Returns:
            TenantKeyInfo if cached, None otherwise
        """
        return self.key_cache.get(tenant_id)
    
    def clear_cache(self, tenant_id: Optional[str] = None):
        """
        Clear key cache
        
        Args:
            tenant_id: Specific tenant to clear, or None to clear all
        """
        if tenant_id:
            if tenant_id in self.key_cache:
                del self.key_cache[tenant_id]
                self.logger.debug(f"Cleared cache for tenant {tenant_id}")
        else:
            self.key_cache.clear()
            self.logger.debug("Cleared all tenant key cache")
