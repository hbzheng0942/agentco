#!/usr/bin/env python3
"""feishu_archive.py <file> [name] — md 产物存档为**飞书云文档(docx)**,stdout 打印可预览链接。
直接传 .md 文件飞书不渲染没法看,所以走导入链:medias 上传(ccm_import_open)→ import_tasks
转 docx → 轮询拿文档 token。导入失败降级为原始文件上传(能存但预览差)。
凭据(.env):FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_ARCHIVE_FOLDER_TOKEN(云空间目标文件夹)。
应用需权限:drive:drive(含导入);文件夹须把应用机器人加为可编辑协作者。
未配置 → 静默退出码 3(dispatch 降级本地路径)。"""
import json, os, sys, time, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import load_env

load_env()
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
# 容忍误贴完整 URL(https://xx.feishu.cn/drive/folder/<token>):取末段即 token
FOLDER = os.environ.get("FEISHU_ARCHIVE_FOLDER_TOKEN", "").rstrip("/").rsplit("/", 1)[-1].split("?")[0]
DOMAIN = os.environ.get("FEISHU_DOMAIN", "feishu.cn")
if not (APP_ID and APP_SECRET and FOLDER):
    sys.exit(3)

src = Path(sys.argv[1])
name = (sys.argv[2] if len(sys.argv) > 2 else src.name)
data = src.read_bytes()


def api(url, payload=None, headers=None, raw=None):
    body = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(url, body, headers or {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=20).read())


tok = api("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
          {"app_id": APP_ID, "app_secret": APP_SECRET})
if tok.get("code") != 0:
    print(f"token失败: {tok}", file=sys.stderr); sys.exit(1)
AUTH = {"Authorization": f"Bearer {tok['tenant_access_token']}"}


def multipart(fields, fname, blob):
    b = uuid.uuid4().hex
    parts = [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
             for k, v in fields]
    parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
                 f"Content-Type: application/octet-stream\r\n\r\n".encode() + blob + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    return b"".join(parts), {**AUTH, "Content-Type": f"multipart/form-data; boundary={b}"}


def import_as_docx():
    """md → 飞书云文档:medias 上传(挂 ccm_import_open)→ import_tasks → 轮询结果。"""
    extra = json.dumps({"obj_type": "docx", "file_extension": "md"})
    body, hdr = multipart([("file_name", name), ("parent_type", "ccm_import_open"),
                           ("size", str(len(data))), ("extra", extra)], name, data)
    r = api("https://open.feishu.cn/open-apis/drive/v1/medias/upload_all", raw=body, headers=hdr)
    if r.get("code") != 0:
        raise RuntimeError(f"medias上传: {r}")
    task = api("https://open.feishu.cn/open-apis/drive/v1/import_tasks", {
        "file_extension": "md", "file_token": r["data"]["file_token"], "type": "docx",
        "file_name": name.removesuffix(".md"),
        "point": {"mount_type": 1, "mount_key": FOLDER}}, headers={**AUTH, "Content-Type": "application/json"})
    if task.get("code") != 0:
        raise RuntimeError(f"import_tasks: {task}")
    ticket = task["data"]["ticket"]
    for _ in range(15):
        time.sleep(1)
        st = api(f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}", headers=AUTH)
        job = (st.get("data") or {}).get("result") or {}
        if job.get("job_status") == 0 and job.get("token"):
            return f"https://{DOMAIN}/docx/{job['token']}"
        if job.get("job_status") not in (None, 1, 2):   # 0=成功 1/2=处理中,其余=失败
            raise RuntimeError(f"导入失败: {job}")
    raise RuntimeError("导入超时")


def upload_raw_file():
    body, hdr = multipart([("file_name", name), ("parent_type", "explorer"),
                           ("parent_node", FOLDER), ("size", str(len(data)))], name, data)
    r = api("https://open.feishu.cn/open-apis/drive/v1/files/upload_all", raw=body, headers=hdr)
    if r.get("code") != 0:
        raise RuntimeError(f"文件上传: {r}")
    return f"https://{DOMAIN}/file/{r['data']['file_token']}"


try:
    print(import_as_docx())
except Exception as e:
    print(f"docx导入失败,降级原始文件: {e}", file=sys.stderr)
    try:
        print(upload_raw_file())
    except Exception as e2:
        print(f"降级也失败: {e2}", file=sys.stderr); sys.exit(1)
