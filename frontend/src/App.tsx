import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { FacultiesPage } from './pages/FacultiesPage'
import { FacultyDetailPage } from './pages/FacultyDetailPage'
import { RoomDetailPage } from './pages/RoomDetailPage'
import { IssuesPage } from './pages/IssuesPage'
import { WorkersPage } from './pages/WorkersPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/faculties" replace />} />
            <Route path="/faculties" element={<FacultiesPage />} />
            <Route path="/faculties/:facultyId" element={<FacultyDetailPage />} />
            <Route path="/rooms/:roomId" element={<RoomDetailPage />} />
            <Route path="/issues" element={<IssuesPage />} />
            <Route path="/workers" element={<WorkersPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/faculties" replace />} />
      </Routes>
    </AuthProvider>
  )
}
