import { useState, useEffect } from 'react'

const HEAT_TIPS = {
    'heat-1': { head: 'LOW IMPACT', body: 'Minimal CPU/memory usage. Safe to run frequently.' },
    'heat-2': { head: 'MODERATE IMPACT', body: 'Some loop or call overhead. Monitor frequency.' },
    'heat-3': { head: 'HIGH IMPACT', body: 'Call inside loop or nested loop detected.' },
    'heat-4': { head: 'CRITICAL IMPACT', body: 'Deep nesting or heavy computation. Refactor recommended.' },
    'heat-5': { head: 'EXTREME IMPACT', body: 'O(N³) or worse. Immediate refactoring required.' },
}

export default function Tooltip() {
    const [tip, setTip] = useState(null)
    const [pos, setPos] = useState({ x: 0, y: 0 })

    useEffect(() => {
        const onOver = (e) => {
            const cell = e.target.closest('.line-code, .thermal-line')
            if (!cell) { setTip(null); return }
            // Check data-tip attribute first (from warning markers)
            const dataTip = cell.dataset.tip
            if (dataTip) { setTip({ head: 'ISSUE', body: dataTip }); return }
            for (const cls of Object.keys(HEAT_TIPS)) {
                if (cell.classList.contains(cls)) { setTip(HEAT_TIPS[cls]); return }
            }
            setTip(null)
        }
        const onMove = (e) => setPos({ x: e.clientX + 14, y: e.clientY - 8 })
        const onOut = (e) => { if (!e.target.closest('.line-code, .thermal-line')) setTip(null) }

        document.addEventListener('mouseover', onOver)
        document.addEventListener('mousemove', onMove)
        document.addEventListener('mouseout', onOut)
        return () => {
            document.removeEventListener('mouseover', onOver)
            document.removeEventListener('mousemove', onMove)
            document.removeEventListener('mouseout', onOut)
        }
    }, [])

    return (
        <div className={`tooltip${tip ? ' visible' : ''}`} style={{ left: pos.x, top: pos.y }}>
            {tip && <><div className="tip-head">{tip.head}</div><div>{tip.body}</div></>}
        </div>
    )
}
