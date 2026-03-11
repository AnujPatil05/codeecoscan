import CodeTable from './CodeTable.jsx'

export default function CodePanel({ title, titleCls, score, scoreCls, lines }) {
    return (
        <div className="lens-panel">
            <div className="lens-panel-header">
                <div className={`lph-title ${titleCls}`}>{title}</div>
                <div className={`lph-score ${scoreCls}`}>{score}</div>
            </div>
            <CodeTable lines={lines} />
        </div>
    )
}
