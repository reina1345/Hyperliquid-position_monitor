# Hyperliquid Position Notifier Bot

This is a Discord bot that monitors Hyperliquid positions for specified addresses and sends notifications for:
- Position Open
- Position Close
- Periodic Status Report (every 1 hour)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Open `config.json`.
   - Set `"discord_token"` to your Discord Bot Token.
   - (Optional) Set `"channel_id"` if you want notifications to go to a specific channel automatically. Otherwise, you might need to configure the bot to use the channel where commands are issued (implementation detail).
   - You can manually add addresses to `"addresses"` list or use the Discord commands.

3. **Run the Bot**
   ```bash
   python bot.py
   ```

## Commands

- `!add <address>`: Add an address to monitor.
- `!remove <address>`: Remove an address from monitoring.
- `!list`: List all monitored addresses.
- `!status`: Force a status report immediately.
