export function PageHeader({ eyebrow, title, description, action }) { return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div>{action}</header>; }
export function StatCard({ label, value, hint, tone = '' }) { return <article className={`stat-card ${tone}`}><span>{label}</span><strong>{value}</strong><small>{hint}</small></article>; }
export function Empty({ children }) { return <div className="empty">{children}</div>; }
export const money = (value = 0, currency = 'INR') => new Intl.NumberFormat(currency === 'INR' ? 'en-IN' : 'en-US', { style: 'currency', currency, maximumFractionDigits: 0 }).format(value);
