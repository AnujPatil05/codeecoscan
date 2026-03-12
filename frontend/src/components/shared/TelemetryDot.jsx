export default function TelemetryDot({ color = 'var(--primary)', style = {} }) {
    return (
        <span
            className="telemetry-dot"
            style={{
                display: 'inline-block',
                width: 6,
                height: 6,
                borderRadius: '50%',
                backgroundColor: color,
                color: color, /* for box-shadow currentcolor */
                animation: 'telemetry-pulse 1.6s infinite ease-in-out',
                marginRight: 6,
                verticalAlign: 'middle',
                flexShrink: 0,
                ...style
            }}
        />
    )
}
