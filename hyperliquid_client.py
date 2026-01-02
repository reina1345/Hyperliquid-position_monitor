import aiohttp
import asyncio
import json

API_URL = "https://api.hyperliquid.xyz/info"

async def get_user_state(address: str):
    """
    Fetches the clearinghouse state for a user.
    """
    payload = {
        "type": "clearinghouseState",
        "user": address
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Error fetching data for {address}: {response.status}")
                    return None
        except Exception as e:
            print(f"Exception fetching data for {address}: {e}")
            return None
