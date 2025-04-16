# Broker API Integration
pip install -r requirements.txt
This project provides a unified interface for interacting with multiple trading platforms (DXTrade and MatchTrade). It includes implementations for login and balance retrieval functionalities.

## Project Structure

```
.
├── brokers.py          # Core broker integration logic
├── example.py          # Example usage of the broker classes
└── README.md          # This documentation file
```

## Implementation Details

### brokers.py

The `brokers.py` file contains the core broker integration logic. It defines a `Broker` class that handles authentication and balance retrieval for different trading platforms.

#### Key Components:

1. **Broker Class Initialization**
   ```python
   def __init__(self, broker_type: str, username: str, password: str, domain: str = "default"):
   ```
   - `broker_type`: Specifies the trading platform ("dxtrade" or "matchtrade")
   - `username`: Trading account username
   - `password`: Trading account password
   - `domain`: Optional domain parameter (default: "default")

2. **Login Method**
   ```python
   async def login(self) -> bool:
   ```
   - Handles platform-specific authentication
   - Stores session tokens and API keys
   - Returns True on successful login, False otherwise

3. **Balance Retrieval Method**
   ```python
   async def get_balance(self) -> Dict[str, Any]:
   ```
   - Retrieves account balance information
   - Returns a dictionary with total balance, available balance, and currency details

#### DXTrade Implementation

- **Login Flow**:
  1. Sends POST request to `/dxsca-web/login`
  2. Extracts session token from response
  3. Updates client headers with authentication tokens

- **Balance Retrieval**:
  1. Sends GET request to `/dxsca-web/accounts/metrics`
  2. Processes response to extract balance information
  3. Returns structured balance data

#### MatchTrade Implementation

- **Login Flow**:
  1. Sends POST request to `/manager/co-login`
  2. Extracts trading API token and system UUID
  3. Updates client headers with authentication tokens

- **Balance Retrieval**:
  1. Sends GET request to `/mtr-api/{system_uuid}/balance`
  2. Processes response to extract balance information
  3. Returns structured balance data

### example.py

The `example.py` file demonstrates how to use the `Broker` class to interact with different trading platforms.

#### Key Components:

1. **Test Broker Function**
   ```python
   async def test_broker(broker_type: str, username: str, password: str):
   ```
   - Tests login and balance retrieval for a specific broker
   - Logs the results of each operation
   - Properly closes HTTP sessions after completion

2. **Main Function**
   ```python
   async def main():
   ```
   - Tests broker implementations
   - Uses actual credentials for testing
   - Handles proper cleanup of resources

## Usage

### Running the Example

```bash
python example.py
```

This will test the broker implementations with the configured credentials.

## Error Handling

The implementation includes comprehensive error handling:

1. **Login Errors**:
   - Invalid credentials
   - Account locked
   - Network issues
   - Server errors

2. **Balance Retrieval Errors**:
   - Session expired
   - Network issues
   - Server errors

## Logging

The code uses Python's logging module to provide detailed information about:
- Login attempts
- API requests and responses
- Error conditions
- Balance retrieval operations

## Dependencies

- httpx
- asyncio
- logging

## Notes

1. The DXTrade implementation is fully functional and tested.
2. The MatchTrade implementation requires additional configuration:
   - Correct broker ID
   - OAuth configuration (if required)
   - System UUID for balance retrieval

## Future Improvements

1. Add support for more trading platforms
2. Implement additional trading operations
3. Add rate limiting and request throttling
4. Implement session cleanup for expired tokens
5. Add more comprehensive error handling
6. Implement retry mechanisms for failed requests 