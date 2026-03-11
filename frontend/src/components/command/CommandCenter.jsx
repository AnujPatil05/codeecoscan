import Sidebar from './Sidebar.jsx'
import CarbonClock from './CarbonClock.jsx'
import AlertBox from './AlertBox.jsx'
import StatsRow from './StatsRow.jsx'
import CommitLog from './CommitLog.jsx'
import TopOffenders from './TopOffenders.jsx'

export default function CommandCenter({ onOpenDiff, onInitiateLens }) {
    return (
        <>
            <Sidebar />
            <div className="cmd-main">
                <div className="cmd-main-top">
                    <CarbonClock onInitiateLens={onInitiateLens} />
                    <AlertBox />
                </div>
                <StatsRow />
                <CommitLog onOpenDiff={onOpenDiff} />
            </div>
            <TopOffenders />
        </>
    )
}
