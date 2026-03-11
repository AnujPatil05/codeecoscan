/**
 * Single code line for display — supports heatmap class + warning marker.
 * rawText is plain text; no dangerouslySetInnerHTML needed for user code.
 */
export default function CodeLine({ num, rawText, heat, hasWarn, issue }) {
    return (
        <tr>
            <td className="line-num">{num}</td>
            <td className={`line-code ${heat || 'heat-0'}`}>
                {rawText || '\u00A0'}
                {hasWarn && (
                    <span
                        className="line-warn-marker"
                        title={issue ? `${issue.head || issue.type}: ${issue.body || issue.message}` : 'Issue detected'}
                    >
                        ⚠
                    </span>
                )}
            </td>
        </tr>
    )
}
