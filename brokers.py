import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Broker:
    def __init__(self, broker_type: str, username: str, password: str, domain: str = "default"):
        self.broker_type = broker_type.lower()
        self.username = username
        self.password = password
        self.domain = domain
        self.account_id = f"{domain}:{username}" if domain != "default" else username
        self.session = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        self.session_token: Optional[str] = None
        
        # Set base URLs based on broker type
        if self.broker_type == "dxtrade":
            self.base_url = "https://trade.gooeytrade.com"  # The Funded Trader
        elif self.broker_type == "matchtrade":
            self.base_url = "https://mtr.voyagemarkets.net"  # Funded Trading Plus
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")

    async def login(self) -> bool:
        """Login to the broker and store session token."""
        try:
            if self.broker_type == "dxtrade":
                login_url = f"{self.base_url}/dxsca-web/login"
                logger.info(f"Attempting login to DXTrade with URL: {login_url}")
                
                login_data = {
                    "username": self.username,
                    "password": self.password,
                    "domain": self.domain
                }
                
                response = await self.session.post(login_url, json=login_data)
                logger.info(f"DXTrade Login Response Status: {response.status_code}")
                logger.info(f"DXTrade Login Response Headers: {response.headers}")
                logger.info(f"DXTrade Login Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    # Try different possible token field names
                    self.session_token = (
                        data.get("sessionToken") or 
                        data.get("token") or 
                        data.get("access_token")
                    )
                    
                    if not self.session_token:
                        # Try to get token from cookies
                        cookies = response.cookies
                        if "JSESSIONID" in cookies:
                            self.session_token = cookies["JSESSIONID"]
                    
                    if self.session_token:
                        # Update client headers with session token
                        self.session.headers.update({
                            "Authorization": f"DXAPI {self.session_token}",
                            "X-Session-Token": self.session_token,
                            "Cookie": f"JSESSIONID={self.session_token}"
                        })
                        logger.info("DXTrade login successful")
                        return True
                    else:
                        logger.error("No session token found in response")
                        return False
                else:
                    logger.error(f"Login failed with status code: {response.status_code}")
                    return False
                
            elif self.broker_type == "matchtrade":
                # Manually format raw query string with unescaped '+'
                raw_email = self.username
                login_url = f"{self.base_url}/manager/login-v2?partnerId=1&email={raw_email}"

                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded"
                    }

                form_data = {
                "password": self.password
                            }

                response = await self.session.post(login_url, data=form_data, headers=headers)

                logger.info(f"MatchTrade Login Response Status: {response.status_code}")
                logger.info(f"MatchTrade Login Response Body: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get("accounts", [])
                    if not accounts:
                        logger.error("No accounts found in response")
                        return False

                    account = accounts[0]
                    self.trading_api_token = account.get("tradingApiToken")
                    self.system_uuid = account.get("offer", {}).get("system", {}).get("uuid")
                    self.session_token = response.cookies.get("co-auth")

                    if self.trading_api_token and self.system_uuid and self.session_token:
                        self.session.headers.update({
                            "Auth-trading-api": self.trading_api_token,
                            "Cookie": f"co-auth={self.session_token}"
                        })
                        logger.info("MatchTrade login successful")
                        return True

            logger.error(f"Login failed with status code: {response.status_code}")
            return False

        except httpx.HTTPError as e:
            logger.error(f"Login failed: {str(e)}")
            return False


            
        except httpx.HTTPError as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        if not self.session_token:
            logger.error("Not logged in. Please login first.")
            return {"error": "Not logged in"}

        try:
            if self.broker_type == "dxtrade":
                # Use only the working endpoint
                metrics_url = f"{self.base_url}/dxsca-web/accounts/metrics"
                logger.info(f"Fetching DXTrade balance from: {metrics_url}")
                
                response = await self.session.get(
                    metrics_url,
                    headers={
                        "Authorization": f"DXAPI {self.session_token}",
                        "X-Session-Token": self.session_token,
                        "X-Requested-With": "XMLHttpRequest",
                        "Cookie": f"JSESSIONID={self.session_token}"
                    }
                )
                logger.info(f"DXTrade Balance Response Status: {response.status_code}")
                logger.info(f"DXTrade Balance Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    metrics = data.get("metrics", [])
                    if metrics:
                        metric = metrics[0]
                        return {
                            "total_balance": float(metric.get("balance", 0)),
                            "available_balance": float(metric.get("availableBalance", 0)),
                            "currency_balances": [{
                                "currency": "USD",
                                "value": float(metric.get("balance", 0)),
                                "available": float(metric.get("availableBalance", 0))
                            }]
                        }
                
                logger.error("Failed to get balance")
                return {"error": "Failed to get balance"}
                
            elif self.broker_type == "matchtrade":
                if not hasattr(self, 'system_uuid'):
                    logger.error("System UUID not found. Please login first.")
                    return {"error": "System UUID not found"}
                    
                balance_url = f"{self.base_url}/mtr-api/{self.system_uuid}/balance"
                logger.info(f"Fetching MatchTrade balance from: {balance_url}")
                
                response = await self.session.get(
                    balance_url,
                    headers={
                        "Auth-trading-api": self.trading_api_token,
                        "Cookie": f"co-auth={self.session_token}"
                    }
                )
                
                logger.info(f"MatchTrade Balance Response Status: {response.status_code}")
                logger.info(f"MatchTrade Balance Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "total_balance": float(data.get("balance", 0)),
                        "available_balance": float(data.get("freeMargin", 0)),
                        "currency_balances": [{
                            "currency": data.get("currency", "USD"),
                            "value": float(data.get("balance", 0)),
                            "available": float(data.get("freeMargin", 0))
                        }]
                    }
                else:
                    logger.error(f"Failed to get balance with status code: {response.status_code}")
                    return {"error": f"Failed to get balance: {response.text}"}
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch balance: {str(e)}")
            return {"error": str(e)} 