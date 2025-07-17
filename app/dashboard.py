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
    # Query recent cashback transactions
    cursor = db.conn.cursor()
    cursor.execute("SELECT username, purchases, last_purchase FROM users ORDER BY last_purchase DESC LIMIT 10")
    transactions = cursor.fetchall()
    template = env.get_template("dashboard.html")
    return template.render(transactions=transactions)

dashboard_router = router
