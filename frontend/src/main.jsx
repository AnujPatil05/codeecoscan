import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/terminal.css'
import './styles/lens.css'
import './styles/mobile.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <App />
    </StrictMode>,
)
