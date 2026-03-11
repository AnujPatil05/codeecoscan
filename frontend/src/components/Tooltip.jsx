import { useState, useEffect, useRef } from 'react'
import { HEAT_TIPS } from '../data/mockData.js'

export default function Tooltip() {
    const [tip, setTip] = useState(null)
    const [pos, setPos] = useState({ x: 0, y: 0 })
    const ref = useRef(null)

    useEffect(() => {
        const onOver = (e) => {
            const cell = e.target.closest('.line-code, .thermal-line')
            if (!cell) { setTip(null); return }
            for (const cls in HEAT_TIPS) {
                if (cell.classList.contains(cls)) {
                    setTip(HEAT_TIPS[cls])
                    return
                }
            }
            setTip(null)
        }

        const onMove = (e) => {
            setPos({ x: e.clientX + 14, y: e.clientY - 8 })
        }

        const onOut = (e) => {
            if (!e.target.closest('.line-code, .thermal-line')) setTip(null)
        }

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
        <div
            ref={ref}
            className={`tooltip${tip ? ' visible' : ''}`}
            style={{ left: pos.x, top: pos.y }}
        >
            {tip && (
                <>
                    <div className="tip-head">{tip.head}</div>
                    <div>{tip.body}</div>
                </>
            )}
        </div>
    )
}
