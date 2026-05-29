import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Vite glob — loads all locale JSON files at build time
const localeModules = import.meta.glob('./locales/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, unknown>>

const resources: Record<string, { translation: Record<string, unknown> }> = {}

for (const [path, data] of Object.entries(localeModules)) {
  // Path: /src/i18n/locales/es.json -> extract "es"
  const lang = path.split('/').pop()?.replace('.json', '')
  if (lang) {
    resources[lang] = { translation: data as Record<string, unknown> }
  }
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
