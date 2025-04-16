import asyncio
from brokers import Broker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_broker(broker_type: str, username: str, password: str):
    """Test broker login and balance retrieval."""
    broker = None
    try:
        # Initialize broker
        broker = Broker(broker_type, username, password)
        logger.info(f"Testing {broker_type} broker...")
        
        # Test login
        if await broker.login():
            logger.info(f"{broker_type} login successful")
            
            # Test balance retrieval
            balance = await broker.get_balance()
            if "error" not in balance:
                logger.info(f"{broker_type} balance: {balance}")
            else:
                logger.error(f"Failed to get {broker_type} balance: {balance['error']}")
        else:
            logger.error(f"{broker_type} login failed")
            
    except Exception as e:
        logger.error(f"An error occurred with {broker_type}: {str(e)}")
    finally:
        # Always close the broker session
        if broker and broker.session:
            await broker.session.aclose()

async def main():
    # Test DXTrade (The Funded Trader)
    await test_broker(
        "dxtrade",
        "FTP_C97086",
        "b7F-San67"
    )
    
    # Test MatchTrade (Funded Trading Plus)
    # await test_broker(
    #     broker_type="matchtrade",
    #     username="dparkmit+TFT@gmail.com",
    #     password="y7J=euUP6",  # ✅ Correct password
    # )

if __name__ == "__main__":
    asyncio.run(main()) 