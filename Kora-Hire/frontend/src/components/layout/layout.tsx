import "./layout.css";

// Layout.tsx
const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="app-shell">
    <div className="page-wrapper">
      <main className="main-content">
        {children}
      </main>
    </div>
  </div>
);

export default Layout