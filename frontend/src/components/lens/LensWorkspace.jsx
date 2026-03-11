import LensHeader from './LensHeader.jsx'
import CodePanel from './CodePanel.jsx'
import ScoreBreakdown from './ScoreBreakdown.jsx'
import { ORIGINAL_CODE, REFACTORED_CODE } from '../../data/mockData.js'

export default function LensWorkspace() {
    return (
        <>
            <LensHeader />
            <div className="lens-body">
                <CodePanel
                    title="⚠ ORIGINAL — ENERGY RISK: CRITICAL"
                    titleCls="danger"
                    score="92 / 100"
                    scoreCls="danger"
                    lines={ORIGINAL_CODE}
                />
                <CodePanel
                    title="✓ REFACTOR — ENERGY RISK: LOW"
                    titleCls="success"
                    score="23 / 100"
                    scoreCls="success"
                    lines={REFACTORED_CODE}
                />
                <ScoreBreakdown />
            </div>
        </>
    )
}
