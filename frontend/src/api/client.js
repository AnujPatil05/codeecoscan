const API_BASE = 'https://codeecoscan.onrender.com'

// ── Core analysis ──────────────────────────────────────────────────

/**
 * POST /analyze — analyze Python code for energy risk + line diagnostics.
 * @param {string} code
 * @param {AbortSignal} [signal]
 * @returns {Promise<{extracted_features, risk_assessment, issues}>}
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

// ── Repository scanning ────────────────────────────────────────────

/**
 * POST /analyze_repo — scan a GitHub repository.
 * @param {string} repoUrl
 * @returns {Promise<{repo_name, energy_risk, files_scanned, energy_per_day, co2_saved, top_files}>}
 */
export async function analyzeRepo(repoUrl) {
    const res = await fetch(`${API_BASE}/analyze_repo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
    })
    if (!res.ok) throw new Error(`API error ${res.status}`)
    return res.json()
}

// ── Profiling ──────────────────────────────────────────────────────

/**
 * POST /profile — get execution cost profile for code.
 * @param {string} code
 * @returns {Promise<{line_times, function_costs, peak_memory, total_energy}>}
 */
export async function profileCode(code) {
    const res = await fetch(`${API_BASE}/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
    })
    if (!res.ok) throw new Error(`API error ${res.status}`)
    return res.json()
}

// ── Commit history ─────────────────────────────────────────────────

/**
 * GET /repo/commits — get commit history with energy deltas.
 * @returns {Promise<Array>}
 */
export async function fetchCommits() {
    const res = await fetch(`${API_BASE}/repo/commits`)
    if (!res.ok) throw new Error(`API error ${res.status}`)
    return res.json()
}
