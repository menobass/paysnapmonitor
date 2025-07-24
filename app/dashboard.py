from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from app.db import db
from app.config import config

router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))

def get_admin():
    # Placeholder for admin authentication
    pass

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    # Query recent cashback transactions from payment_events table
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT username, amount, memo, paid, reason, timestamp, snap_permlink 
        FROM payment_events 
        WHERE paid = 1 
        ORDER BY timestamp DESC 
        LIMIT 20
    """)
    transactions = cursor.fetchall()
    template = env.get_template("dashboard.html")
    return template.render(transactions=transactions)

dashboard_router = router
