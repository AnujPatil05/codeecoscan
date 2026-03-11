import { useState, useCallback } from 'react'
import { profileCode } from '../api/client.js'

/**
 * Hook for profiling code execution cost.
 * Ready to swap to real implementation when /profile is fully implemented.
 */
export default function useProfiling() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const profile = useCallback(async (code) => {
        if (!code?.trim()) return
        setLoading(true)
        setError(null)
        try {
            const result = await profileCode(code)
            setData(result)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [])

    return { data, loading, error, profile }
}
