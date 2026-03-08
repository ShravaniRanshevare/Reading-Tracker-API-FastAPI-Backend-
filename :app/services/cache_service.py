import json
from ..redis_client import redis_client

async def get_cache(key:str):
    data=redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key:str,value,ttl:int=60):
    redis_client.set(key,json.dumps(value),ex=ttl)