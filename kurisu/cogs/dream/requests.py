import aiohttp
import asyncio
from datetime import datetime
from kurisu import sd_cfg
from kurisu.core.database.methods import create_or_update_task

BEARER_TOKEN = sd_cfg["api_token"]
POD_ID = sd_cfg["pod_id"]

BASE_URL = f"https://api.runpod.ai/v2/{POD_ID}"
ASYNC_API = f"{BASE_URL}/run"
SYNC_API = f"{BASE_URL}/runsync"
STATUS =  f"{BASE_URL}/status/"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

async def async_run(payload, user_id, chat_id, message_id, debug=None):
    if debug:
        json_req = {"id": debug, "status": "IN_QUEUE"}
    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(ASYNC_API, json=payload, headers=HEADERS) as r:
                json_req = await r.json()
        
    task_id = json_req["id"]
    status = json_req["status"]
    
    create_or_update_task(task_guid=task_id, date=datetime.now(), status=status, user_id=user_id, chat_id=chat_id, message_id=message_id)
    return task_id

async def sync_run(payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(SYNC_API, json=payload, headers=HEADERS) as r:
            json_req = await r.json()

    return json_req

async def check_status(task_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{STATUS}{task_id}", headers=HEADERS) as r:
            return await r.json()
