/* ═══════════════════════════════════════════════════════
   Mock data matching the reference HTML exactly.
   Structured so hooks can swap to live API later.
═══════════════════════════════════════════════════════ */

// ── Screen 1: Command Center ────────────────────────

export const REPOS = [
    { name: 'codelog-backend', active: true },
    { name: 'devconnect-api' },
    { name: 'fintrace-core' },
    { name: 'ml-pipeline' },
    { name: 'data-preprocessor' },
]

export const ALERTS = [
    { text: 'train.py: O(N³) LOOP', tag: 'CRITICAL' },
    { text: 'model.py: FULL TENSOR COPY', tag: 'CRITICAL' },
    { text: 'pipeline.py: BLOCKING I/O', tag: 'HIGH', warn: true },
    { text: 'utils.py: REDUNDANT RECOMPUTE', tag: 'HIGH', warn: true },
]

export const STATS = [
    { label: 'ENERGY RISK SCORE', val: '67', sub: '/ 100 — HIGH', cls: 'danger' },
    { label: 'FILES SCANNED', val: '142', sub: 'LAST SCAN: 4m AGO', cls: '' },
    { label: 'ENERGY / DAY', val: '48.3', sub: 'WH / DAY', cls: 'warn' },
    { label: 'CO₂ SAVED (MTD)', val: '0.84', sub: 'KG — 12 REFACTORS', cls: 'green' },
]

export const COMMIT_LOG = [
    { ts: '14:32:01', sha: 'a3f2c91', msg: 'feat: add batch processing to training loop', author: '@anuj', delta: '+34%', dir: 'up', hasDiff: true },
    { ts: '13:11:44', sha: 'b7e1d03', msg: 'refactor: vectorize sample processing with numpy', author: '@anuj', delta: '-22%', dir: 'down' },
    { ts: '12:58:20', sha: 'c9a4f77', msg: 'fix: remove duplicate DataFrame copy in pipeline', author: '@anuj', delta: '-11%', dir: 'down' },
    { ts: '11:45:03', sha: 'd2b8c12', msg: 'feat: add tensorflow model export functionality', author: '@anuj', delta: '+18%', dir: 'up' },
    { ts: '10:20:55', sha: 'e5f3a48', msg: 'chore: update requirements, add torch 2.1', author: '@anuj', delta: '+7%', dir: 'up' },
    { ts: '09:04:17', sha: 'f1c6d90', msg: 'refactor: replace nested loop with list comprehension', author: '@anuj', delta: '-41%', dir: 'down' },
    { ts: '08:33:02', sha: 'a0e9b34', msg: 'feat: add model caching layer to reduce redundancy', author: '@anuj', delta: '-19%', dir: 'down' },
    { ts: 'YESTERDAY', sha: '9d7f201', msg: 'perf: lazy-load heavy imports behind function gate', author: '@anuj', delta: '-28%', dir: 'down' },
]

export const TOP_FILES = [
    { name: 'train.py', score: 92, color: 'var(--danger)', glow: 'var(--glow-danger)' },
    { name: 'model.py', score: 78, color: 'var(--danger)' },
    { name: 'pipeline.py', score: 61, color: 'var(--warning)' },
    { name: 'utils.py', score: 44, color: 'var(--warning)' },
    { name: 'data_loader.py', score: 29, color: 'var(--primary)', glow: 'var(--glow-primary)' },
]

export const SPARKLINE_POINTS = '0,45 36,38 72,50 108,30 144,22 180,15 216,18'
export const SPARKLINE_POLYGON = '0,55 0,45 36,38 72,50 108,30 144,22 180,15 216,18 216,55'

// ── Screen 2: Lens Workspace ────────────────────────

export const ORIGINAL_CODE = [
    { num: 1, code: '<span class="kw">import</span> <span class="nm">torch</span>', heat: 'heat-3' },
    { num: 2, code: '<span class="kw">import</span> <span class="nm">pandas</span> <span class="kw">as</span> <span class="nm">pd</span>', heat: 'heat-3' },
    { num: 3, code: '<span class="kw">import</span> <span class="nm">numpy</span> <span class="kw">as</span> <span class="nm">np</span>', heat: 'heat-0' },
    { num: 4, code: '', heat: 'heat-0' },
    { num: 5, code: '<span class="kw">def</span> <span class="fn">train</span>(data):', heat: 'heat-1' },
    { num: 6, code: '    results = []', heat: 'heat-1' },
    { num: 7, code: '    <span class="kw">for</span> batch <span class="kw">in</span> data:   <span class="cm"># O(N)</span>', heat: 'heat-2' },
    { num: 8, code: '        <span class="kw">for</span> sample <span class="kw">in</span> batch:  <span class="cm"># O(N²) ⚠</span>', heat: 'heat-4', tip: 'heat-4' },
    { num: 9, code: '            <span class="kw">for</span> elem <span class="kw">in</span> sample:  <span class="cm"># O(N³) !</span>', heat: 'heat-5', tip: 'heat-5' },
    { num: 10, code: '                processed = <span class="bi">abs</span>(elem)', heat: 'heat-5' },
    { num: 11, code: '                results.<span class="bi">append</span>(processed)', heat: 'heat-4' },
    { num: 12, code: '    <span class="kw">return</span> results', heat: 'heat-0' },
    { num: 13, code: '', heat: 'heat-0' },
    { num: 14, code: '<span class="kw">def</span> <span class="fn">load_data</span>(path):', heat: 'heat-2' },
    { num: 15, code: '    df = <span class="nm">pd</span>.<span class="bi">read_csv</span>(path)', heat: 'heat-3' },
    { num: 16, code: '    df_copy = df.<span class="bi">copy</span>()  <span class="cm"># UNNECESSARY COPY</span>', heat: 'heat-4', tip: 'heat-3' },
    { num: 17, code: '    <span class="kw">return</span> df_copy.<span class="bi">values</span>.<span class="bi">tolist</span>()', heat: 'heat-3' },
]

export const REFACTORED_CODE = [
    { num: 1, code: '<span class="kw">import</span> <span class="nm">torch</span>  <span class="cm"># lazy-loaded</span>', heat: 'fix-1' },
    { num: 2, code: '<span class="kw">import</span> <span class="nm">numpy</span> <span class="kw">as</span> <span class="nm">np</span>', heat: 'fix-1' },
    { num: 3, code: '', heat: 'heat-0' },
    { num: 4, code: '', heat: 'heat-0' },
    { num: 5, code: '<span class="kw">def</span> <span class="fn">train</span>(data):', heat: 'fix-2' },
    { num: 6, code: '    <span class="cm"># Vectorized — eliminates O(N³) loop</span>', heat: 'fix-2' },
    { num: 7, code: '    arr = <span class="nm">np</span>.<span class="bi">concatenate</span>(', heat: 'fix-2' },
    { num: 8, code: '        [<span class="nm">np</span>.<span class="bi">array</span>(b).<span class="bi">flatten</span>() <span class="kw">for</span> b <span class="kw">in</span> data]', heat: 'fix-2' },
    { num: 9, code: '    )', heat: 'fix-2' },
    { num: 10, code: '    <span class="kw">return</span> <span class="nm">np</span>.<span class="bi">abs</span>(arr).<span class="bi">tolist</span>()', heat: 'fix-2' },
    { num: 11, code: '', heat: 'heat-0' },
    { num: 12, code: '', heat: 'heat-0' },
    { num: 13, code: '', heat: 'heat-0' },
    { num: 14, code: '<span class="kw">def</span> <span class="fn">load_data</span>(path):', heat: 'fix-1' },
    { num: 15, code: '    <span class="cm"># No copy — direct array extraction</span>', heat: 'fix-1' },
    { num: 16, code: '    <span class="kw">return</span> <span class="nm">np</span>.<span class="bi">genfromtxt</span>(path, delimiter=<span class="st">\',\'</span>)', heat: 'fix-2' },
    { num: 17, code: '', heat: 'heat-0' },
]

export const LENS_BREAKDOWN = [
    { name: 'LOOP DEPTH', score: '+35 → +0', cls: 'danger', barPct: 0, barColor: 'var(--primary)', barGlow: 'var(--glow-primary)', desc: 'O(N³) nested loops eliminated via numpy vectorization. Estimated 200x speedup on large batches.' },
    { name: 'HEAVY IMPORTS', score: '+16 → +8', cls: 'warn', barPct: 35, barColor: 'var(--warning)', desc: 'pandas removed. torch retained but lazily invoked. numpy kept — necessary for vectorization.' },
    { name: 'MEMORY COPIES', score: '+18 → +0', cls: 'danger', barPct: 0, barColor: 'var(--primary)', barGlow: 'var(--glow-primary)', desc: 'DataFrame .copy() call removed. Direct numpy extraction reduces peak memory by ~50%.' },
    { name: 'INTERACTION', score: '+15 → +15', cls: 'ok', barPct: 60, barColor: 'var(--warning)', desc: 'I/O pattern unchanged. File reads still blocking — consider async I/O for further optimization.' },
    { name: 'RECURSION', score: '+0', cls: 'ok', barPct: 0, barColor: 'var(--muted)', desc: 'No recursive calls detected in either version.' },
]

// ── Screen 3: Thermal Heatmap ───────────────────────

export const THERMAL_LINES = [
    { time: '0.1ms', timeCls: 'low', code: '<span class="kw">import</span> torch', heat: 'heat-0' },
    { time: '0.2ms', timeCls: 'low', code: '<span class="kw">import</span> pandas <span class="kw">as</span> pd', heat: 'heat-1' },
    { time: '—', timeCls: 'low', code: '<span class="kw">import</span> numpy <span class="kw">as</span> np', heat: 'heat-0' },
    { time: '', timeCls: '', code: '', heat: 'heat-0' },
    { time: '—', timeCls: 'low', code: '<span class="kw">def</span> <span class="fn">train</span>(data):', heat: 'heat-0' },
    { time: '0.1ms', timeCls: 'low', code: '    results = []', heat: 'heat-0' },
    { time: '12ms', timeCls: 'med', code: '    <span class="kw">for</span> batch <span class="kw">in</span> data:', heat: 'heat-2' },
    { time: '148ms', timeCls: '', code: '        <span class="kw">for</span> sample <span class="kw">in</span> batch:', heat: 'heat-4' },
    { time: '450ms', timeCls: '', code: '            <span class="kw">for</span> elem <span class="kw">in</span> sample:', heat: 'heat-5' },
    { time: '450ms', timeCls: '', code: '                processed = <span class="bi">abs</span>(elem)', heat: 'heat-5' },
    { time: '380ms', timeCls: '', code: '                results.<span class="bi">append</span>(processed)', heat: 'heat-4' },
    { time: '0.1ms', timeCls: 'low', code: '    <span class="kw">return</span> results', heat: 'heat-0' },
    { time: '', timeCls: '', code: '', heat: 'heat-0' },
    { time: '—', timeCls: 'low', code: '<span class="kw">def</span> <span class="fn">load_data</span>(path):', heat: 'heat-0' },
    { time: '32ms', timeCls: 'med', code: '    df = pd.<span class="bi">read_csv</span>(path)', heat: 'heat-2' },
    { time: '85ms', timeCls: 'med', code: '    df_copy = df.<span class="bi">copy</span>()  <span class="cm"># MEMORY SPIKE</span>', heat: 'heat-3' },
    { time: '28ms', timeCls: 'med', code: '    <span class="kw">return</span> df_copy.<span class="bi">values</span>.<span class="bi">tolist</span>()', heat: 'heat-2' },
]

export const FUNCTIONS = [
    { name: 'train()', lines: 'LINES 5–12', cost: '1.42 μWh/call', barPct: 95, barColor: 'var(--danger)', barGlow: 'var(--glow-danger)', active: true },
    { name: 'load_data()', lines: 'LINES 14–17', cost: '0.38 μWh/call', barPct: 38, barColor: 'var(--warning)' },
    { name: 'preprocess()', lines: 'LINES 20–26', cost: '0.12 μWh/call', barPct: 18, barColor: 'var(--primary)' },
    { name: 'validate()', lines: 'LINES 28–33', cost: '0.04 μWh/call', barPct: 6, barColor: 'var(--primary)' },
]

export const HEAT_METRICS = [
    { label: 'TOTAL TIME', val: '1.44s' },
    { label: 'PEAK MEM', val: '412 MB', fontSize: '14px' },
    { label: 'CRITICAL', val: '3 LINES' },
    { label: 'ENERGY', val: '1.80 μWh', fontSize: '13px' },
]

// ── Screen 4: Emission Matrix ───────────────────────

export const MATRIX_COMMITS = [
    { sha: 'a3f2c91', file: 'train.py', msg: 'feat: add batch processing', author: '@anuj', deltaE: '+34%', deltaCo2: '+0.021', dirE: 'up', dirC: 'up', risk: 'HIGH', riskCls: 'high', ts: '2026-03-11 14:32', hasDiff: true },
    { sha: 'b7e1d03', file: 'utils.py', msg: 'refactor: vectorize processing', author: '@anuj', deltaE: '-22%', deltaCo2: '-0.014', dirE: 'down', dirC: 'down', risk: 'MED', riskCls: 'med', ts: '2026-03-11 13:11' },
    { sha: 'c9a4f77', file: 'pipeline.py', msg: 'fix: remove DataFrame copy', author: '@anuj', deltaE: '-11%', deltaCo2: '-0.007', dirE: 'down', dirC: 'down', risk: 'LOW', riskCls: 'low', ts: '2026-03-11 12:58' },
    { sha: 'd2b8c12', file: 'model.py', msg: 'feat: tensorflow export', author: '@anuj', deltaE: '+18%', deltaCo2: '+0.011', dirE: 'up', dirC: 'up', risk: 'HIGH', riskCls: 'high', ts: '2026-03-11 10:20' },
    { sha: 'f1c6d90', file: 'train.py', msg: 'refactor: list comprehension', author: '@anuj', deltaE: '-41%', deltaCo2: '-0.026', dirE: 'down', dirC: 'down', risk: 'LOW', riskCls: 'low', ts: '2026-03-11 09:04' },
    { sha: 'a0e9b34', file: 'model.py', msg: 'feat: model caching layer', author: '@anuj', deltaE: '-19%', deltaCo2: '-0.012', dirE: 'down', dirC: 'down', risk: 'LOW', riskCls: 'low', ts: '2026-03-11 08:33' },
    { sha: '9d7f201', file: 'pipeline.py', msg: 'perf: lazy-load heavy imports', author: '@anuj', deltaE: '-28%', deltaCo2: '-0.018', dirE: 'down', dirC: 'down', risk: 'LOW', riskCls: 'low', ts: '2026-03-10 17:44' },
    { sha: '8c3e512', file: 'data_loader.py', msg: 'chore: update requirements', author: '@anuj', deltaE: '+7%', deltaCo2: '+0.004', dirE: 'up', dirC: 'up', risk: 'MED', riskCls: 'med', ts: '2026-03-10 14:22' },
]

export const DIFF_DATA = {
    sha: 'a3f2c91',
    lines: [
        { type: 'ctx', text: '--- a/train.py' },
        { type: 'ctx', text: '+++ b/train.py' },
        { type: 'ctx', text: '@@ -5,8 +5,10 @@' },
        { type: 'ctx', text: ' def train(data):' },
        { type: 'ctx', text: '     results = []' },
        { type: 'rem', text: '-    for batch in data:' },
        { type: 'rem', text: '-        processed = abs(batch)' },
        { type: 'rem', text: '-        results.append(processed)' },
        { type: 'add', text: '+    for batch in data:             # O(N)' },
        { type: 'add', text: '+        for sample in batch:        # O(N²)' },
        { type: 'add', text: '+            for elem in sample:     # O(N³) ⚠' },
        { type: 'add', text: '+                processed = abs(elem)' },
        { type: 'add', text: '+                results.append(processed)' },
        { type: 'ctx', text: '     return results' },
    ],
    impact: '+34% / +0.021 kgCO₂',
    risk: 'HIGH',
}

// ── Tooltip definitions ────────────────────────────

export const HEAT_TIPS = {
    'heat-4': { head: 'O(N²) DETECTED', body: 'Quadratic complexity. Estimated: 0.38 μWh / invocation on 1K batch.' },
    'heat-5': { head: 'O(N³) — CRITICAL', body: 'Cubic complexity. Eliminates ~200x with vectorization. CO₂: 1.2 μWh/call.' },
    'heat-3': { head: 'HIGH MEMORY ALLOC', body: 'DataFrame .copy() doubles peak memory. Consider in-place operations.' },
}
