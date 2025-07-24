# Pay n Snap Hive Cashback Bot

## Overview
A Python bot for monitoring Hive blockchain payments, processing cashback rewards, and providing an admin dashboard for Pay n Snap. The bot automatically sends cashback to customers and provides store beneficiaries on reply comments.

## Features
- **Blockchain Monitoring**: Monitors Hive payments using lighthive
- **Cashback Processing**: Processes cashback based on purchase count/rates
- **Store Beneficiaries**: Automatically sets 10% beneficiaries to stores on bot reply comments
- **Discord Integration**: Real-time notifications via Discord webhooks
- **Admin Dashboard**: FastAPI + Jinja2 web interface for transaction monitoring
- **Database**: SQLite for local storage with comprehensive transaction tracking
- **Configuration**: Configurable via config.yaml and .env files
- **Security**: Robust logging, error handling, and security features

## New Features (Latest Update)
- 🎯 **Store Beneficiary System**: Reply comments now include 10% beneficiaries to stores
- 💬 **Discord Webhooks**: Real-time notifications for payments, cashbacks, and errors
- 📊 **Enhanced Dashboard**: Shows all transactions (not just first per user)
- 🔒 **Improved Security**: Better error handling and fallback mechanisms

## Setup Instructions

### Prerequisites
- Python 3.8+
- Hive account with posting/active keys
- Discord server (optional, for notifications)

### Installation (Ubuntu/Linux)
1. **Clone repository**
   ```bash
   git clone https://github.com/menobass/paysnapmonitor.git
   cd paysnapmonitor
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your Hive keys and Discord webhook
   ```

5. **Configure bot settings**
   ```bash
   cp config.yaml.template config.yaml
   # Edit config.yaml with your stores and settings
   ```

6. **Run the bot**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

7. **Access dashboard**
   Open `http://localhost:8000/` in your browser

## Configuration

### .env File
```properties
HIVE_POSTING_KEY=your_posting_key_here
HIVE_ACTIVE_KEY=your_active_key_here
ADMIN_PASSWORD_HASH=bcrypt_hash_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
EMAIL_ALERTS=your@email.com
HIVE_USERNAME=your_bot_account
```

### Discord Setup (Optional)
1. Create a Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Create webhook and copy URL to .env file
4. Bot will send real-time notifications for all payment events

## Production Deployment

### Systemd Service
Use the provided template:
```bash
sudo cp paynsnapbot.service.template /etc/systemd/system/paynsnapbot.service
# Edit the service file with your paths
sudo systemctl enable paynsnapbot
sudo systemctl start paynsnapbot
```

### Monitoring
- Check logs: `sudo journalctl -u paynsnapbot -f`
- View dashboard: `http://your-server:8000/`
- Monitor Discord channel for real-time updates

## How It Works

1. **Payment Detection**: Bot monitors blockchain for payments to configured stores
2. **Snap Validation**: Waits for user to post a snap with correct beneficiaries
3. **Cashback Processing**: Calculates and sends HBD cashback to customer
4. **Store Benefits**: Reply comment includes 10% beneficiary to the store
5. **Notifications**: Discord alerts for all events (success, failures, timeouts)

## Store Benefits
- Customers get cashback (incentive to use HBD)
- Stores get 10% of post rewards from bot replies (incentive to accept HBD)
- Win-win ecosystem encouraging HBD adoption

## Development & Testing

### Run Tests
```bash
pytest
```

### Code Quality
```bash
black .           # Format code
flake8 .          # Lint code  
mypy .            # Type checking
```

### Available Tasks (VS Code)
- **Run Bot**: Start the bot with uvicorn
- **Run Tests**: Execute pytest suite
- **Lint & Type Check**: Run quality checks

## Database Schema
- `users`: User purchase history and limits
- `payment_events`: All transaction records with outcomes
- `processed_ops`: Blockchain operations tracking
- `bans`: User ban management
- `stores`: Store configuration

## Security Features
- All secrets stored in `.env` (never in source code)
- Admin passwords use bcrypt hashing
- Safe fallback mechanisms for failed operations
- Comprehensive logging for audit trails

## Troubleshooting
- **Bot not starting**: Check Hive keys in .env file
- **No Discord notifications**: Verify webhook URL format
- **Database issues**: Check file permissions and disk space
- **Payment not processing**: Verify store configuration in config.yaml

## Support & Contributing
- **Issues**: Create GitHub issues for bugs/features
- **Contact**: @meno on Hive blockchain
- **Contributions**: Pull requests welcome

## License
This project is open source. Use responsibly and contribute back to the community!
