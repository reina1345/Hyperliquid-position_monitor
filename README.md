# Hyperliquid Position Notifier Bot (Webhook Version)

This is a script that monitors Hyperliquid positions for specified addresses and sends notifications via a Discord Webhook for:
- Position Open
- Position Close / Flip
- Periodic Status Report (every 1 hour)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Open `config.json`.
   - Set `"webhook_url"` to your Discord Webhook URL.
   - Add the addresses you want to monitor to the `"addresses"` list manually.
     ```json
     {
         "addresses": [
             "0xF59079E159130dA804ac3b2ea2D24c9d683AEc2A",
             "0xANOTHER_ADDRESS"
         ],
         "webhook_url": "https://discord.com/api/webhooks/..."
     }
     ```

3. **Run the Monitor**
   ```bash
   python monitor.py
   ```

## Features

- **Real-time Monitoring**: Checks positions every 1 minute.
- **Notifications**:
  - 🚨 **OPENED**: New position detected.
  - ✅ **CLOSED**: Position closed.
  - 🔄 **FLIPPED**: Position flipped (e.g., Long to Short).
- **Periodic Report**: Sends a summary of all open positions every hour.
