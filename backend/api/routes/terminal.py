from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import docker
import uuid
import os
import asyncio

router = APIRouter()
docker_client = docker.from_env()

@router.websocket("/ws/terminal")
async def terminal_ws(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    workspace_dir = f"/tmp/{session_id}"
    os.makedirs(workspace_dir, exist_ok=True)
    container = docker_client.containers.run(
        "python:3.10",
        command="python3 -i",
        tty=True,
        stdin_open=True,
        detach=True,
        mem_limit="256m",
        network_disabled=True,
        volumes={workspace_dir: {"bind": "/workspace", "mode": "rw"}},
        working_dir="/workspace"
    )
    try:
        exec_id = docker_client.api.exec_create(container.id, 'python3 -i', tty=True, stdin=True)
        sock = docker_client.api.exec_start(exec_id, tty=True, detach=False, stream=True, socket=True)
        async def read_from_container():
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    await websocket.send_text(data.decode(errors='ignore'))
                except Exception:
                    break
        reader_task = asyncio.create_task(read_from_container())
        while True:
            data = await websocket.receive_text()
            try:
                sock.send(data.encode())
            except Exception:
                break
    except WebSocketDisconnect:
        pass
    finally:
        try:
            container.kill()
        except Exception:
            pass
        try:
            container.remove()
        except Exception:
            pass
        try:
            os.system(f"rm -rf {workspace_dir}")
        except Exception:
            pass 