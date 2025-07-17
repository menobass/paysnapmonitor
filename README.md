# Pay n Snap Hive Cashback Bot

## Overview
A Python bot for monitoring Hive blockchain payments, processing cashback rewards, and providing an admin dashboard for Pay n Snap.

## Features
- Monitors Hive payments using hivelite
- Processes cashback based on purchase count/rates
- Admin dashboard (FastAPI + Jinja2)
- SQLite for local storage
- Configurable via config.yaml and .env
- Robust logging, error handling, and security

## Setup (Ubuntu)
1. Clone repo and enter folder
2. Create and activate virtualenv
3. Copy `.env.template` to `.env` and fill secrets
4. Copy `config.yaml.template` to `config.yaml` and configure
5. Install dependencies: `pip install -r requirements.txt`
6. Run bot: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Access dashboard at `http://localhost:8000/admin`

## Systemd Service
See `paynsnapbot.service.template` for running as a service.

## Security
- All secrets in `.env`, never in source
- Admin passwords hashed
- Regular DB/config backups recommended

## Testing & Quality
- Run tests: `pytest`
- Lint/format: `black . && flake8 . && mypy .`

## Extensibility
- Modular codebase for future features

## Support
For issues, contact @meno on hive
