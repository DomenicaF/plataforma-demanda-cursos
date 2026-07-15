import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Admin from './pages/Admin.jsx'

function Protected({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function initials(user) {
  const base = user.full_name || user.email || '?'
  return base.trim().slice(0, 1).toUpperCase()
}

function Navbar() {
  const { user, logout } = useAuth()
  if (!user) return null
  return (
    <div className="navbar">
      <div className="brand">📊 Demanda de Cursos en Línea</div>
      <nav>
        <NavLink to="/" end>Tablero</NavLink>
        {user.role === 'administrador' && <NavLink to="/admin">Administración</NavLink>}
      </nav>
      <div className="user">
        <div className="avatar">{initials(user)}</div>
        <div>
          <div style={{ color: 'var(--text)', fontWeight: 600 }}>{user.full_name}</div>
          <div style={{ fontSize: 12 }}>{user.role}</div>
        </div>
        <button className="logout" onClick={logout}>Salir</button>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Protected><Dashboard /></Protected>} />
        <Route path="/admin" element={<Protected><Admin /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
