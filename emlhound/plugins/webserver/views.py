from fastapi import APIRouter, Request
from emlhound.vaultman import VaultMan
from emlhound.config import Config
import redis
import os
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse, JSONResponse
import logging


config = Config(os.getenv("EMLH_CFG")).config

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

eml_pool = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"])
vman = VaultMan(config["vault_path"])
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request:Request):
    stats=vman.refresh_stats()    
    return templates.TemplateResponse("dashboard.html", {"request": request , "stats":stats})


@router.delete("/report/{md5}")
def delete_workspace(request:Request, md5:str):
    try:
        vman.delete_workspace(md5)
    except Exception as e:
        logging.error(f"Error deleting workspace {md5}: {e}")
        return JSONResponse(content={"response":"failure", "message":str(e)}, status_code=500)

    return JSONResponse(content={"response":"success"}, status_code=200)


@router.get("/report/{md5}", response_class=HTMLResponse)
def get_eml_report(request:Request, md5:str):
    try:
        report = vman.retrieve_report_from_vault(md5)
        if report is None:
            return templates.TemplateResponse("404.html", {"request": request})
    except Exception as e:
        logging.error(f"Error retrieving report from vault: {e}")

    return templates.TemplateResponse("report.html", {"request": request , "report":report})

@router.get("/reports", response_class=HTMLResponse)
def list_reports(request:Request):
    try:
        hashes = vman.get_eml_hashes()
        
    except Exception as e:
        logging.error(f"Error retreiving reports list from vault: {e}")
        return templates.TemplateResponse("500.html",{"request":request, "report_hashes":hashes})
    
    return templates.TemplateResponse("reports.html",{"request":request, "report_hashes":hashes})

    