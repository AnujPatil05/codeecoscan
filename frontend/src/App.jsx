import { useState, useEffect, useCallback } from 'react'
import Nav from './components/Nav.jsx'
import StatusBar from './components/StatusBar.jsx'
import Modal from './components/Modal.jsx'
import Tooltip from './components/Tooltip.jsx'
import CommandCenter from './components/command/CommandCenter.jsx'
import LensWorkspace from './components/lens/LensWorkspace.jsx'
import ThermalHeatmap from './components/thermal/ThermalHeatmap.jsx'
import EmissionMatrix from './components/matrix/EmissionMatrix.jsx'

const SCREENS = ['command', 'lens', 'thermal', 'matrix']

export default function App() {
    const [screen, setScreen] = useState('command')
    const [modalOpen, setModalOpen] = useState(false)

    const openDiff = useCallback(() => setModalOpen(true), [])
    const closeDiff = useCallback(() => setModalOpen(false), [])

    const switchScreen = useCallback((id) => {
        setScreen(id)
    }, [])

    // Keyboard shortcuts: CTRL+1–4 switch screens, ESC closes modal
    useEffect(() => {
        const handler = (e) => {
            if (e.ctrlKey && e.key >= '1' && e.key <= '4') {
                e.preventDefault()
                switchScreen(SCREENS[parseInt(e.key) - 1])
            }
            if (e.key === 'Escape') closeDiff()
        }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [switchScreen, closeDiff])

    return (
        <>
            <Nav activeScreen={screen} onSwitch={switchScreen} />

            <div id="screen-command" className={`screen${screen === 'command' ? ' active' : ''}`}>
                <CommandCenter
                    onOpenDiff={openDiff}
                    onInitiateLens={() => switchScreen('lens')}
                />
            </div>

            <div id="screen-lens" className={`screen${screen === 'lens' ? ' active' : ''}`}>
                {screen === 'lens' && <LensWorkspace />}
            </div>

            <div id="screen-thermal" className={`screen${screen === 'thermal' ? ' active' : ''}`}>
                {screen === 'thermal' && <ThermalHeatmap />}
            </div>

            <div id="screen-matrix" className={`screen${screen === 'matrix' ? ' active' : ''}`}>
                {screen === 'matrix' && <EmissionMatrix onOpenDiff={openDiff} />}
            </div>

            <StatusBar />
            <Modal isOpen={modalOpen} onClose={closeDiff} />
            <Tooltip />
        </>
    )
}
