const API_BASE = 'https://codeecoscan.onrender.com'

/**
 * POST /analyze — analyze Python code for energy risk.
 * @param {string} code
 * @param {AbortSignal} [signal]
 * @returns {Promise<object>}
 */
export async function analyzeCode(code, signal) {
    const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
        signal,
    })
    if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `API error ${res.status}`)
    }
    return res.json()
}

/**
 * Stubs for future endpoints — currently return mock data.
 * Structured so UI components don't need changes when backend is ready.
 */
export async function fetchRepoSummary(/* repoName */) {
    // TODO: GET /repo/summary
    return null
}

export async function fetchRepoHistory(/* repoName */) {
    // TODO: GET /repo/history
    return null
}

export async function fetchProfiling(/* code */) {
    // TODO: POST /profile
    return null
}
