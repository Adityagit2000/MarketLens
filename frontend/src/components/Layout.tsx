import { Outlet, NavLink } from 'react-router-dom'
import clsx from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Opportunities', href: '/opportunities' },
  { name: 'Positions', href: '/positions' },
  { name: 'Performance', href: '/performance' },
]

export default function Layout() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-terminal-surface border-r border-terminal-border flex flex-col">
        <div className="p-4 border-b border-terminal-border">
          <h1 className="text-lg font-bold text-terminal-text">
            Market Intelligence
          </h1>
          <p className="text-xs text-terminal-muted mt-1">Decision Engine</p>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navigation.map((item) => (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={({ isActive }) =>
                    clsx(
                      'block px-4 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-terminal-muted hover:bg-terminal-border hover:text-terminal-text'
                    )
                  }
                >
                  {item.name}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        
        <div className="p-4 border-t border-terminal-border">
          <div className="text-xs text-terminal-muted">
            <p>System Status: <span className="text-profit">Online</span></p>
            <p className="mt-1">Last Update: Just now</p>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
