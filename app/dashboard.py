import os
import json
import time
import requests
import secrets
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from app.db import db
from app.config import config

router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))


def get_admin():
    # Placeholder for admin authentication
    pass


def _discord_notify(title: str, description: str, color: int = 0x3399FF):
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        return
    try:
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        }
        payload = {"username": "PaySnap Bot", "embeds": [embed]}
        requests.post(
            url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except Exception:
        # Fail silently for admin UX; logs are handled elsewhere
        pass


def _latest_transactions(limit: int = 20):
    cursor = db.conn.cursor()
    cursor.execute(
        """
        SELECT username, amount, memo, paid, reason, timestamp, snap_permlink 
        FROM payment_events 
        WHERE paid = 1 
        ORDER BY timestamp DESC 
        LIMIT ?
        """,
        (limit,),
    )
    return cursor.fetchall()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    # Query recent cashback transactions from payment_events table
    transactions = _latest_transactions()
    template = env.get_template("dashboard.html")
    return template.render(transactions=transactions, message=None)


@router.post("/reset_user", response_class=HTMLResponse)
def reset_user(request: Request, username: str = Form(...), token: str = Form("")):
    admin_token = os.getenv("ADMIN_TOKEN", "")
    if not admin_token:
        raise HTTPException(status_code=500, detail="Admin token not configured")
    if not secrets.compare_digest(token, admin_token):
        raise HTTPException(status_code=403, detail="Forbidden")

    success = db.reset_user(username.strip())
    message = (
        f"User @{username} reset successfully."
        if success
        else f"User @{username} not found or reset failed."
    )
    if success:
        _discord_notify(
            title="Admin Action: User Reset",
            description=f"Admin reset daily counters for @{username}",
            color=0x3366FF,
        )
    template = env.get_template("dashboard.html")
    return template.render(transactions=_latest_transactions(), message=message)


dashboard_router = router
