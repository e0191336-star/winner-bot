import json
from pathlib import Path
from typing import List

from fastapi import APIRouter

router = APIRouter(prefix="/pairs", tags=["pairs"])

_OTC_PATH = Path(__file__).parent / "otc_pairs.json"


@router.get("/otc", response_model=List[str])
async def list_otc_pairs():
	if _OTC_PATH.exists():
		return json.loads(_OTC_PATH.read_text())
	return []