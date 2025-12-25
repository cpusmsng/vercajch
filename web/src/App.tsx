import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import EquipmentPage from './pages/EquipmentPage'
import EquipmentDetailPage from './pages/EquipmentDetailPage'
import CalibrationsPage from './pages/CalibrationsPage'
import TransfersPage from './pages/TransfersPage'
import UsersPage from './pages/UsersPage'
import LocationsPage from './pages/LocationsPage'
import CategoriesPage from './pages/CategoriesPage'
import MaintenancePage from './pages/MaintenancePage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/equipment" element={<EquipmentPage />} />
                <Route path="/equipment/:id" element={<EquipmentDetailPage />} />
                <Route path="/calibrations" element={<CalibrationsPage />} />
                <Route path="/transfers" element={<TransfersPage />} />
                <Route path="/users" element={<UsersPage />} />
                <Route path="/locations" element={<LocationsPage />} />
                <Route path="/categories" element={<CategoriesPage />} />
                <Route path="/maintenance" element={<MaintenancePage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
