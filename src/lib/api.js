const BASE = '/api'

async function get(path) {
  const response = await fetch(`${BASE}${path}`)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `request failed with status ${response.status}`)
  }
  return response.json()
}

export function fetchSites() {
  return get('/sites')
}

export function fetchGeometry(site, utc, height) {
  return get(
    `/geometry?site=${encodeURIComponent(site)}` +
      `&utc=${encodeURIComponent(utc)}` +
      `&height=${encodeURIComponent(height)}`,
  )
}

export function fetchCompare(sites, utc, height) {
  return get(
    `/compare?sites=${encodeURIComponent(sites.join(','))}` +
      `&utc=${encodeURIComponent(utc)}` +
      `&height=${encodeURIComponent(height)}`,
  )
}

export function fetchHorizon(site, height) {
  return get(`/sites/${encodeURIComponent(site)}/horizon?height=${encodeURIComponent(height)}`)
}

export function fetchProvenance() {
  return get('/provenance')
}
