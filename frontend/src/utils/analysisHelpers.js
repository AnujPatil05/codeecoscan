/**
 * Maps API risk_breakdown to display-ready breakdown items.
 * Each item drives the ScoreBreakdown panel.
 */
export function breakdownFromAPI(riskBreakdown, features) {
    const { loop_score = 0, interaction_penalty = 0, recursion = 0, heavy_imports = 0 } = riskBreakdown || {}
    const maxScore = Math.max(loop_score, interaction_penalty, recursion, heavy_imports, 1)

    return [
        {
            name: 'LOOP DEPTH',
            score: `+${loop_score}`,
            cls: loop_score > 30 ? 'danger' : loop_score > 10 ? 'warn' : 'ok',
            barPct: (loop_score / maxScore) * 100,
            barColor: loop_score > 30 ? 'var(--danger)' : loop_score > 10 ? 'var(--warning)' : 'var(--primary)',
            desc: features?.has_nested_loops
                ? `Nested loops detected (depth ${features.max_loop_depth}). Consider NumPy vectorization.`
                : 'No nested loops detected.',
        },
        {
            name: 'INTERACTION',
            score: `+${interaction_penalty}`,
            cls: interaction_penalty > 20 ? 'danger' : interaction_penalty > 8 ? 'warn' : 'ok',
            barPct: (interaction_penalty / maxScore) * 100,
            barColor: interaction_penalty > 20 ? 'var(--danger)' : interaction_penalty > 8 ? 'var(--warning)' : 'var(--primary)',
            desc: features?.function_calls_inside_loops
                ? 'Function calls inside loops detected. Consider caching or hoisting.'
                : 'No function calls inside loops.',
        },
        {
            name: 'RECURSION',
            score: `+${recursion}`,
            cls: recursion > 10 ? 'danger' : recursion > 0 ? 'warn' : 'ok',
            barPct: (recursion / maxScore) * 100,
            barColor: recursion > 10 ? 'var(--danger)' : recursion > 0 ? 'var(--warning)' : 'var(--muted)',
            desc: features?.has_recursion
                ? 'Direct recursion detected. Verify stack depth and add memoization.'
                : 'No recursive calls detected.',
        },
        {
            name: 'HEAVY IMPORTS',
            score: `+${heavy_imports}`,
            cls: heavy_imports > 15 ? 'danger' : heavy_imports > 5 ? 'warn' : 'ok',
            barPct: (heavy_imports / maxScore) * 100,
            barColor: heavy_imports > 15 ? 'var(--danger)' : heavy_imports > 5 ? 'var(--warning)' : 'var(--primary)',
            desc: features?.heavy_imports_detected?.length
                ? `Detected: ${features.heavy_imports_detected.join(', ')}. Verify GPU/ML usage is required.`
                : 'No energy-heavy imports detected.',
        },
    ]
}

/**
 * Maps API issues array to heatmap class per line number.
 * Returns { lineNumber: heatClass } map.
 */
export function heatMapFromIssues(issues, totalLines) {
    const map = {}
    for (const issue of (issues || [])) {
        const existing = map[issue.line]
        const incoming = severityToHeat(issue.severity)
        if (!existing || heatLevel(incoming) > heatLevel(existing)) {
            map[issue.line] = incoming
        }
    }
    return map
}

function severityToHeat(severity) {
    switch (severity) {
        case 'high': return 'heat-5'
        case 'medium': return 'heat-3'
        case 'low': return 'heat-1'
        default: return 'heat-0'
    }
}

function heatLevel(cls) {
    const map = { 'heat-0': 0, 'heat-1': 1, 'heat-2': 2, 'heat-3': 3, 'heat-4': 4, 'heat-5': 5 }
    return map[cls] ?? 0
}

/**
 * Converts issue list to tooltip map: { lineNumber: {head, body} }
 */
export function tooltipMapFromIssues(issues) {
    const map = {}
    const TYPE_LABELS = {
        nested_loop: 'NESTED LOOP DETECTED',
        call_in_loop: 'CALL INSIDE LOOP',
        heavy_import: 'HEAVY IMPORT',
        recursion: 'RECURSION DETECTED',
    }
    for (const issue of (issues || [])) {
        if (!map[issue.line]) {
            map[issue.line] = { head: TYPE_LABELS[issue.type] || issue.type, body: issue.message }
        }
    }
    return map
}

/**
 * Converts raw source code into line objects for CodeTable.
 * Applies heat class and warning marker from issue maps.
 */
export function codeLinesToDisplay(code, heatMap, issueMap) {
    if (!code) return []
    return code.split('\n').map((text, i) => {
        const lineNum = i + 1
        const heat = heatMap[lineNum] || 'heat-0'
        const hasWarn = !!issueMap[lineNum]
        return { num: lineNum, rawText: text, heat, hasWarn, issue: issueMap[lineNum] }
    })
}

/**
 * Generate rule-based optimization suggestions from API response.
 */
export function generateSuggestions(features, issues) {
    const sugs = []
    const issueTypes = new Set((issues || []).map(i => i.type))

    if (issueTypes.has('nested_loop') || features?.has_nested_loops) {
        const depth = features?.max_loop_depth || 2
        sugs.push({
            title: `Nested loops detected (depth ${depth}) — O(N^${depth}) complexity`,
            detail: 'Consider NumPy vectorization or list comprehensions to eliminate the inner loop.',
            severity: 'high',
        })
    }
    if (issueTypes.has('call_in_loop') || features?.function_calls_inside_loops) {
        sugs.push({
            title: 'Function calls inside loops',
            detail: 'Cache return values outside the loop, or use vectorized equivalents (numpy.vectorize, map).',
            severity: 'medium',
        })
    }
    if (issueTypes.has('heavy_import') && features?.heavy_imports_detected?.length) {
        sugs.push({
            title: `Heavy libraries: ${features.heavy_imports_detected.join(', ')}`,
            detail: 'Verify GPU/ML acceleration is actually needed. Consider lazy imports or lightweight alternatives.',
            severity: 'medium',
        })
    }
    if (issueTypes.has('recursion') || features?.has_recursion) {
        sugs.push({
            title: 'Recursive function detected',
            detail: 'Add memoization (functools.lru_cache) or convert to iterative if stack depth is large.',
            severity: features?.recursion_inside_loop ? 'high' : 'medium',
        })
    }
    if (sugs.length === 0) {
        sugs.push({ title: 'No significant issues detected', detail: 'Code looks energy-efficient. Continue monitoring on new changes.', severity: 'low' })
    }
    return sugs
}
