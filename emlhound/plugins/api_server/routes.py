from fastapi import APIRouter
from emlhound.vaultman import VaultMan
from emlhound.config import Config
import redis
import os



print(os.getenv("EMLH_CFG"))
config = Config(os.getenv("EMLH_CFG")).config

print(config)

eml_pool = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"])
vman = VaultMan(config["vault_path"])
router = APIRouter()

@router.get("/")
def root():
    return {"response": vman.refresh_stats() }