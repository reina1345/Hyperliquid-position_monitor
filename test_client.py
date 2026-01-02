import asyncio
from hyperliquid_client import get_user_state

async def main():
    sample_address = "0xF59079E159130dA804ac3b2ea2D24c9d683AEc2A"
    print(f"Fetching data for {sample_address}...")
    data = await get_user_state(sample_address)

    if data:
        print("Successfully fetched data:")
        print(f"Margin Summary: {data.get('marginSummary', 'N/A')}")
        positions = data.get('assetPositions', [])
        print(f"Open Positions: {len(positions)}")
        for pos in positions:
            p_data = pos.get('position', {})
            print(f"- {p_data.get('coin')}: Size {p_data.get('szi')}, Entry {p_data.get('entryPx')}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    asyncio.run(main())
