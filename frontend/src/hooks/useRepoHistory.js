import { useState, useCallback } from 'react'
import { fetchCommits } from '../api/client.js'

/**
 * Hook for fetching repository commit history with energy deltas.
 * Ready to swap to real data when /repo/commits is fully implemented.
 */
export default function useRepoHistory() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fetchHistory = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const result = await fetchCommits()
            setData(result)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [])

    return { data, loading, error, fetchHistory }
}
