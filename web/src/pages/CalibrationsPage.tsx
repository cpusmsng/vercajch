import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { CalibrationDashboard, CalibrationDueItem } from '../types'
import {
  Gauge,
  AlertTriangle,
  Download,
  Settings,
  Eye,
  Plus,
  ChevronRight,
} from 'lucide-react'

export default function CalibrationsPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'list'>('dashboard')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['calibrations', 'dashboard'],
    queryFn: async () => {
      const response = await api.get<CalibrationDashboard>(
        '/calibrations/dashboard'
      )
      return response.data
    },
  })

  const { data: dueItems } = useQuery({
    queryKey: ['calibrations', 'due', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      params.append('days_ahead', '90')
      const response = await api.get(`/calibrations/due?${params}`)
      return response.data
    },
    enabled: activeTab === 'list',
  })

  const stats = [
    {
      label: 'Celkom sledovaných',
      value: dashboard?.summary.total_requiring_calibration || 0,
      color: 'text-gray-900',
      bg: 'bg-gray-50',
    },
    {
      label: 'Platné',
      value: dashboard?.summary.valid || 0,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      label: 'Končí do 30 dní',
      value: dashboard?.summary.expiring_30_days || 0,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
    },
    {
      label: 'Končí do 7 dní',
      value: dashboard?.summary.expiring_7_days || 0,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
    },
    {
      label: 'Expirované',
      value: dashboard?.summary.expired || 0,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Kalibrácie</h1>
          <p className="text-gray-600">
            Sledovanie a správa kalibrácií zariadení
          </p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            <Download className="h-4 w-4 mr-2" />
            Export plánu
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            <Settings className="h-4 w-4 mr-2" />
            Nastavenia
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className={`${stat.bg} rounded-xl p-4 text-center`}
          >
            <div className={`text-2xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'dashboard'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'list'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Zoznam
          </button>
        </nav>
      </div>

      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Critical - Expired */}
          {dashboard?.expired && dashboard.expired.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="flex items-center gap-2 text-red-700 font-semibold mb-4">
                <AlertTriangle className="h-5 w-5" />
                Vyžaduje okamžitú pozornosť ({dashboard.expired.length})
              </div>
              <div className="bg-white rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Zariadenie
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Kategória
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Po expirácii
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Akcie
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dashboard.expired.map((item) => (
                      <tr key={item.equipment.id}>
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">
                            {item.equipment.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {item.equipment.internal_code}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {item.equipment.category?.name}
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-red-600 font-medium">
                            {Math.abs(item.days_until_expiry)} dní
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              to={`/equipment/${item.equipment.id}`}
                              className="text-gray-400 hover:text-primary-600"
                            >
                              <Eye className="h-5 w-5" />
                            </Link>
                            <button className="text-primary-600 hover:text-primary-700">
                              <Plus className="h-5 w-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Upcoming */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Nadchádzajúce kalibrácie (30 dní)
              </h3>
              <button
                onClick={() => setActiveTab('list')}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
              >
                Zobraziť všetky
                <ChevronRight className="h-4 w-4 ml-1" />
              </button>
            </div>
            {dashboard?.upcoming && dashboard.upcoming.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Zariadenie
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Kategória
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Platnosť do
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Zostáva
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Akcie
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dashboard.upcoming.map((item) => (
                      <tr key={item.equipment.id}>
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">
                            {item.equipment.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {item.equipment.internal_code}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {item.equipment.category?.name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {item.equipment.next_calibration_date}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`font-medium ${
                              item.days_until_expiry <= 7
                                ? 'text-orange-600'
                                : 'text-yellow-600'
                            }`}
                          >
                            {item.days_until_expiry} dní
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              to={`/equipment/${item.equipment.id}`}
                              className="text-gray-400 hover:text-primary-600"
                            >
                              <Eye className="h-5 w-5" />
                            </Link>
                            <button className="text-primary-600 hover:text-primary-700">
                              <Plus className="h-5 w-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Žiadne nadchádzajúce kalibrácie
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'list' && (
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <div className="flex flex-wrap gap-2">
              {[
                { value: 'all', label: 'Všetky' },
                { value: 'expiring', label: 'Končiace' },
                { value: 'expired', label: 'Expirované' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setStatusFilter(opt.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    statusFilter === opt.value
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Zariadenie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Kategória
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Platnosť do
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Zostáva
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Stav
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Akcie
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {dueItems?.map((item: any) => (
                  <tr key={item.equipment.id}>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {item.equipment.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {item.equipment.internal_code}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {item.equipment.category?.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {item.equipment.next_calibration_date}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`font-medium ${
                          item.days_until_expiry < 0
                            ? 'text-red-600'
                            : item.days_until_expiry <= 7
                            ? 'text-orange-600'
                            : item.days_until_expiry <= 30
                            ? 'text-yellow-600'
                            : 'text-green-600'
                        }`}
                      >
                        {item.days_until_expiry < 0
                          ? `${Math.abs(item.days_until_expiry)} dní po`
                          : `${item.days_until_expiry} dní`}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          item.status === 'expired'
                            ? 'bg-red-100 text-red-800'
                            : item.status === 'expiring'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {item.status === 'expired'
                          ? 'Expirovaná'
                          : item.status === 'expiring'
                          ? 'Končí'
                          : 'Platná'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/equipment/${item.equipment.id}`}
                          className="text-gray-400 hover:text-primary-600"
                        >
                          <Eye className="h-5 w-5" />
                        </Link>
                        <button className="text-primary-600 hover:text-primary-700">
                          <Plus className="h-5 w-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
