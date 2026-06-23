import asyncio
import os
import subprocess

import paramiko

from app.core.config import settings


async def run_host_check(host: str) -> str:
    cmd = f"ping -c 1 -W 2 {host}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    return out.decode("utf-8", errors="replace")


async def run_deploy_hook(script_name: str) -> str:
    root = settings.deploy_hooks_dir
    path = os.path.join(root, script_name)
    proc = await asyncio.create_subprocess_shell(
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=root,
    )
    out, _ = await proc.communicate()
    return out.decode("utf-8", errors="replace")


def verify_jump_host(host: str, port: int, username: str, password: str) -> dict:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        host,
        port=port,
        username=username,
        password=password,
        timeout=settings.ssh_probe_timeout,
        allow_agent=True,
        look_for_keys=True,
    )
    _, stdout, _ = client.exec_command("uname -a")
    banner = stdout.read().decode("utf-8", errors="replace").strip()
    client.close()
    return {"host": host, "banner": banner}
