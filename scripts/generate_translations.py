"""
Build-time translation generator: reads en.json and generates 22 locale files.

Usage: python scripts/generate_translations.py

Requires deep-translator (pip install deep-translator).
Runs at build time, not at runtime — no backend dependency.
"""

import json
import os
import sys
from pathlib import Path

# Try to import, install if missing
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Installing deep-translator...")
    os.system(f"{sys.executable} -m pip install deep-translator")
    from deep_translator import GoogleTranslator

LOCALES_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "i18n" / "locales"
EN_PATH = LOCALES_DIR / "en.json"

# Target languages (key = filename, value = what deep-translator expects)
LANGUAGES = {
    "es": "spanish",
    "hi": "hindi",
    "ar": "arabic",
    "pt": "portuguese",
    "fr": "french",
    "de": "german",
    "id": "indonesian",
    "ja": "japanese",
    "ko": "korean",
    "vi": "vietnamese",
    "it": "italian",
    "tr": "turkish",
    "bn": "bengali",
    "ta": "tamil",
    "pa": "punjabi",
    "ur": "urdu",
    "te": "telugu",
    "ms": "malay",
    "th": "thai",
    "ru": "russian",
    "nl": "dutch",
    "zh": "chinese (simplified)",
    "zh-TW": "chinese (traditional)",
}

# Keys to NOT translate (proper names, brand, language names)
SKIP_KEYS = {"lang", "brand", "en", "es", "hi", "ar", "pt", "fr", "de", "id", "ja",
             "ko", "vi", "it", "tr", "bn", "ta", "pa", "ur", "te", "ms", "th",
             "ru", "nl", "zh"}

SKIP_KEY_PREFIXES = ("language.",)  # Don't translate language names


def should_translate(key_path: str, value: str) -> bool:
    """Return True if this value should be translated."""
    # Skip short values (likely codes or placeholders)
    if len(value.strip()) < 2:
        return False
    # Skip pure numbers
    if value.strip().isdigit():
        return False
    # Skip brand/language names by key
    parts = key_path.split(".")
    if parts[-1] in SKIP_KEYS:
        return False
    for prefix in SKIP_KEY_PREFIXES:
        if key_path.startswith(prefix):
            return False
    return True


def flatten(obj: dict, prefix: str = "") -> dict[str, str]:
    """Flatten nested dict into dot-separated keys."""
    items = {}
    for key, val in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict):
            items.update(flatten(val, path))
        else:
            items[path] = val
    return items


def unflatten(items: dict[str, str]) -> dict:
    """Restore nested dict from dot-separated keys."""
    result = {}
    for path, val in items.items():
        parts = path.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = val
    return result


def translate_object(en_obj: dict, target_lang: str) -> dict:
    """Translate all translatable values in en_obj to target_lang (batch)."""
    flat = flatten(en_obj)
    translator = GoogleTranslator(source="auto", target=target_lang)

    # Build ordered list of translatable values
    to_translate = []
    key_order = []
    for key_path, val in flat.items():
        if should_translate(key_path, val) and val.strip():
            to_translate.append(val)
            key_order.append(key_path)

    # Batch translate
    translated_batch = []
    if to_translate:
        try:
            translated_batch = translator.translate_batch(to_translate)
            print(f"  [OK] Batch translated {len(translated_batch)} strings")
        except Exception as e:
            print(f"  [FAIL] Batch failed ({e}), trying individually...")
            # Fallback: individual
            for val in to_translate:
                try:
                    translated_batch.append(translator.translate(val))
                except Exception:
                    translated_batch.append(val)

    # Reassemble
    idx = 0
    translated = {}
    for key_path in flat:
        if key_path in key_order:
            translated[key_path] = translated_batch[idx] if idx < len(translated_batch) else flat[key_path]
            idx += 1
        else:
            translated[key_path] = flat[key_path]

    return unflatten(translated)


def main():
    if not EN_PATH.exists():
        print(f"Error: {EN_PATH} not found")
        sys.exit(1)

    with open(EN_PATH, encoding="utf-8") as f:
        en_data = json.load(f)

    print(f"Loaded en.json ({len(flatten(en_data))} keys)\n")

    for lang_code, lang_name in LANGUAGES.items():
        out_path = LOCALES_DIR / f"{lang_code}.json"

        print(f"\n--- Translating to {lang_name} ({lang_code}) ---")
        try:
            translated = translate_object(en_data, lang_name)

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)

            print(f"  [WRITE] {out_path.name}")
        except Exception as e:
            print(f"  [FAIL] {e}")

    print("\n[DONE] All locale files generated.")


if __name__ == "__main__":
    main()
