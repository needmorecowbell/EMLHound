from fastapi import APIRouter, Request
from emlhound.vaultman import VaultMan
from emlhound.config import Config
import redis
import os
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse



config = Config(os.getenv("EMLH_CFG")).config

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

eml_pool = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"])
vman = VaultMan(config["vault_path"])
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request:Request):
    stats=vman.refresh_stats()    
    return templates.TemplateResponse("dashboard.html", {"request": request , "stats":stats})