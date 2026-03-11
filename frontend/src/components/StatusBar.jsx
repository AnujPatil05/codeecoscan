import { useLiveTime } from '../hooks/useClock.js'

export default function StatusBar() {
    const time = useLiveTime()

    return (
        <div id="statusbar">
            <div className="sb-item active">REPO <span>CODELOG-BACKEND</span></div>
            <div className="sb-item">BRANCH <span>main</span></div>
            <div className="sb-item">LOOP DEPTH <span>3</span></div>
            <div className="sb-item">RECURSION <span>NO</span></div>
            <div className="sb-item">HEAVY IMPORTS <span>2</span></div>
            <div className="sb-item sb-right">
                <span>{time}</span>
            </div>
        </div>
    )
}
