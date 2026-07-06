#!/usr/bin/env python3
"""feishu_archive.py <file> [name] — md 产物存档到飞书云空间 agentco 目录,stdout 打印可访问链接。
凭据(.env):FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_ARCHIVE_FOLDER_TOKEN(云空间目标文件夹 token)。
应用需开通权限:drive:drive(或至少 drive:file:upload)。未配置 → 静默退出码 3(dispatch 降级本地路径)。
"""
import json, os, sys, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import load_env

load_env()
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FOLDER = os.environ.get("FEISHU_ARCHIVE_FOLDER_TOKEN", "")
DOMAIN = os.environ.get("FEISHU_DOMAIN", "feishu.cn")
if not (APP_ID and APP_SECRET and FOLDER):
    sys.exit(3)

src = Path(sys.argv[1])
name = sys.argv[2] if len(sys.argv) > 2 else src.name
data = src.read_bytes()

def api(url, payload=None, headers=None, raw=None, method=None):
    req = urllib.request.Request(url, raw if raw is not None else json.dumps(payload).encode(),
                                 headers or {"Content-Type": "application/json"}, method=method)
    return json.loads(urllib.request.urlopen(req, timeout=20).read())

tok = api("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
          {"app_id": APP_ID, "app_secret": APP_SECRET})
if tok.get("code") != 0:
    print(f"token失败: {tok}", file=sys.stderr); sys.exit(1)
tenant = tok["tenant_access_token"]

# multipart/form-data 手工拼装(依赖零)
boundary = uuid.uuid4().hex
parts = []
for k, v in [("file_name", name), ("parent_type", "explorer"),
             ("parent_node", FOLDER), ("size", str(len(data)))]:
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
             f"Content-Type: text/markdown\r\n\r\n".encode() + data + b"\r\n")
parts.append(f"--{boundary}--\r\n".encode())
body = b"".join(parts)

r = api("https://open.feishu.cn/open-apis/drive/v1/files/upload_all", raw=body, headers={
    "Authorization": f"Bearer {tenant}",
    "Content-Type": f"multipart/form-data; boundary={boundary}"})
if r.get("code") != 0:
    print(f"上传失败: {r}", file=sys.stderr); sys.exit(1)
print(f"https://{DOMAIN}/file/{r['data']['file_token']}")
