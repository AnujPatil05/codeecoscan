import { useState, useCallback, useRef } from 'react'
import { submitRepoScan, pollJob } from '../api/client.js'

const POLL_INTERVAL_MS = 2000

/**
 * Hook for repo scanning with async job polling.
 * 1. submitRepoScan() → {job_id}
 * 2. poll GET /jobs/{job_id} every 2s until status == 'done' | 'error'
 */
export default function useRepoSummary() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [status, setStatus] = useState('')   // 'queued' | 'running' | 'done' | 'error'
    const [error, setError] = useState(null)
    const [elapsed, setElapsed] = useState(0)
    const pollRef = useRef(null)

    const _stopPoll = () => { if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null } }

    const fetchSummary = useCallback(async (repoUrl) => {
        if (!repoUrl?.trim()) return
        _stopPoll()
        setLoading(true)
        setError(null)
        setData(null)
        setStatus('queued')

        let job
        try {
            job = await submitRepoScan(repoUrl)
        } catch (err) {
            setError(err.message)
            setLoading(false)
            return
        }

        const jobId = job.job_id
        pollRef.current = setInterval(async () => {
            try {
                const s = await pollJob(jobId)
                setStatus(s.status)
                setElapsed(s.elapsed_s)

                if (s.status === 'done') {
                    _stopPoll()
                    setData(s.result)
                    setLoading(false)
                } else if (s.status === 'error') {
                    _stopPoll()
                    setError(s.error || 'Scan failed')
                    setLoading(false)
                }
            } catch (err) {
                _stopPoll()
                setError(err.message)
                setLoading(false)
            }
        }, POLL_INTERVAL_MS)
    }, [])

    return { data, loading, status, elapsed, error, fetchSummary }
}
