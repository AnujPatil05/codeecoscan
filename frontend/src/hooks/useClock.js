import { useState, useEffect, useRef } from 'react'

/** Ticking carbon clock — increments 0.00001 every 80ms. */
export function useCarbonClock(initial = 4.892) {
    const [val, setVal] = useState(initial)
    const ref = useRef(initial)

    useEffect(() => {
        const id = setInterval(() => {
            ref.current += 0.00001
            setVal(ref.current)
        }, 80)
        return () => clearInterval(id)
    }, [])

    return val.toFixed(3).padStart(7, '0')
}

/** Live wall clock — updates every second. */
export function useLiveTime() {
    const [time, setTime] = useState('')
    useEffect(() => {
        const tick = () => {
            const now = new Date()
            setTime(now.toTimeString().split(' ')[0] + ' UTC+5:30')
        }
        tick()
        const id = setInterval(tick, 1000)
        return () => clearInterval(id)
    }, [])
    return time
}
