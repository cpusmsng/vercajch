import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { MaintenanceRecord, PaginatedResponse } from '../types'
import {
  Search,
  Plus,
  Filter,
  ChevronLeft,
  ChevronRight,
  Eye,
  ClipboardList,
  Check,
  Clock,
  AlertTriangle,
  X,
} from 'lucide-react'

export default function MaintenancePage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const [showModal, setShowModal] = useState(false)

  const { data: maintenance, isLoading } = useQuery({
    queryKey: ['maintenance', page, search, statusFilter, typeFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        size: '20',
      })
      if (search) params.append('search', search)
      if (statusFilter) params.append('status', statusFilter)
      if (typeFilter) params.append('type', typeFilter)

      const response = await api.get<PaginatedResponse<MaintenanceRecord>>(
        `/maintenance?${params}`
      )
      return response.data
    },
  })

  const { data: stats } = useQuery({
    queryKey: ['maintenance', 'stats'],
    queryFn: async () => {
      const response = await api.get('/maintenance/stats')
      return response.data
    },
  })

  const statusOptions = [
    { value: '', label: 'Všetky stavy' },
    { value: 'scheduled', label: 'Naplánované' },
    { value: 'in_progress', label: 'Prebieha' },
    { value: 'completed', label: 'Dokončené' },
    { value: 'cancelled', label: 'Zrušené' },
  ]

  const typeOptions = [
    { value: '', label: 'Všetky typy' },
    { value: 'preventive', label: 'Preventívna' },
    { value: 'corrective', label: 'Oprava' },
    { value: 'inspection', label: 'Kontrola' },
  ]

  const statusLabels: Record<string, string> = {
    scheduled: 'Naplánované',
    in_progress: 'Prebieha',
    completed: 'Dokončené',
    cancelled: 'Zrušené',
  }

  const statusColors: Record<string, string> = {
    scheduled: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }

  const typeLabels: Record<string, string> = {
    preventive: 'Preventívna',
    corrective: 'Oprava',
    inspection: 'Kontrola',
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Údržba</h1>
          <p className="text-gray-600">Správa údržby a opráv náradia</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nová údržba
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.scheduled || 0}
              </div>
              <div className="text-sm text-gray-500">Naplánované</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <ClipboardList className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.in_progress || 0}
              </div>
              <div className="text-sm text-gray-500">Prebieha</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Check className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.completed_this_month || 0}
              </div>
              <div className="text-sm text-gray-500">Dokončené (mesiac)</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {stats?.overdue || 0}
              </div>
              <div className="text-sm text-gray-500">Oneskorené</div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Hľadať podľa názvu náradia..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center px-4 py-2 border rounded-lg transition-colors ${
              showFilters
                ? 'bg-primary-50 border-primary-200 text-primary-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Filter className="h-5 w-5 mr-2" />
            Filtre
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stav
              </label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {statusOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Typ
              </label>
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {typeOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Maintenance Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Náradie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Typ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Popis
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dátum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stav
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Akcie
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
                    </div>
                  </td>
                </tr>
              ) : maintenance?.items.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-12 text-center text-gray-500"
                  >
                    Žiadne záznamy údržby
                  </td>
                </tr>
              ) : (
                maintenance?.items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {item.equipment?.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {item.equipment?.internal_code}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.maintenance_type ? typeLabels[item.maintenance_type] || item.maintenance_type : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {item.description}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.scheduled_date &&
                        new Date(item.scheduled_date).toLocaleDateString('sk-SK')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          statusColors[item.status]
                        }`}
                      >
                        {statusLabels[item.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/equipment/${item.equipment_id}`}
                          className="text-gray-400 hover:text-primary-600"
                          title="Detail náradia"
                        >
                          <Eye className="h-5 w-5" />
                        </Link>
                        {item.status === 'scheduled' && (
                          <button
                            onClick={async () => {
                              await api.patch(`/maintenance/${item.id}`, {
                                status: 'in_progress',
                              })
                              queryClient.invalidateQueries({
                                queryKey: ['maintenance'],
                              })
                            }}
                            className="text-gray-400 hover:text-blue-600"
                            title="Začať"
                          >
                            <ClipboardList className="h-5 w-5" />
                          </button>
                        )}
                        {item.status === 'in_progress' && (
                          <button
                            onClick={async () => {
                              await api.patch(`/maintenance/${item.id}`, {
                                status: 'completed',
                                completed_date: new Date().toISOString(),
                              })
                              queryClient.invalidateQueries({
                                queryKey: ['maintenance'],
                              })
                            }}
                            className="text-gray-400 hover:text-green-600"
                            title="Dokončiť"
                          >
                            <Check className="h-5 w-5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {maintenance && maintenance.pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Zobrazuje sa{' '}
                  <span className="font-medium">{(page - 1) * 20 + 1}</span> až{' '}
                  <span className="font-medium">
                    {Math.min(page * 20, maintenance.total)}
                  </span>{' '}
                  z <span className="font-medium">{maintenance.total}</span>{' '}
                  výsledkov
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === maintenance.pages}
                  className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* New Maintenance Modal */}
      {showModal && (
        <MaintenanceModal
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setShowModal(false)
            queryClient.invalidateQueries({ queryKey: ['maintenance'] })
          }}
        />
      )}
    </div>
  )
}

function MaintenanceModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    equipment_id: '',
    maintenance_type: 'preventive',
    description: '',
    scheduled_date: '',
    notes: '',
  })
  const [equipmentSearch, setEquipmentSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const { data: equipmentList } = useQuery({
    queryKey: ['equipment-search', equipmentSearch],
    queryFn: async () => {
      if (!equipmentSearch) return []
      const response = await api.get(`/equipment?search=${equipmentSearch}&size=10`)
      return response.data.items
    },
    enabled: equipmentSearch.length > 2,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await api.post('/maintenance', formData)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Nastala chyba')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Nový záznam údržby
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Náradie
              </label>
              <input
                type="text"
                placeholder="Vyhľadať náradie..."
                value={equipmentSearch}
                onChange={(e) => setEquipmentSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              {equipmentList && equipmentList.length > 0 && (
                <div className="mt-2 border rounded-lg divide-y max-h-40 overflow-auto">
                  {equipmentList.map((eq: any) => (
                    <button
                      key={eq.id}
                      type="button"
                      onClick={() => {
                        setFormData({ ...formData, equipment_id: eq.id })
                        setEquipmentSearch(eq.name)
                      }}
                      className="w-full px-3 py-2 text-left hover:bg-gray-50 text-sm"
                    >
                      {eq.name} - {eq.internal_code}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Typ údržby
              </label>
              <select
                value={formData.maintenance_type}
                onChange={(e) =>
                  setFormData({ ...formData, maintenance_type: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="preventive">Preventívna</option>
                <option value="corrective">Oprava</option>
                <option value="inspection">Kontrola</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Popis
              </label>
              <textarea
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Naplánovaný dátum
              </label>
              <input
                type="date"
                value={formData.scheduled_date}
                onChange={(e) =>
                  setFormData({ ...formData, scheduled_date: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Poznámky
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Zrušiť
              </button>
              <button
                type="submit"
                disabled={loading || !formData.equipment_id}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Ukladám...' : 'Vytvoriť'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
