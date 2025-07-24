import time
import os
import requests
import json
from lighthive.client import Client
from lighthive.datastructures import Operation
from app.config import config
from app.db import db
from app.cashback import CashbackCalculator
from app.logging_utils import setup_logger
from app.snap_utils import get_latest_peaksnaps_post, user_has_valid_snap

logger = setup_logger("paynsnapbot")

class HiveBot:
    LAST_BLOCK_FILE = "last_block.txt"

    def __init__(self):
        self.nodes = [
            'https://api.hive.blog',         # @blocktrades
            'https://api.openhive.network',  # @gtg
            'https://anyx.io',               # @anyx
            'https://rpc.ausbit.dev',        # @ausbitbank
            'https://rpc.mahdiyari.info',    # @mahdiyari
            'https://api.hive.blue',         # @guiltyparties
            'https://techcoderx.com',        # @techcoderx
            'https://hive.roelandp.nl',      # @roelandp
            'https://hived.emre.sh',         # @emrebeyler
            'https://api.deathwing.me',      # @deathwing
            'https://api.c0ff33a.uk',        # @c0ff33a
            'https://hive-api.arcange.eu',   # @arcange
            'https://hive-api.3speak.tv',    # @threespeak
            'https://hiveapi.actifit.io'     # @actifit
        ]
        self.stores = config.get('stores', [])
        self.calculator = CashbackCalculator()
        self.username = os.getenv('HIVE_USERNAME')
        self.posting_key = os.getenv('HIVE_POSTING_KEY')
        self.active_key = os.getenv('HIVE_ACTIVE_KEY')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.last_block = self.read_last_block()
        self.pending_payments = []  # List of dicts: {sender, to, amount, memo, block_num, timestamp, snap_author, snap_permlink}

    def send_discord_notification(self, title, description, color=0x00ff00, fields=None):
        """Send a notification to Discord via webhook"""
        if not self.discord_webhook_url:
            logger.debug("Discord webhook URL not configured, skipping notification")
            return
        
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            }
            
            if fields:
                embed["fields"] = fields
                
            payload = {
                "username": "PaySnap Bot",
                "embeds": [embed]
            }
            
            response = requests.post(
                self.discord_webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
            else:
                logger.error(f"Failed to send Discord notification: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")

    def read_last_block(self):
        try:
            with open(self.LAST_BLOCK_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            client = Client(nodes=self.nodes)
            props = client.get_dynamic_global_properties()
            logger.info(f"DEBUG: get_dynamic_global_properties returned: {props} (type: {type(props)})")
            if isinstance(props, dict) and 'head_block_number' in props:
                return props['head_block_number']
            logger.error(f"Could not determine starting block from props: {props}")
            raise Exception("Could not determine starting block.")

    def write_last_block(self, block_num):
        try:
            with open(self.LAST_BLOCK_FILE, "w") as f:
                f.write(str(block_num))
        except Exception as e:
            logger.error(f"Failed to write last block: {e}")

    def poll_blocks(self):
        logger.info("Starting live block polling...")
        client = Client(nodes=self.nodes)
        while True:
            try:
                props = client.get_dynamic_global_properties()
                if not isinstance(props, dict) or 'head_block_number' not in props:
                    logger.error(f"Could not get head_block_number from props: {props}")
                    time.sleep(5)
                    continue
                head_block = props['head_block_number']
                # Start from last processed block + 1
                next_block = self.last_block + 1
                if next_block > head_block:
                    time.sleep(3)
                    continue
                self.process_block(next_block)
                self.write_last_block(next_block)
                self.last_block = next_block
            except Exception as e:
                logger.error(f"Error processing block {self.last_block + 1}: {e}")
                time.sleep(5)
            self.check_pending_payments()

    def process_block(self, block_num):
        logger.info(f"Processing block {block_num}...")
        for node in self.nodes:
            try:
                client = Client(nodes=[node])
                ops = client.get_ops_in_block(block_num, False)
                logger.debug(f"Node {node} ops for block {block_num}: {ops}")
                if ops:
                    logger.info(f"Block {block_num} ops count: {len(ops)}")
                    for op in ops:
                        self.process_op(block_num, op)
                    return
                else:
                    logger.info(f"Node {node} returned no ops for block {block_num}.")
            except Exception as e:
                logger.error(f"Block {block_num} node {node} error: {e}")
        logger.error(f"Failed to process block {block_num} on all nodes.")

    def process_op(self, block_num, op):
        op_id = op.get('trx_id', '')
        op_type = op.get('op', [None])[0]
        op_data = op.get('op', [None, {}])[1]

        # Only log qualifying transfer
        if op_type == 'transfer':
            to = op_data.get('to')
            memo = op_data.get('memo', '')
            amount = op_data.get('amount', '')
            from_account = op_data.get('from', '')
            if to in self.stores and self.valid_memo(memo):
                logger.info(f"QUALIFYING TRANSFER: block={block_num} from={from_account} to={to} amount={amount} memo={memo} trx_id={op_id}")
                
                # Send Discord notification for new payment received
                self.send_discord_notification(
                    title="💳 New Payment Received",
                    description=f"Received payment from **@{from_account}** - waiting for snap",
                    color=0x0099ff,  # Blue
                    fields=[
                        {"name": "User", "value": f"@{from_account}", "inline": True},
                        {"name": "Amount", "value": amount, "inline": True},
                        {"name": "Store", "value": to, "inline": True},
                        {"name": "Invoice", "value": memo, "inline": True},
                        {"name": "Block", "value": str(block_num), "inline": True},
                        {"name": "Status", "value": "⏳ Waiting for snap", "inline": True}
                    ]
                )
                
                self.pending_payments.append({
                    'sender': from_account,
                    'to': to,
                    'amount': float(amount.split()[0]),
                    'memo': memo,
                    'block_num': block_num,
                    'op_id': op_id,
                    'timestamp': time.time(),
                    'snap_author': None,
                    'snap_permlink': None
                })
        # Only log qualifying snap (custom_json or comment, as per your logic)
        if op_type == 'custom_json':
            # Example: check for snap logic here
            # If you have a way to identify a snap, add logic here
            pass
        if op_type == 'comment':
            author = op_data.get('author', '')
            parent_author = op_data.get('parent_author', '')
            permlink = op_data.get('permlink', '')
            # Find pending payments for this author and update with snap info
            for payment in self.pending_payments:
                if payment['sender'] == author and parent_author == 'peak.snaps' and payment['snap_author'] is None:
                    logger.info(f"SNAP DETECTED: block={block_num} author={author} parent_author={parent_author} trx_id={op_id} permlink={permlink}")
                    payment['snap_author'] = author
                    payment['snap_permlink'] = permlink
    def valid_memo(self, memo):
        import re
        return bool(re.match(r"^kcs-hpos-[a-zA-Z0-9-]+$", memo))

    def send_cashback(self, user, amount, memo):
        logger.info(f"Sending {amount} HBD to {user} for {memo}")
        try:
            client = Client(nodes=self.nodes, keys=[self.active_key])
            op = Operation('transfer', {
                'from': self.username,
                'to': user,
                'amount': f"{amount:.3f} HBD",
                'memo': memo
            })
            tx = client.broadcast([op])
            logger.info(f"Transfer broadcast result: {tx}")
        except Exception as e:
            logger.error(f"Error sending cashback to {user}: {e}")

    def reply_comment(self, user, memo, amount, parent_author, parent_permlink):
        import re
        invoice_match = re.match(r"^kcs-hpos-(\d{4})-(\d{4})$", memo)
        invoice_number = memo if not invoice_match else f"{invoice_match.group(1)}-{invoice_match.group(2)}"
        msg = f"Hello {user}, thank you for using Snap and Pay. I just sent you {amount:.2f} HBD back to you for the invoice {invoice_number}."
        logger.info(f"Replying to {user}: {msg}")
        client = Client(nodes=self.nodes, keys=[self.posting_key])
        op = Operation('comment', {
            'parent_author': parent_author,
            'parent_permlink': parent_permlink,
            'author': self.username,
            'permlink': f"paynsnap-{int(time.time())}",
            'title': "",
            'body': msg,
            'json_metadata': '{}'
        })
        client.broadcast([op])

    def check_pending_payments(self):
        logger.info(f"Checking pending payments queue: {len(self.pending_payments)} items.")
        now = time.time()
        timeout = 120  # seconds
        client = Client(nodes=self.nodes)
        still_pending = []
        for payment in self.pending_payments:
            sender = payment['sender']
            to = payment['to']
            amount = payment['amount']
            memo = payment['memo']
            block_num = payment['block_num']
            op_id = payment['op_id']
            ts = payment['timestamp']
            snap_author = payment.get('snap_author')
            snap_permlink = payment.get('snap_permlink')
            logger.info(f"Checking payment: sender={sender}, to={to}, amount={amount}, memo={memo}, block={block_num}")
            logger.info(f"Snap info: snap_author={snap_author}, snap_permlink={snap_permlink}")
            purchases = db.conn.execute("SELECT purchases FROM users WHERE username=?", (sender,)).fetchone()
            purchase_num = purchases[0] + 1 if purchases else 1
            daily_limit = config.get('limits', {}).get('daily_cashback_limit', 3)
            reason = None
            paid = 0
            snap_valid = False
            # Only process if snap info is present and valid
            if purchase_num > daily_limit:
                reason = "User exceeded daily limit"
                paid = 0
                # Send Discord notification for daily limit exceeded
                self.send_discord_notification(
                    title="⚠️ Payment Rejected - Daily Limit",
                    description=f"**@{sender}** exceeded daily cashback limit",
                    color=0xffaa00,  # Orange
                    fields=[
                        {"name": "User", "value": f"@{sender}", "inline": True},
                        {"name": "Purchase #", "value": str(purchase_num), "inline": True},
                        {"name": "Daily Limit", "value": str(daily_limit), "inline": True},
                        {"name": "Amount", "value": f"{amount:.3f} HBD", "inline": True},
                        {"name": "Invoice", "value": memo, "inline": True}
                    ]
                )
            elif not snap_author or not snap_permlink:
                reason = "No snap detected"
                paid = 0
            else:
                snap_valid = user_has_valid_snap(client, snap_author, snap_permlink, sender)
                logger.info(f"user_has_valid_snap({snap_author}, {snap_permlink}, {sender}) returned: {snap_valid}")
                if not snap_valid:
                    reason = "Snap detected, wrong beneficiaries"
                    paid = 0
                    # Send Discord notification for invalid snap
                    self.send_discord_notification(
                        title="❌ Payment Rejected - Invalid Snap",
                        description=f"**@{sender}** posted a snap with wrong beneficiaries",
                        color=0xff0000,  # Red
                        fields=[
                            {"name": "User", "value": f"@{sender}", "inline": True},
                            {"name": "Amount", "value": f"{amount:.3f} HBD", "inline": True},
                            {"name": "Invoice", "value": memo, "inline": True},
                            {"name": "Snap Link", "value": f"[@{snap_author}/{snap_permlink}](https://peakd.com/@{snap_author}/{snap_permlink})", "inline": False},
                            {"name": "Issue", "value": "Beneficiaries not set correctly", "inline": False}
                        ]
                    )
                else:
                    logger.info(f"Valid snap detected for user {sender}. Processing cashback.")
                    cashback = self.calculator.calculate(purchase_num, amount)
                    self.send_cashback(sender, cashback, memo)
                    self.reply_comment(sender, memo, cashback, snap_author, snap_permlink)
                    
                    # Send Discord notification for successful payment
                    self.send_discord_notification(
                        title="💰 Cashback Sent!",
                        description=f"Successfully sent cashback to **@{sender}**",
                        color=0x00ff00,  # Green
                        fields=[
                            {"name": "User", "value": f"@{sender}", "inline": True},
                            {"name": "Amount", "value": f"{cashback:.3f} HBD", "inline": True},
                            {"name": "Purchase #", "value": str(purchase_num), "inline": True},
                            {"name": "Original Payment", "value": f"{amount:.3f} HBD", "inline": True},
                            {"name": "Invoice", "value": memo, "inline": True},
                            {"name": "Snap Link", "value": f"[@{snap_author}/{snap_permlink}](https://peakd.com/@{snap_author}/{snap_permlink})", "inline": False}
                        ]
                    )
                    
                    db.conn.execute("INSERT INTO processed_ops (block_num, op_id) VALUES (?, ?)", (block_num, op_id))
                    db.conn.execute("INSERT OR REPLACE INTO users (username, purchases, last_purchase) VALUES (?, ?, datetime('now'))", (sender, purchase_num))
                    db.conn.commit()
                    paid = 1
                    reason = f"Snap detected, paid {cashback:.2f} HBD"
            # Timeout logic
            if not paid and now - ts < timeout:
                logger.info(f"Payment from {sender} still pending snap reply.")
                still_pending.append(payment)
            elif not paid and now - ts >= timeout:
                reason = "Payment timed out waiting for snap"
                logger.info(f"Payment from {sender} timed out waiting for snap.")
                # Send Discord notification for timeout
                self.send_discord_notification(
                    title="⏰ Payment Timeout",
                    description=f"**@{sender}** payment timed out waiting for snap",
                    color=0x808080,  # Gray
                    fields=[
                        {"name": "User", "value": f"@{sender}", "inline": True},
                        {"name": "Amount", "value": f"{amount:.3f} HBD", "inline": True},
                        {"name": "Invoice", "value": memo, "inline": True},
                        {"name": "Timeout", "value": f"{timeout} seconds", "inline": True}
                    ]
                )
            db.conn.execute(
                "INSERT INTO payment_events (block_num, op_id, username, amount, memo, snap_permlink, paid, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (block_num, op_id, sender, amount, memo, snap_permlink, paid, reason)
            )
            db.conn.commit()
        self.pending_payments = still_pending
