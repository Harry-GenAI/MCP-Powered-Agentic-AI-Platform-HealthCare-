import redis
import json


#initialize the redis client
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

#save/set redis cache
def set_cache(key_name:str, value, exp_time_limit:int=3600):

    redis_client.set(
        name=key,
        ex=ttl,
        value=json.dumps(value)

    )

#get redis cache
def get_cache(key:str):

    value = redis_client.get(key)

    if value:
        return json.loads(value)
    
    return None
