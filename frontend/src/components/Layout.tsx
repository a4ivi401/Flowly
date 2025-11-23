import type { ReactNode } from 'react'

type LayoutProps = {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="dot" />
          <span className="brand-name">AI Time Manager</span>
        </div>
        <nav className="nav-links">
          <a href="#tasks">Tasks</a>
          <a href="#today">Today</a>
        </nav>
      </header>
      <main className="app-content">{children}</main>
    </div>
  )
}

export default Layout
