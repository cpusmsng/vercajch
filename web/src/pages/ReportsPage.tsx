import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import {
  BarChart3,
  PieChart,
  Download,
  Calendar,
  TrendingUp,
  Package,
  Users,
  MapPin,
} from 'lucide-react'

export default function ReportsPage() {
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0],
    to: new Date().toISOString().split('T')[0],
  })

  const { data: equipmentSummary } = useQuery({
    queryKey: ['reports', 'equipment-summary'],
    queryFn: async () => {
      const response = await api.get('/reports/equipment-summary')
      return response.data
    },
  })

  const { data: checkoutStats } = useQuery({
    queryKey: ['reports', 'checkout-stats', dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        from_date: dateRange.from,
        to_date: dateRange.to,
      })
      const response = await api.get(`/reports/checkout-stats?${params}`)
      return response.data
    },
  })

  const { data: userActivity } = useQuery({
    queryKey: ['reports', 'user-activity', dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        from_date: dateRange.from,
        to_date: dateRange.to,
      })
      const response = await api.get(`/reports/user-activity?${params}`)
      return response.data
    },
  })

  const { data: locationStats } = useQuery({
    queryKey: ['reports', 'location-stats'],
    queryFn: async () => {
      const response = await api.get('/reports/location-stats')
      return response.data
    },
  })

  const handleExport = async (type: string) => {
    try {
      const params = new URLSearchParams({
        from_date: dateRange.from,
        to_date: dateRange.to,
        format: 'xlsx',
      })
      const response = await api.get(`/reports/export/${type}?${params}`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${type}-report.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reporty</h1>
          <p className="text-gray-600">Prehľady a štatistiky systému</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) =>
                setDateRange({ ...dateRange, from: e.target.value })
              }
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <span className="text-gray-500">-</span>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) =>
                setDateRange({ ...dateRange, to: e.target.value })
              }
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Celkom náradia</p>
              <p className="text-2xl font-bold text-gray-900">
                {equipmentSummary?.total || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Package className="h-6 w-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">
              +{equipmentSummary?.added_this_month || 0}
            </span>
            <span className="text-gray-500 ml-1">tento mesiac</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Aktívne výpožičky</p>
              <p className="text-2xl font-bold text-gray-900">
                {checkoutStats?.active_checkouts || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            {checkoutStats?.total_checkouts || 0} celkom za obdobie
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Aktívni používatelia</p>
              <p className="text-2xl font-bold text-gray-900">
                {userActivity?.active_users || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            {userActivity?.total_actions || 0} akcií za obdobie
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Lokácie</p>
              <p className="text-2xl font-bold text-gray-900">
                {locationStats?.total_locations || 0}
              </p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <MapPin className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            {locationStats?.locations_with_equipment || 0} s náradím
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equipment by Status */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Náradie podľa stavu
            </h3>
            <button
              onClick={() => handleExport('equipment')}
              className="text-gray-400 hover:text-primary-600"
            >
              <Download className="h-5 w-5" />
            </button>
          </div>
          <div className="space-y-4">
            {[
              {
                status: 'available',
                label: 'Dostupné',
                color: 'bg-green-500',
                count: equipmentSummary?.by_status?.available || 0,
              },
              {
                status: 'checked_out',
                label: 'Vydané',
                color: 'bg-blue-500',
                count: equipmentSummary?.by_status?.checked_out || 0,
              },
              {
                status: 'maintenance',
                label: 'V údržbe',
                color: 'bg-yellow-500',
                count: equipmentSummary?.by_status?.maintenance || 0,
              },
              {
                status: 'retired',
                label: 'Vyradené',
                color: 'bg-gray-500',
                count: equipmentSummary?.by_status?.retired || 0,
              },
            ].map((item) => {
              const total = equipmentSummary?.total || 1
              const percentage = Math.round((item.count / total) * 100)
              return (
                <div key={item.status}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="text-gray-900 font-medium">
                      {item.count} ({percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full transition-all`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Equipment by Condition */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Náradie podľa stavu opotrebenia
            </h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {[
              {
                condition: 'new',
                label: 'Nové',
                color: 'bg-green-500',
                count: equipmentSummary?.by_condition?.new || 0,
              },
              {
                condition: 'good',
                label: 'Dobré',
                color: 'bg-blue-500',
                count: equipmentSummary?.by_condition?.good || 0,
              },
              {
                condition: 'fair',
                label: 'Opotrebované',
                color: 'bg-yellow-500',
                count: equipmentSummary?.by_condition?.fair || 0,
              },
              {
                condition: 'poor',
                label: 'Zlé',
                color: 'bg-orange-500',
                count: equipmentSummary?.by_condition?.poor || 0,
              },
              {
                condition: 'broken',
                label: 'Poškodené',
                color: 'bg-red-500',
                count: equipmentSummary?.by_condition?.broken || 0,
              },
            ].map((item) => {
              const total = equipmentSummary?.total || 1
              const percentage = Math.round((item.count / total) * 100)
              return (
                <div key={item.condition}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="text-gray-900 font-medium">
                      {item.count} ({percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full transition-all`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Top Categories */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Top kategórie podľa počtu náradia
          </h3>
          <button
            onClick={() => handleExport('categories')}
            className="text-gray-400 hover:text-primary-600"
          >
            <Download className="h-5 w-5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Kategória
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Počet
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Hodnota
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Priemerný vek
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {equipmentSummary?.by_category?.slice(0, 10).map((cat: any) => (
                <tr key={cat.id}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {cat.name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {cat.count}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {cat.total_value?.toLocaleString('sk-SK')} €
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {cat.average_age_days
                      ? `${Math.round(cat.average_age_days / 365)} rokov`
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Users */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Najaktívnejší používatelia
          </h3>
          <button
            onClick={() => handleExport('users')}
            className="text-gray-400 hover:text-primary-600"
          >
            <Download className="h-5 w-5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Používateľ
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Výpožičky
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Transfery
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Onboardingy
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {userActivity?.top_users?.slice(0, 10).map((user: any) => (
                <tr key={user.id}>
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-primary-600 font-medium text-sm">
                          {user.full_name?.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.full_name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {user.department}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {user.checkout_count || 0}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {user.transfer_count || 0}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 text-right">
                    {user.onboarding_count || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Export dát
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => handleExport('equipment')}
            className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              Zoznam náradia
            </span>
          </button>
          <button
            onClick={() => handleExport('checkouts')}
            className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              Výpožičky
            </span>
          </button>
          <button
            onClick={() => handleExport('calibrations')}
            className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              Kalibrácie
            </span>
          </button>
          <button
            onClick={() => handleExport('maintenance')}
            className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">
              Údržba
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}
