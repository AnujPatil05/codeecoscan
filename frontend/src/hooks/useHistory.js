import { useState, useCallback } from 'react'
import { fetchAnalysisHistory } from '../api/client.js'

/** Hook for fetching analysis history from the database. */
export default function useHistory() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fetchHistory = useCallback(async (limit = 50) => {
        setLoading(true)
        setError(null)
        try {
            const result = await fetchAnalysisHistory(limit)
            setData(result)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [])

    return { data, loading, error, fetchHistory }
}
