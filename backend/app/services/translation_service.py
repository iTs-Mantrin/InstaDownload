"""Auto-translate English locale strings into any target language using deep-translator.

Caches results in-memory and to disk so each language is translated only once.
"""

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Paths
_HERE = Path(__file__).resolve().parent  # backend/app/services/
_BACKEND = _HERE.parent.parent  # backend/
_EN_SOURCE = _HERE.parent.parent.parent / "frontend" / "src" / "i18n" / "locales" / "en.json"
_CACHE_DIR = _BACKEND / "translation_cache"

# In-memory cache: lang_code -> translated dict
_memory_cache: dict[str, dict[str, Any]] = {}
_memory_lock = Lock()

_MAX_BATCH = 50  # deep-translator batch limit


def _load_en_source() -> dict[str, Any]:
    """Load the English source JSON."""
    if not _EN_SOURCE.exists():
        logger.warning("en.json not found at %s, using fallback", _EN_SOURCE)
        return {"lang": "English", "brand": "InstaDownload"}
    with open(_EN_SOURCE, encoding="utf-8") as f:
        return json.load(f)


def _flatten(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, str]:
    """Flatten a nested dict to dot-separated keys with string values only."""
    items: dict[str, str] = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten(v, new_key, sep=sep))
        elif isinstance(v, str):
            items[new_key] = v
        # skip non-string values (numbers, arrays, etc.)
    return items


def _unflatten(d: dict[str, str], sep: str = ".") -> dict[str, Any]:
    """Restore nested dict from dot-separated keys."""
    result: dict[str, Any] = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
    return result


def _cache_path(lang: str) -> Path:
    return _CACHE_DIR / f"{lang}.json"


def _load_disk_cache(lang: str) -> dict[str, Any] | None:
    path = _cache_path(lang)
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.warning("Failed to read cache for %s", lang)
    return None


def _save_disk_cache(lang: str, data: dict[str, Any]) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(lang)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        logger.warning("Failed to write cache for %s", lang)


_LANG_MAP: dict[str, str] = {
    # deep-translator needs full codes for Chinese variants
    "zh": "zh-CN",
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
    "zh-HK": "zh-TW",
    "zh-SG": "zh-CN",
}


def _normalize_lang(lang: str) -> str:
    """Normalize a language code (e.g. ``en-IN`` → ``en``, ``zh`` → ``zh-CN``)."""
    normalized = lang.split("-")[0] if "-" in lang else lang
    return _LANG_MAP.get(lang, _LANG_MAP.get(normalized, normalized))


def translate_locale(target_lang: str) -> dict[str, Any]:
    """Return translated locale dict for *target_lang* (e.g. ``'es'``, ``'fr'``).

    - Checks in-memory cache first, then disk cache.
    - Falls back to auto-translating from English using Google Translate.
    - The result is cached permanently (in-memory + on disk).
    """
    # Normalize language code (e.g. en-IN → en, zh → zh-CN)
    normalized = _normalize_lang(target_lang)

    # 1. In-memory cache (check normalized key)
    with _memory_lock:
        cached = _memory_cache.get(normalized)
        if cached is not None:
            # Also cache under original key for future lookups
            if target_lang != normalized:
                _memory_cache[target_lang] = cached
            return cached

    # 2. Disk cache
    disk_cached = _load_disk_cache(normalized)
    if disk_cached is not None:
        with _memory_lock:
            _memory_cache[normalized] = disk_cached
            if target_lang != normalized:
                _memory_cache[target_lang] = disk_cached
        return disk_cached

    # 3. Translate
    english = _load_en_source()

    if normalized == "en":
        with _memory_lock:
            _memory_cache[target_lang] = english
            _memory_cache["en"] = english
        return english

    # Flatten -> translate batch -> unflatten
    flat_en = _flatten(english)
    texts = list(flat_en.values())
    keys = list(flat_en.keys())

    try:
        translator = GoogleTranslator(source="en", target=normalized)
        translated_texts: list[str] = []

        for i in range(0, len(texts), _MAX_BATCH):
            batch = texts[i : i + _MAX_BATCH]
            # GoogleTranslator.translate_batch returns list[str]
            translated_texts.extend(translator.translate_batch(batch))
    except Exception:
        logger.exception(
            "Translation failed for %s (normalized: %s), falling back to English",
            target_lang,
            normalized,
        )
        with _memory_lock:
            _memory_cache[target_lang] = english
            _memory_cache[normalized] = english
        return english

    # Build flat translated dict
    flat_translated: dict[str, str] = {}
    for key, translated in zip(keys, translated_texts):
        flat_translated[key] = translated or flat_en[key]

    result = _unflatten(flat_translated)

    # Cache (under both original and normalized keys)
    with _memory_lock:
        _memory_cache[target_lang] = result
        _memory_cache[normalized] = result
    _save_disk_cache(normalized, result)
    # Also save under original key so future direct lookups hit disk
    if target_lang != normalized:
        _save_disk_cache(target_lang, result)

    return result
