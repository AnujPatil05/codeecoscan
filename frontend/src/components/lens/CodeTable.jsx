import CodeLine from './CodeLine.jsx'

/** Table of user's code lines with heatmap overlays and warning markers. */
export default function CodeTable({ lines }) {
    return (
        <div className="code-editor">
            <table className="code-table">
                <tbody>
                    {lines.map(l => (
                        <CodeLine
                            key={l.num}
                            num={l.num}
                            rawText={l.rawText}
                            heat={l.heat}
                            hasWarn={l.hasWarn}
                            issue={l.issue}
                        />
                    ))}
                </tbody>
            </table>
        </div>
    )
}
