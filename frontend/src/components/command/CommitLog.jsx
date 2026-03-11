import { COMMIT_LOG } from '../../data/mockData.js'

export default function CommitLog({ onOpenDiff }) {
    return (
        <div className="cmd-log-area">
            <div className="log-header">RECENT COMMIT TELEMETRY — CLICK ROW FOR DIFF</div>
            {COMMIT_LOG.map((c, i) => (
                <div key={i} className="log-entry" onClick={c.hasDiff ? onOpenDiff : undefined}>
                    <span className="log-ts">{c.ts}</span>
                    <span className="log-sha">{c.sha}</span>
                    <span className="log-msg">{c.msg}</span>
                    <span className="log-author">{c.author}</span>
                    <span className={`log-delta ${c.dir}`}>{c.delta}</span>
                </div>
            ))}
        </div>
    )
}
