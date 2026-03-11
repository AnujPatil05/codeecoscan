import { THERMAL_LINES } from '../../data/mockData.js'

export default function ThermalCode() {
    return (
        <div className="thermal-code-area">
            <table className="thermal-code-table">
                <tbody>
                    {THERMAL_LINES.map((l, i) => (
                        <tr key={i}>
                            <td className="thermal-gutter">
                                {l.time && (
                                    <span className={`gutter-time${l.timeCls ? ` ${l.timeCls}` : ''}`}>
                                        {l.time}
                                    </span>
                                )}
                            </td>
                            <td
                                className={`thermal-line ${l.heat}`}
                                dangerouslySetInnerHTML={{ __html: l.code || '' }}
                            />
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
