const API_BASE = 'https://codeecoscan.onrender.com'
const _headers = { 'Content-Type': 'application/json' }

async function _throw(res) {
    if (res.status === 404) throw new Error('Backend deploying — endpoint not available yet, try again in ~2 min')
    const d = await res.json().catch(() => ({}))
    throw new Error(d.detail || `Server error ${res.status}`)
}

export async function analyzeCode(code, signal) {
    const r = await fetch(`${API_BASE}/analyze`, { method: 'POST', headers: _headers, body: JSON.stringify({ code }), signal })
    if (!r.ok) await _throw(r)
    return r.json()
}

export async function analyzeRepo(repoUrl, signal) {
    const r = await fetch(`${API_BASE}/analyze_repo`, { method: 'POST', headers: _headers, body: JSON.stringify({ repo_url: repoUrl }), signal })
    if (!r.ok) await _throw(r)
    return r.json()
}

export async function profileCode(code, signal) {
    const r = await fetch(`${API_BASE}/profile`, { method: 'POST', headers: _headers, body: JSON.stringify({ code }), signal })
    if (!r.ok) await _throw(r)
    return r.json()
}

export async function fetchAnalysisHistory(limit = 50) {
    const r = await fetch(`${API_BASE}/analysis/history?limit=${limit}`)
    if (!r.ok) await _throw(r)
    return r.json()
}

export async function fetchCommits() {
    const r = await fetch(`${API_BASE}/repo/commits`)
    if (!r.ok) await _throw(r)
    return r.json()
}
