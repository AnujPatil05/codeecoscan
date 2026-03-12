import '../../styles/lens.css'
import { useState, useRef } from 'react'

const SAMPLE_CODE = `import torch
import pandas as pd
import numpy as np

def train(data):
    results = []
    for batch in data:
        for sample in batch:
            for elem in sample:
                processed = abs(elem)
                results.append(processed)
    return results

def load_data(path):
    df = pd.read_csv(path)
    df_copy = df.copy()
    return df_copy.values.tolist()
`

export default function InputPanel({ sharedCode, setSharedCode, onAnalyze, onScanRepo, loading, error }) {
    const [tab, setTab] = useState('paste')  // 'paste' | 'upload' | 'repo'
    // Fallback if sharedCode is somehow empty on first load, though we'll handle this in App or Workspace
    const currentCode = sharedCode || ''
    const [repoUrl, setRepoUrl] = useState('')
    const [dragOver, setDragOver] = useState(false)
    const fileRef = useRef(null)

    const handleAnalyze = () => {
        if (tab === 'paste' && currentCode.trim()) onAnalyze(currentCode)
        if (tab === 'repo' && repoUrl.trim() && onScanRepo) onScanRepo(repoUrl.trim())
    }

    const handleFile = (file) => {
        if (!file) return
        const reader = new FileReader()
        reader.onload = (e) => {
            const text = e.target.result
            setSharedCode(text)
            setTab('paste')
            onAnalyze(text)
        }
        reader.readAsText(file)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragOver(false)
        const file = e.dataTransfer.files[0]
        if (file && file.name.endsWith('.py')) handleFile(file)
    }

    const activeCode = tab === 'paste' ? currentCode : ''
    const canAnalyze = (tab === 'paste' && currentCode.trim()) || (tab === 'repo' && repoUrl.trim())

    return (
        <div className="input-panel">
            <div className="panel-header">INPUT</div>

            {/* Tabs */}
            <div className="input-tabs">
                {[['paste', 'PASTE CODE'], ['upload', 'UPLOAD .PY'], ['repo', 'GITHUB REPO']].map(([id, label]) => (
                    <div
                        key={id}
                        className={`input-tab${tab === id ? ' active' : ''}`}
                        onClick={() => setTab(id)}
                    >
                        {label}
                    </div>
                ))}
            </div>

            {/* Body */}
            <div className="input-body">

                {/* Paste tab */}
                {tab === 'paste' && (
                    <textarea
                        className="code-textarea"
                        value={currentCode}
                        onChange={e => setSharedCode(e.target.value)}
                        placeholder="# Paste Python code here…"
                        spellCheck={false}
                    />
                )}

                {/* Upload tab */}
                {tab === 'upload' && (
                    <div
                        className={`upload-zone${dragOver ? ' drag-over' : ''}`}
                        onClick={() => fileRef.current?.click()}
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleDrop}
                    >
                        <div className="upload-icon">⊕</div>
                        <div className="upload-label">
                            <span>DROP .PY FILE</span>
                            or click to select
                        </div>
                        <input
                            ref={fileRef}
                            type="file"
                            accept=".py"
                            className="upload-input"
                            onChange={e => handleFile(e.target.files[0])}
                        />
                    </div>
                )}

                {/* Repo tab */}
                {tab === 'repo' && (
                    <div className="repo-input-wrap">
                        <div className="repo-url-label">GITHUB REPOSITORY URL</div>
                        <input
                            type="text"
                            className="repo-url-field"
                            placeholder="https://github.com/user/repo"
                            value={repoUrl}
                            onChange={e => setRepoUrl(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && canAnalyze && handleAnalyze()}
                        />
                        <div style={{ fontSize: 10, color: 'var(--muted)' }}>
                            Scans all .py files and aggregates energy risk scores.
                        </div>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="input-footer">
                {tab === 'paste' && (
                    <div className="char-count">{currentCode.length} chars · {currentCode.split('\n').length} lines</div>
                )}
                {error && <div className="api-error">⚠ {error}</div>}
                <div className="analysis-status">
                    <div className={`status-dot${loading ? ' loading' : ''}`} />
                    {loading ? (tab === 'repo' ? 'SCANNING REPO…' : 'ANALYZING…') : 'READY'}
                </div>
                <button
                    className={`analyze-btn${loading ? ' loading' : ''}`}
                    onClick={handleAnalyze}
                    disabled={!canAnalyze || loading}
                >
                    {loading ? (tab === 'repo' ? '▶ SCANNING REPO…' : '▶ ANALYZING…') : '▶ ANALYZE'}
                </button>
            </div>
        </div>
    )
}
