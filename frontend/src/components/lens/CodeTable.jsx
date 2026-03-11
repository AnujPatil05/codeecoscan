import CodeLine from './CodeLine.jsx'

/** Table of code lines with heatmap overlays. */
export default function CodeTable({ lines }) {
    return (
        <div className="code-editor">
            <table className="code-table">
                <tbody>
                    {lines.map(l => (
                        <CodeLine key={l.num} num={l.num} code={l.code} heat={l.heat} />
                    ))}
                </tbody>
            </table>
        </div>
    )
}
