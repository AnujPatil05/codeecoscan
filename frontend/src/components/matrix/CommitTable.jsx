import { MATRIX_COMMITS } from '../../data/mockData.js'

export default function CommitTable({ onOpenDiff }) {
    return (
        <div className="table-area">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>SHA</th>
                        <th>FILE</th>
                        <th>MESSAGE</th>
                        <th>AUTHOR</th>
                        <th>Δ_ENERGY</th>
                        <th>CO₂ Δ (kg)</th>
                        <th>RISK</th>
                        <th>TIMESTAMP</th>
                    </tr>
                </thead>
                <tbody>
                    {MATRIX_COMMITS.map(c => (
                        <tr key={c.sha} onClick={c.hasDiff ? onOpenDiff : undefined}>
                            <td className="td-sha">{c.sha}</td>
                            <td>{c.file}</td>
                            <td>{c.msg}</td>
                            <td className="td-author">{c.author}</td>
                            <td className={`td-delta ${c.dirE}`}>{c.deltaE}</td>
                            <td className={`td-delta ${c.dirC}`}>{c.deltaCo2}</td>
                            <td><span className={`td-risk ${c.riskCls}`}>{c.risk}</span></td>
                            <td className="td-ts">{c.ts}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
