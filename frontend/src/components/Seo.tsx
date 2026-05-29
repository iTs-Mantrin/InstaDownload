import { useEffect } from 'react'

interface SeoProps {
  title: string
  description: string
  path?: string
  keywords?: string[]
  image?: string
  schema?: Record<string, unknown> | Record<string, unknown>[]
}

const DEFAULT_ORIGIN = 'https://instadownload.app'

function upsertMeta(selector: string, attributes: Record<string, string>) {
  let element = document.head.querySelector(selector) as HTMLMetaElement | null
  if (!element) {
    element = document.createElement('meta')
    document.head.appendChild(element)
  }

  Object.entries(attributes).forEach(([key, value]) => {
    element!.setAttribute(key, value)
  })
}

export default function Seo({
  title,
  description,
  path = '/',
  keywords = [],
  image = `${DEFAULT_ORIGIN}/og-image.png`,
  schema,
}: SeoProps) {
  useEffect(() => {
    const canonicalUrl = new URL(path, DEFAULT_ORIGIN).toString()

    document.title = title
    upsertMeta('meta[name="description"]', { name: 'description', content: description })

    if (keywords.length > 0) {
      upsertMeta('meta[name="keywords"]', { name: 'keywords', content: keywords.join(', ') })
    }

    upsertMeta('meta[property="og:title"]', { property: 'og:title', content: title })
    upsertMeta('meta[property="og:description"]', { property: 'og:description', content: description })
    upsertMeta('meta[property="og:type"]', { property: 'og:type', content: 'website' })
    upsertMeta('meta[property="og:url"]', { property: 'og:url', content: canonicalUrl })
    upsertMeta('meta[property="og:image"]', { property: 'og:image', content: image })
    upsertMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: 'summary_large_image' })
    upsertMeta('meta[name="twitter:title"]', { name: 'twitter:title', content: title })
    upsertMeta('meta[name="twitter:description"]', { name: 'twitter:description', content: description })
    upsertMeta('meta[name="twitter:image"]', { name: 'twitter:image', content: image })

    let canonical = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    canonical.href = canonicalUrl

    let schemaElement = document.head.querySelector('#route-schema') as HTMLScriptElement | null
    if (!schemaElement) {
      schemaElement = document.createElement('script')
      schemaElement.id = 'route-schema'
      schemaElement.type = 'application/ld+json'
      document.head.appendChild(schemaElement)
    }

    if (schema) {
      schemaElement.textContent = JSON.stringify(schema)
    } else {
      schemaElement.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: title,
        description,
        url: canonicalUrl,
      })
    }
  }, [description, image, keywords, path, schema, title])

  return null
}
