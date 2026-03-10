import MonacoEditor from '@monaco-editor/react'

const MONACO_OPTIONS = {
    fontSize: 13,
    fontFamily: "'IBM Plex Mono', monospace",
    lineNumbers: 'on',
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    padding: { top: 16, bottom: 16 },
    renderLineHighlight: 'none',
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    scrollbar: { vertical: 'auto', horizontal: 'hidden' },
    wordWrap: 'on',
}

export default function Editor({ value, onChange }) {
    return (
        <MonacoEditor
            height="100%"
            defaultLanguage="python"
            value={value}
            onChange={onChange}
            theme="vs-dark"
            options={MONACO_OPTIONS}
        />
    )
}
