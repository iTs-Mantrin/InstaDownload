"""Auto-translation endpoint for frontend i18n.

Frontend hits ``/api/locales/{lang}`` and gets back a JSON dict of translated
strings.  The backend caches results so each language is translated only once.
"""

from fastapi import APIRouter
from app.services.translation_service import translate_locale

router = APIRouter(prefix="/api", tags=["Translation"])


@router.get("/locales/{lang}")
async def get_locale(lang: str):
    """Return translated locale JSON for *lang* (e.g. ``es``, ``fr``, ``hi``)."""
    return translate_locale(lang)
