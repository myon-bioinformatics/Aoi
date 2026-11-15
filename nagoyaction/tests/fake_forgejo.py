#!/usr/bin/env python3
"""🎭 stand-in for the forgejo binary: the CLI subcommands hubdial uses + an in-memory slice of the REST API."""
import json, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "fake-token-0123456789abcdef0123456789abcdef"
args = sys.argv[1:]
cfg = args[args.index("--config") + 1] if "--config" in args else ""
args = [a for i, a in enumerate(args) if a != "--config" and (i == 0 or args[i - 1] != "--config")]
cmd = args[0] if args else ""

if cmd == "--version":
    print("Forgejo version 0.0.0-fake")
elif cmd == "migrate":
    print("migrated")
elif cmd == "admin" and args[2] == "create":
    print(f"New user '{args[args.index('--username') + 1]}' has been successfully created!")
elif cmd == "admin" and args[2] == "generate-access-token":
    print(TOKEN)
elif cmd == "web":
    port = int(re.search(r"HTTP_PORT = (\d+)", open(cfg).read()).group(1))
    db = {"repos": {}, "labels": {}, "issues": {}, "mirrors": {}}

    class H(BaseHTTPRequestHandler):
        log_message = lambda *a: None

        def reply(self, code, obj=None):
            raw = json.dumps(obj).encode() if obj is not None else b""
            self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(raw)

        def route(self, method):
            path = self.path.split("?")[0]
            if path == "/api/healthz":
                return self.reply(200, {"status": "pass"})
            if self.headers.get("Authorization") != f"token {TOKEN}":
                return self.reply(401, {"message": "unauthorized"})
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"null")
            if path == "/api/v1/user/repos":
                if method == "POST":
                    db["repos"][body["name"]] = {"name": body["name"], "private": body.get("private", True)}
                    return self.reply(201, db["repos"][body["name"]])
                return self.reply(200, list(db["repos"].values()))
            if m := re.fullmatch(r"/api/v1/repos/[^/]+/([^/]+)/branches/(.+)", path):
                db["polls"] = db.get("polls", 0) + 1
                return self.reply(200, {"name": m.group(2)}) if db["polls"] > 1 else self.reply(404, {"message": "not yet"})
            m = re.fullmatch(r"/api/v1/repos/([^/]+)/([^/]+)/(labels|issues|pulls|push_mirrors)", path)
            if not m or m.group(2) not in db["repos"]:
                return self.reply(404, {"message": "not found"})
            repo, kind = m.group(2), m.group(3)
            store = db.setdefault({"labels": "labels", "issues": "issues", "push_mirrors": "mirrors", "pulls": "pulls"}[kind], {}).setdefault(repo, [])
            if method == "GET":
                return self.reply(200, store)
            item = dict(body, id=len(store) + 1)
            if kind == "issues":
                labels = {l["id"]: l for l in db["labels"].get(repo, [])}
                item.update(number=item["id"], html_url=f"http://localhost:{port}/x/{repo}/issues/{item['id']}", labels=[labels[i] for i in body.get("labels", [])])
            if kind == "pulls":
                item.update(number=item["id"], html_url=f"http://localhost:{port}/x/{repo}/pulls/{item['id']}", head={"ref": body["head"]}, base={"ref": body["base"]})
            if kind == "push_mirrors":
                item.pop("remote_password", None)
            store.append(item)
            return self.reply(201, item)

        do_GET = lambda self: self.route("GET")
        do_POST = lambda self: self.route("POST")

    HTTPServer(("127.0.0.1", port), H).serve_forever()
