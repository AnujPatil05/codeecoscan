const API_BASE = 'https://codeecoscan.onrender.com'

const _headers = { 'Content-Type': 'application/json' }

// ── Core analysis ──────────────────────────────────────────────────

export async function analyzeCode(code, signal) {
    const r = await fetch(`${API_BASE}/analyze`, {
        method: 'POST', headers: _headers,
        body: JSON.stringify({ code }), signal,
    })
    if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || `API ${r.status}`) }
    return r.json()
}

// ── Repository scanning ────────────────────────────────────────────

export async function analyzeRepo(repoUrl, signal) {
    const r = await fetch(`${API_BASE}/analyze_repo`, {
        method: 'POST', headers: _headers,
        body: JSON.stringify({ repo_url: repoUrl }), signal,
    })
    if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || `API ${r.status}`) }
    return r.json()
}

// ── Profiling ──────────────────────────────────────────────────────

export async function profileCode(code, signal) {
    const r = await fetch(`${API_BASE}/profile`, {
        method: 'POST', headers: _headers,
        body: JSON.stringify({ code }), signal,
    })
    if (!r.ok) throw new Error(`API ${r.status}`)
    return r.json()
}

// ── Analysis history ───────────────────────────────────────────────

export async function fetchAnalysisHistory(limit = 50) {
    const r = await fetch(`${API_BASE}/analysis/history?limit=${limit}`)
    if (!r.ok) throw new Error(`API ${r.status}`)
    return r.json()
}

// ── Repo commits (recent repo scans) ──────────────────────────────

export async function fetchCommits() {
    const r = await fetch(`${API_BASE}/repo/commits`)
    if (!r.ok) throw new Error(`API ${r.status}`)
    return r.json()
}
