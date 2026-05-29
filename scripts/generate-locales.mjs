/**
 * Build-time translation generator for InstaDownload.
 * 
 * Reads frontend/src/i18n/locales/en.json and generates
 * locale files for 22 target languages.
 * 
 * Usage: node scripts/generate-locales.mjs
 * 
 * No runtime backend needed — translations are static files
 * bundled with the frontend at build time.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import translate from '@vitalets/google-translate-api'

const __dirname = dirname(fileURLToPath(import.meta.url))
const LOCALES_DIR = resolve(__dirname, '..', 'frontend', 'src', 'i18n', 'locales')
const EN_PATH = resolve(LOCALES_DIR, 'en.json')

// Target languages: code -> human label (for logging)
const TARGET_LANGS = [
  'es', 'hi', 'ar', 'pt', 'fr', 'de', 'id', 'ja', 'ko', 'vi',
  'it', 'tr', 'bn', 'ta', 'pa', 'ur', 'te', 'ms', 'th', 'ru', 'nl', 'zh',
]

// Keys or key prefixes whose values should NOT be translated
const SKIP_KEYS = new Set([
  'lang', 'brand',
  // Language names in the language section
  'en', 'es', 'hi', 'ar', 'pt', 'fr', 'de', 'id', 'ja', 'ko',
  'vi', 'it', 'tr', 'bn', 'ta', 'pa', 'ur', 'te', 'ms', 'th', 'ru', 'nl', 'zh',
])

function shouldTranslate(keyPath, value) {
  if (!value || value.trim().length < 2) return false
  if (/^\d+$/.test(value.trim())) return false
  const parts = keyPath.split('.')
  if (parts.at(-1) === 'lang') return false
  if (parts[0] === 'language' && parts.length === 2) return false
  if (SKIP_KEYS.has(parts.at(-1))) return false
  return true
}

function flatten(obj, prefix = '') {
  const items = {}
  for (const [key, val] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      Object.assign(items, flatten(val, path))
    } else if (typeof val === 'string') {
      items[path] = val
    }
  }
  return items
}

function unflatten(items) {
  const result = {}
  for (const [path, val] of Object.entries(items)) {
    const parts = path.split('.')
    let current = result
    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) current[parts[i]] = {}
      current = current[parts[i]]
    }
    current[parts.at(-1)] = val
  }
  return result
}

async function translateBatch(texts, targetLang) {
  const results = []
  // Translate in chunks of 5 to avoid overwhelming the API
  const CHUNK = 5
  for (let i = 0; i < texts.length; i += CHUNK) {
    const chunk = texts.slice(i, i + CHUNK)
    const promises = chunk.map(t => 
      translate(t, { to: targetLang })
        .then(r => r.text)
        .catch(() => null)
    )
    const chunkResults = await Promise.all(promises)
    results.push(...chunkResults)
    // Small delay between chunks to be nice
    if (i + CHUNK < texts.length) {
      await new Promise(r => setTimeout(r, 200))
    }
  }
  return results
}

async function main() {
  // Read en.json
  const enRaw = JSON.parse(readFileSync(EN_PATH, 'utf-8'))
  const flat = flatten(enRaw)

  // Build translation map
  const textToKey = {}
  const toTranslate = []
  for (const [keyPath, val] of Object.entries(flat)) {
    if (shouldTranslate(keyPath, val)) {
      textToKey[val] = keyPath
      toTranslate.push(val)
    }
  }

  console.log(`Loaded en.json — ${Object.keys(flat).length} keys, ${toTranslate.length} to translate\n`)

  for (const lang of TARGET_LANGS) {
    const outPath = resolve(LOCALES_DIR, `${lang}.json`)
    console.log(`[${lang}] Translating ${toTranslate.length} strings...`)

    try {
      const translatedTexts = await translateBatch(toTranslate, lang)
      
      // Build translated flat object
      const translatedFlat = { ...flat }
      for (let i = 0; i < toTranslate.length; i++) {
        const keyPath = textToKey[toTranslate[i]]
        if (translatedTexts[i]) {
          translatedFlat[keyPath] = translatedTexts[i]
        }
      }

      // Restore nested structure
      const result = unflatten(translatedFlat)
      writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf-8')
      console.log(`  ✓ Wrote ${lang}.json`)
    } catch (err) {
      console.error(`  ✗ ${lang}: ${err.message}`)
    }

    // Delay between languages
    await new Promise(r => setTimeout(r, 500))
  }

  console.log('\n✓ Done! All locale files generated.')
}

main().catch(console.error)
