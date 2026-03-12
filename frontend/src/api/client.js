const API_BASE = 'https://codeecoscan.onrender.com'
const _headers = { 'Content-Type': 'application/json' }

async function _throw(res) {
    if (res.status === 404) throw new Error('Backend deploying — try again in ~2 min')
    if (res.status === 400) { const d = await res.json().catch(() => ({})); throw new Error(d.detail || 'Invalid request') }
    const d = await res.json().catch(() => ({}))
    throw new Error(d.detail || `Server error ${res.status}`)
}

// ── Core analysis ──────────────────────────────────────────────────

export async function analyzeCode(code, signal) {
    const r = await fetch(`${API_BASE}/analyze`, { method: 'POST', headers: _headers, body: JSON.stringify({ code }), signal })
    if (!r.ok) await _throw(r)
    return r.json()
}

// ── Repository scanning (async job) ────────────────────────────────

/**
 * Submit a repo scan — returns {job_id, status:'queued'} immediately.
 */
export async function submitRepoScan(repoUrl) {
    const r = await fetch(`${API_BASE}/analyze_repo`, {
        method: 'POST', headers: _headers, body: JSON.stringify({ repo_url: repoUrl }),
    })
    if (!r.ok) await _throw(r)
    return r.json()  // {job_id, status, message}
}

/**
 * Poll a background scan job.
 * Returns {job_id, status, result, error, elapsed_s}
 */
export async function pollJob(jobId) {
    const r = await fetch(`${API_BASE}/jobs/${jobId}`)
    if (!r.ok) await _throw(r)
    return r.json()
}

// ── Profiling ──────────────────────────────────────────────────────

export async function profileCode(code, signal) {
    const r = await fetch(`${API_BASE}/profile`, { method: 'POST', headers: _headers, body: JSON.stringify({ code }), signal })
    if (!r.ok) await _throw(r)
    return r.json()
}

// ── Analysis history ───────────────────────────────────────────────

export async function fetchAnalysisHistory(limit = 50) {
    const r = await fetch(`${API_BASE}/analysis/history?limit=${limit}`)
    if (!r.ok) await _throw(r)
    return r.json()
}

// ── Repo commits ──────────────────────────────────────────────────

export async function fetchCommits() {
    const r = await fetch(`${API_BASE}/repo/commits`)
    if (!r.ok) await _throw(r)
    return r.json()
}
