/** Single code line that supports heat classes and tooltip integration. */
export default function CodeLine({ num, code, heat }) {
    return (
        <tr>
            <td className="line-num">{num}</td>
            <td
                className={`line-code ${heat || 'heat-0'}`}
                dangerouslySetInnerHTML={{ __html: code || '' }}
            />
        </tr>
    )
}
