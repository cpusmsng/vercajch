import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import {
  Wrench,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  ArrowLeftRight,
  ClipboardList,
} from 'lucide-react'

export default function DashboardPage() {
  const { data: equipmentStats } = useQuery({
    queryKey: ['reports', 'equipment-summary'],
    queryFn: async () => {
      const response = await api.get('/reports/equipment-summary')
      return response.data
    },
  })

  const { data: calibrationStats } = useQuery({
    queryKey: ['calibrations', 'dashboard'],
    queryFn: async () => {
      const response = await api.get('/calibrations/dashboard')
      return response.data
    },
  })

  const { data: checkoutStats } = useQuery({
    queryKey: ['reports', 'checkout-stats'],
    queryFn: async () => {
      const response = await api.get('/reports/checkout-stats')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Prehľad stavu náradia a vybavenia</p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Celkom náradia</p>
              <p className="text-2xl font-bold text-gray-900">
                {equipmentStats?.total || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Wrench className="h-6 w-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Vydané</p>
              <p className="text-2xl font-bold text-gray-900">
                {equipmentStats?.by_status?.checked_out || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <ArrowLeftRight className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">V údržbe</p>
              <p className="text-2xl font-bold text-gray-900">
                {equipmentStats?.by_status?.maintenance || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <ClipboardList className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Dostupné</p>
              <p className="text-2xl font-bold text-gray-900">
                {equipmentStats?.by_status?.available || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Calibration Stats */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Kalibrácie</h2>
          <Link
            to="/calibrations"
            className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
          >
            Zobraziť všetky
            <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {calibrationStats?.summary?.total_requiring_calibration || 0}
            </div>
            <div className="text-xs text-gray-500">Celkom</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {calibrationStats?.summary?.valid || 0}
            </div>
            <div className="text-xs text-gray-500">Platné</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {calibrationStats?.summary?.expiring_30_days || 0}
            </div>
            <div className="text-xs text-gray-500">Končí do 30 dní</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {calibrationStats?.summary?.expiring_7_days || 0}
            </div>
            <div className="text-xs text-gray-500">Končí do 7 dní</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {calibrationStats?.summary?.expired || 0}
            </div>
            <div className="text-xs text-gray-500">Expirované</div>
          </div>
        </div>

        {calibrationStats?.expired && calibrationStats.expired.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-700 font-medium mb-2">
              <AlertTriangle className="h-5 w-5" />
              Vyžaduje okamžitú pozornosť
            </div>
            <div className="space-y-2">
              {calibrationStats.expired.slice(0, 3).map((item: any) => (
                <div
                  key={item.equipment.id}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-700">{item.equipment.name}</span>
                  <span className="text-red-600">
                    {Math.abs(item.days_until_expiry)} dní po expirácii
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Stats Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Checkout Stats */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Výpožičky (posledných 30 dní)
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {checkoutStats?.total_checkouts || 0}
              </div>
              <div className="text-xs text-gray-500">Celkom</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {checkoutStats?.active_checkouts || 0}
              </div>
              <div className="text-xs text-gray-500">Aktívne</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {checkoutStats?.overdue_checkouts || 0}
              </div>
              <div className="text-xs text-gray-500">Oneskorené</div>
            </div>
          </div>
        </div>

        {/* Equipment by Condition */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Stav náradia
          </h2>
          <div className="space-y-3">
            {['new', 'good', 'fair', 'poor', 'broken'].map((condition) => {
              const count = equipmentStats?.by_condition?.[condition] || 0
              const total = equipmentStats?.total || 1
              const percentage = Math.round((count / total) * 100)
              const colors: Record<string, string> = {
                new: 'bg-green-500',
                good: 'bg-blue-500',
                fair: 'bg-yellow-500',
                poor: 'bg-orange-500',
                broken: 'bg-red-500',
              }
              const labels: Record<string, string> = {
                new: 'Nové',
                good: 'Dobré',
                fair: 'Opotrebované',
                poor: 'Zlé',
                broken: 'Poškodené',
              }
              return (
                <div key={condition}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{labels[condition]}</span>
                    <span className="text-gray-900 font-medium">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${colors[condition]} h-2 rounded-full`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
