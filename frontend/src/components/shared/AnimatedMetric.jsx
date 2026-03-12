import { useState, useEffect, useRef } from 'react'

export default function AnimatedMetric({ value, decimals = 0 }) {
    const isNumber = typeof value === 'number'

    // We hold the CURRENT visible number
    const [displayVal, setDisplayVal] = useState(isNumber ? value : 0)

    const requestRef = useRef()
    const previousTimeRef = useRef(null)
    const targetRef = useRef(isNumber ? value : 0)
    const startRef = useRef(isNumber ? value : 0)
    const durationMs = 500

    useEffect(() => {
        if (!isNumber) return
        if (value === targetRef.current) return

        startRef.current = displayVal
        targetRef.current = value
        previousTimeRef.current = null // reset for new animation

        const animate = (time) => {
            if (!previousTimeRef.current) previousTimeRef.current = time
            const elapsed = time - previousTimeRef.current
            const progress = Math.min(elapsed / durationMs, 1)

            // Ease out cubic
            const easeOut = 1 - Math.pow(1 - progress, 3)
            const current = startRef.current + (targetRef.current - startRef.current) * easeOut

            setDisplayVal(current)

            if (progress < 1) {
                requestRef.current = requestAnimationFrame(animate)
            } else {
                setDisplayVal(targetRef.current)
            }
        }

        requestRef.current = requestAnimationFrame(animate)
        return () => cancelAnimationFrame(requestRef.current)
    }, [value, isNumber])

    if (!isNumber) return <span>{value}</span>

    return <span>{displayVal.toFixed(decimals)}</span>
}
