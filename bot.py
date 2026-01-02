import discord
from discord.ext import commands, tasks
import os
import storage
from hyperliquid_client import get_user_state

# Intents are required for reading message content and members in newer Discord API
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store previous states of positions: { address: { coin: { ...position_data... } } }
previous_states = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    if not monitor_positions.is_running():
        monitor_positions.start()
    if not periodic_report.is_running():
        periodic_report.start()

@bot.command()
async def set_channel(ctx):
    """Sets the current channel as the notification channel."""
    storage.set_channel_id(ctx.channel.id)
    await ctx.send(f"Notification channel set to {ctx.channel.mention}")

@bot.command()
async def add(ctx, address: str):
    """Adds an address to the monitoring list."""
    if storage.add_address(address):
        await ctx.send(f"Added address: {address}")
    else:
        await ctx.send(f"Address already in list: {address}")

@bot.command()
async def remove(ctx, address: str):
    """Removes an address from the monitoring list."""
    if storage.remove_address(address):
        await ctx.send(f"Removed address: {address}")
    else:
        await ctx.send(f"Address not found in list: {address}")

@bot.command(name="list")
async def list_addresses(ctx):
    """Lists all monitored addresses."""
    addresses = storage.get_addresses()
    if addresses:
        msg = "Monitored Addresses:\n" + "\n".join(addresses)
        await ctx.send(msg)
    else:
        await ctx.send("No addresses are currently being monitored.")

@bot.command()
async def status(ctx):
    """Force a status report immediately."""
    await send_status_report(ctx.channel)

async def send_status_report(channel):
    addresses = storage.get_addresses()
    if not addresses:
        await channel.send("No addresses monitored.")
        return

    report_msg = "**📊 Periodic Position Report**\n"

    for address in addresses:
        try:
            data = await get_user_state(address)
            if not data:
                report_msg += f"\nFailed to fetch for `{address[:6]}...`"
                continue

            current_positions_list = data.get('assetPositions', [])

            if not current_positions_list:
                report_msg += f"\n`{address[:6]}...{address[-4:]}`: No open positions."
            else:
                report_msg += f"\n`{address[:6]}...{address[-4:]}`:"
                for pos in current_positions_list:
                    p = pos.get('position', {})
                    coin = p.get('coin')
                    size = p.get('szi')
                    entry = p.get('entryPx')
                    pnl = p.get('unrealizedPnl')
                    side = "LONG" if float(size) > 0 else "SHORT"
                    report_msg += f"\n  - **{side}** {coin} | Sz: {size} | Ep: {entry} | PnL: {pnl}"
        except Exception as e:
            report_msg += f"\nError fetching `{address[:6]}...`: {e}"

    await channel.send(report_msg)

@tasks.loop(hours=1)
async def periodic_report():
    channel_id = storage.get_channel_id()
    if channel_id == 0:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        await send_status_report(channel)

@periodic_report.before_loop
async def before_periodic():
    await bot.wait_until_ready()

@tasks.loop(minutes=1)
async def monitor_positions():
    channel_id = storage.get_channel_id()
    if channel_id == 0:
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        return

    addresses = storage.get_addresses()
    for address in addresses:
        try:
            data = await get_user_state(address)
            if not data:
                continue

            # Parse current positions into a dict: coin -> position_data
            current_positions_list = data.get('assetPositions', [])
            current_positions = {}
            for pos in current_positions_list:
                p = pos.get('position', {})
                coin = p.get('coin')
                if coin:
                    current_positions[coin] = p

            # If this is the first time we see this address, just initialize state
            if address not in previous_states:
                previous_states[address] = current_positions
                continue

            prev_positions = previous_states[address]

            # Check for Opened Positions (in current but not in prev) OR Flips
            for coin, pos_data in current_positions.items():
                size = pos_data.get('szi')
                entry = pos_data.get('entryPx')
                side = "LONG" if float(size) > 0 else "SHORT"

                if coin not in prev_positions:
                    # Brand new position
                    await channel.send(
                        f"🚨 **OPENED** - Address: `{address[:6]}...{address[-4:]}`\n"
                        f"**{side}** {coin} | Size: {size} | Entry: {entry}"
                    )
                else:
                    # Check for Flip (sign change)
                    prev_size = prev_positions[coin].get('szi')
                    if (float(size) > 0 and float(prev_size) < 0) or (float(size) < 0 and float(prev_size) > 0):
                        prev_side = "LONG" if float(prev_size) > 0 else "SHORT"
                        await channel.send(
                            f"🔄 **FLIPPED** - Address: `{address[:6]}...{address[-4:]}`\n"
                            f"Was **{prev_side}**, Now **{side}** {coin} | Size: {size} | Entry: {entry}"
                        )

            # Check for Closed Positions (in prev but not in current)
            for coin, pos_data in prev_positions.items():
                if coin not in current_positions:
                    size = pos_data.get('szi')
                    entry = pos_data.get('entryPx')
                    side = "LONG" if float(size) > 0 else "SHORT"
                    await channel.send(
                        f"✅ **CLOSED** - Address: `{address[:6]}...{address[-4:]}`\n"
                        f"**{side}** {coin} | (Was Size: {size}, Entry: {entry})"
                    )

            # Update state
            previous_states[address] = current_positions

        except Exception as e:
            print(f"Error in monitor loop for {address}: {e}")

@monitor_positions.before_loop
async def before_monitor():
    await bot.wait_until_ready()

if __name__ == "__main__":
    token = storage.get_discord_token()
    if not token or token == "YOUR_DISCORD_TOKEN_HERE":
        print("Please set your Discord Bot Token in config.json")
    else:
        bot.run(token)
