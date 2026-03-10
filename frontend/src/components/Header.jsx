export default function Header() {
    return (
        <header className="header">
            <div className="header__wordmark">
                Code<span>Eco</span>Scan
            </div>
            <div className="header__tag">Energy Diagnostic</div>
            <div className="header__api">
                API:{' '}
                <a href="https://codeecoscan.onrender.com/docs" target="_blank" rel="noreferrer">
                    codeecoscan.onrender.com
                </a>
            </div>
        </header>
    )
}
