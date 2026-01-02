import asyncio
import aiohttp
import storage
from hyperliquid_client import get_user_state
import datetime

# Store previous states: { address: { coin: { ...position_data... } } }
previous_states = {}

async def send_discord_message(content: str):
    webhook_url = storage.get_webhook_url()
    if not webhook_url:
        print("No Webhook URL configured.")
        return

    payload = {"content": content}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=payload) as response:
                if response.status not in [200, 204]:
                    print(f"Failed to send webhook: {response.status}")
        except Exception as e:
            print(f"Error sending webhook: {e}")

async def monitor_positions_loop():
    print("Starting position monitor loop...")
    while True:
        addresses = storage.get_addresses()
        for address in addresses:
            try:
                data = await get_user_state(address)
                if not data:
                    continue

                # Parse current positions
                current_positions_list = data.get('assetPositions', [])
                current_positions = {}
                for pos in current_positions_list:
                    p = pos.get('position', {})
                    coin = p.get('coin')
                    if coin:
                        current_positions[coin] = p

                # Initialize state if new address
                if address not in previous_states:
                    previous_states[address] = current_positions
                    continue

                prev_positions = previous_states[address]

                # Check for Opened Positions OR Flips
                for coin, pos_data in current_positions.items():
                    size = pos_data.get('szi')
                    entry = pos_data.get('entryPx')
                    side = "LONG" if float(size) > 0 else "SHORT"

                    if coin not in prev_positions:
                        # Brand new position
                        await send_discord_message(
                            f"🚨 **OPENED** - Address: `{address[:6]}...{address[-4:]}`\n"
                            f"**{side}** {coin} | Size: {size} | Entry: {entry}"
                        )
                    else:
                        # Check for Flip
                        prev_size = prev_positions[coin].get('szi')
                        if (float(size) > 0 and float(prev_size) < 0) or (float(size) < 0 and float(prev_size) > 0):
                            prev_side = "LONG" if float(prev_size) > 0 else "SHORT"
                            await send_discord_message(
                                f"🔄 **FLIPPED** - Address: `{address[:6]}...{address[-4:]}`\n"
                                f"Was **{prev_side}**, Now **{side}** {coin} | Size: {size} | Entry: {entry}"
                            )

                # Check for Closed Positions
                for coin, pos_data in prev_positions.items():
                    if coin not in current_positions:
                        size = pos_data.get('szi')
                        entry = pos_data.get('entryPx')
                        side = "LONG" if float(size) > 0 else "SHORT"
                        await send_discord_message(
                            f"✅ **CLOSED** - Address: `{address[:6]}...{address[-4:]}`\n"
                            f"**{side}** {coin} | (Was Size: {size}, Entry: {entry})"
                        )

                # Update state
                previous_states[address] = current_positions

            except Exception as e:
                print(f"Error in monitor loop for {address}: {e}")

        await asyncio.sleep(60)

async def periodic_report_loop():
    print("Starting periodic report loop...")
    while True:
        # Wait for 1 hour, but execute immediately on first run?
        # Requirement was "periodic status report". Let's run it once then wait.
        # To avoid spamming on restart, let's wait first or align to clock.
        # Simple approach: Wait 1 hour.
        await asyncio.sleep(3600)

        addresses = storage.get_addresses()
        if not addresses:
            continue

        report_msg = "**📊 Periodic Position Report**\n"
        has_data = False

        for address in addresses:
            try:
                data = await get_user_state(address)
                if not data:
                    continue

                current_positions_list = data.get('assetPositions', [])
                if current_positions_list:
                    has_data = True
                    report_msg += f"\n`{address[:6]}...{address[-4:]}`:"
                    for pos in current_positions_list:
                        p = pos.get('position', {})
                        coin = p.get('coin')
                        size = p.get('szi')
                        entry = p.get('entryPx')
                        pnl = p.get('unrealizedPnl')
                        side = "LONG" if float(size) > 0 else "SHORT"
                        report_msg += f"\n  - **{side}** {coin} | Sz: {size} | Ep: {entry} | PnL: {pnl}"
                else:
                    report_msg += f"\n`{address[:6]}...{address[-4:]}`: No open positions."

            except Exception as e:
                print(f"Error in report loop for {address}: {e}")

        if has_data or addresses:
            await send_discord_message(report_msg)

async def main():
    await asyncio.gather(
        monitor_positions_loop(),
        periodic_report_loop()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
