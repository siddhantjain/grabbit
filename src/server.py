#!/usr/bin/env python3
"""Grabbit web server with dashboard 🐰"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from .tracker import grabbit


# Load dashboard secret
def load_secret():
    secret_file = Path(__file__).parent.parent / "data" / ".dashboard_secret"
    if secret_file.exists():
        return secret_file.read_text().strip()
    return None

DASHBOARD_SECRET = load_secret()


class GrabbitHandler(BaseHTTPRequestHandler):
    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _check_auth(self, path):
        """Auth disabled - running on Tailscale."""
        return True

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Check authentication via URL path
        if not self._check_auth(path):
            self._send_html("<h1>🐰 Grabbit says: Access denied!</h1>", 403)
            return

        # Strip the secret from the path for routing
        clean_path = path.replace(f"/{DASHBOARD_SECRET}", "") or "/"

        # API routes
        if clean_path.startswith("/api/"):
            self._handle_api(clean_path, params)
            return

        # Dashboard
        if clean_path in ["/", "/index.html"]:
            html = generate_dashboard_html()
            self._send_html(html)
            return

        self._send_html("<h1>🐰 Page not found!</h1>", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if not self._check_auth(path):
            self._send_json({"error": "Access denied"}, 403)
            return

        clean_path = path.replace(f"/{DASHBOARD_SECRET}", "") or "/"

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}

        if clean_path == "/api/add":
            result = grabbit.add(**data)
            self._send_json(result)
        elif clean_path == "/api/mark_bought":
            item_id = data.get("id")
            result = grabbit.mark_bought(item_id=item_id)
            self._send_json(result)
        elif clean_path == "/api/archive":
            item_id = data.get("id")
            result = grabbit.archive(item_id)
            self._send_json(result)
        elif clean_path == "/api/delete":
            item_id = data.get("id")
            result = grabbit.delete(item_id)
            self._send_json(result)
        elif clean_path == "/api/update":
            item_id = data.pop("id", None)
            if item_id:
                result = grabbit.update(item_id, **data)
                self._send_json(result)
            else:
                self._send_json({"error": "Missing id"}, 400)
        elif clean_path == "/api/restore":
            # Convenience: set status back to needed
            item_id = data.get("id")
            if item_id:
                result = grabbit.update(item_id, status="needed", bought_at=None)
                self._send_json(result)
            else:
                self._send_json({"error": "Missing id"}, 400)
        else:
            self._send_json({"error": "Unknown endpoint"}, 404)

    def _handle_api(self, path, params):
        if path == "/api/list":
            status = params.get("status", ["needed"])[0]
            store = params.get("store", [None])[0]
            category = params.get("category", [None])[0]
            result = grabbit.list(status=status, store=store, category=category)
            self._send_json(result)
        elif path == "/api/summary":
            self._send_json(grabbit.summary())
        elif path == "/api/stores":
            self._send_json(grabbit.stores())
        elif path == "/api/recent":
            days = int(params.get("days", [7])[0])
            self._send_json(grabbit.recent_purchases(days))
        elif path.startswith("/api/at/"):
            store = path.split("/api/at/")[1]
            self._send_json(grabbit.at_store(store))
        elif path.startswith("/api/for/"):
            person = path.split("/api/for/")[1]
            self._send_json(grabbit.for_person(person))
        else:
            self._send_json({"error": "Unknown endpoint"}, 404)

    def log_message(self, format, *args):
        pass  # Suppress logging


def generate_dashboard_html() -> str:
    """Generate the Grabbit dashboard HTML 🐰"""
    summary = grabbit.summary()
    items = grabbit.list(status="needed")["items"]
    stores = grabbit.stores()["stores"]
    
    # Priority colors
    priority_colors = {
        "urgent": "#e94560",
        "high": "#f39c12",
        "medium": "#4ecca3",
        "low": "#888"
    }
    
    # Generate items HTML
    items_html = ""
    if items:
        for item in items:
            priority_color = priority_colors.get(item.get("priority", "medium"), "#888")
            store_badge = f'<span class="store-badge">{item.get("store", "")}</span>' if item.get("store") else ""
            person_badge = f'<span class="person-badge">🎁 {item["for_person"]}</span>' if item.get("for_person") != "self" else ""
            notes = f'<div class="item-notes">{item.get("notes", "")}</div>' if item.get("notes") else ""
            
            items_html += f'''
            <div class="item-card" data-id="{item['id']}" data-priority="{item.get('priority', 'medium')}">
                <div class="item-priority" style="background: {priority_color}"></div>
                <div class="item-content">
                    <div class="item-header">
                        <span class="item-name">{item['item']}</span>
                        {store_badge}
                        {person_badge}
                    </div>
                    {notes}
                </div>
                <div class="item-actions">
                    <button onclick="markBought('{item['id']}')" title="Mark bought">✓</button>
                    <button onclick="archiveItem('{item['id']}')" title="Archive">📦</button>
                </div>
            </div>
            '''
    else:
        items_html = '<div class="empty">🐰 Nothing to grab! Your list is empty.</div>'

    # Generate store filter buttons
    store_filters = '<button class="store-btn active" onclick="filterStore(null)">All</button>'
    for store, count in stores.items():
        store_filters += f'<button class="store-btn" onclick="filterStore(\'{store}\')">{store} ({count})</button>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grabbit 🐰</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        
        h1 {{ 
            text-align: center; 
            margin-bottom: 10px; 
            font-size: 2em;
        }}
        .tagline {{
            text-align: center;
            color: #888;
            margin-bottom: 25px;
            font-size: 0.95em;
        }}
        
        .summary {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 25px;
        }}
        .summary-stat {{
            text-align: center;
            background: rgba(255,255,255,0.05);
            padding: 15px 25px;
            border-radius: 12px;
        }}
        .summary-stat .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #4ecca3;
        }}
        .summary-stat .label {{
            font-size: 0.85em;
            color: #888;
        }}
        .summary-stat.urgent .value {{ color: #e94560; }}
        
        .store-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
            justify-content: center;
        }}
        .store-btn {{
            background: rgba(255,255,255,0.1);
            border: none;
            color: #ccc;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .store-btn:hover {{ background: rgba(255,255,255,0.2); }}
        .store-btn.active {{ background: #4ecca3; color: #1a1a2e; }}
        
        .items-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .item-card {{
            display: flex;
            align-items: stretch;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .item-card:hover {{ transform: translateX(5px); }}
        
        .item-priority {{
            width: 5px;
            flex-shrink: 0;
        }}
        
        .item-content {{
            flex: 1;
            padding: 15px;
        }}
        .item-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .item-name {{
            font-weight: 500;
            font-size: 1.05em;
        }}
        .store-badge {{
            background: #0f3460;
            color: #aaa;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        .person-badge {{
            background: #4a1942;
            color: #f0a;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        .item-notes {{
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .item-actions {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 10px;
            gap: 5px;
        }}
        .item-actions button {{
            background: rgba(255,255,255,0.1);
            border: none;
            color: #fff;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1em;
            transition: all 0.2s;
        }}
        .item-actions button:hover {{
            background: #4ecca3;
        }}
        
        .empty {{
            text-align: center;
            color: #666;
            padding: 40px;
            font-size: 1.1em;
        }}
        
        .add-form {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        .add-form input, .add-form select {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 1em;
            width: 100%;
            margin-bottom: 10px;
        }}
        .add-form input::placeholder {{ color: #666; }}
        .add-form .row {{
            display: flex;
            gap: 10px;
        }}
        .add-form .row > * {{ flex: 1; }}
        .add-form button {{
            background: #4ecca3;
            border: none;
            color: #1a1a2e;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
        }}
        .add-form button:hover {{ background: #3db892; }}
        
        .section-title {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🐰 Grabbit</h1>
        <p class="tagline">Your friendly shopping list rabbit</p>
        
        <div class="summary">
            <div class="summary-stat">
                <div class="value">{summary['total_needed']}</div>
                <div class="label">To Grab</div>
            </div>
            <div class="summary-stat urgent">
                <div class="value">{summary['urgent']}</div>
                <div class="label">Urgent</div>
            </div>
            <div class="summary-stat">
                <div class="value">{summary['total_bought']}</div>
                <div class="label">Grabbed</div>
            </div>
        </div>
        
        <div class="add-form">
            <input type="text" id="item-input" placeholder="What do you need to grab? 🐰" />
            <div class="row">
                <input type="text" id="store-input" placeholder="Store (optional)" />
                <select id="priority-input">
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
            <button onclick="addItem()">🐰 Grab It!</button>
        </div>
        
        <div class="section-title">Items to Grab</div>
        <div class="store-filters">
            {store_filters}
        </div>
        
        <div class="items-list" id="items-list">
            {items_html}
        </div>
    </div>
    
    <script>
        const SECRET = "{DASHBOARD_SECRET}";
        
        async function api(endpoint, method = "GET", data = null) {{
            const url = "/" + SECRET + "/api" + endpoint;
            const opts = {{ method }};
            if (data) {{
                opts.headers = {{ "Content-Type": "application/json" }};
                opts.body = JSON.stringify(data);
            }}
            const res = await fetch(url, opts);
            return res.json();
        }}
        
        async function addItem() {{
            const item = document.getElementById("item-input").value.trim();
            if (!item) return;
            
            const store = document.getElementById("store-input").value.trim() || null;
            const priority = document.getElementById("priority-input").value;
            
            await api("/add", "POST", {{ item, store, priority }});
            location.reload();
        }}
        
        async function markBought(id) {{
            await api("/mark_bought", "POST", {{ id }});
            location.reload();
        }}
        
        async function archiveItem(id) {{
            await api("/archive", "POST", {{ id }});
            location.reload();
        }}
        
        function filterStore(store) {{
            document.querySelectorAll(".store-btn").forEach(btn => btn.classList.remove("active"));
            event.target.classList.add("active");
            
            document.querySelectorAll(".item-card").forEach(card => {{
                if (!store) {{
                    card.style.display = "flex";
                }} else {{
                    const cardStore = card.querySelector(".store-badge")?.textContent;
                    card.style.display = cardStore === store ? "flex" : "none";
                }}
            }});
        }}
        
        // Enter key to add
        document.getElementById("item-input").addEventListener("keypress", (e) => {{
            if (e.key === "Enter") addItem();
        }});
    </script>
</body>
</html>'''


def run_server(port=4002):
    server = HTTPServer(("0.0.0.0", port), GrabbitHandler)
    print(f"🐰 Grabbit running on http://0.0.0.0:{port}/{DASHBOARD_SECRET}/")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
