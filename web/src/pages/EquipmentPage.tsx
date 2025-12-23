import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { Equipment, Category, Location, PaginatedResponse } from '../types'
import {
  Search,
  Plus,
  Filter,
  ChevronLeft,
  ChevronRight,
  Eye,
  Edit,
  QrCode,
} from 'lucide-react'

export default function EquipmentPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState<string>('')
  const [status, setStatus] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  const { data: equipment, isLoading } = useQuery({
    queryKey: ['equipment', page, search, categoryId, status],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        size: '20',
      })
      if (search) params.append('search', search)
      if (categoryId) params.append('category_id', categoryId)
      if (status) params.append('status', status)

      const response = await api.get<PaginatedResponse<Equipment>>(
        `/equipment?${params}`
      )
      return response.data
    },
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get<Category[]>('/categories')
      return response.data
    },
  })

  const statusOptions = [
    { value: '', label: 'Všetky stavy' },
    { value: 'available', label: 'Dostupné' },
    { value: 'checked_out', label: 'Vydané' },
    { value: 'maintenance', label: 'V údržbe' },
    { value: 'retired', label: 'Vyradené' },
  ]

  const conditionLabels: Record<string, string> = {
    new: 'Nové',
    good: 'Dobré',
    fair: 'Opotrebované',
    poor: 'Zlé',
    broken: 'Poškodené',
  }

  const statusLabels: Record<string, string> = {
    available: 'Dostupné',
    checked_out: 'Vydané',
    maintenance: 'V údržbe',
    retired: 'Vyradené',
  }

  const statusColors: Record<string, string> = {
    available: 'bg-green-100 text-green-800',
    checked_out: 'bg-blue-100 text-blue-800',
    maintenance: 'bg-yellow-100 text-yellow-800',
    retired: 'bg-gray-100 text-gray-800',
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Náradie</h1>
          <p className="text-gray-600">
            Spravujte náradie a vybavenie
          </p>
        </div>
        <Link
          to="/equipment/new"
          className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Pridať náradie
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Hľadať podľa názvu, kódu, sériového čísla..."
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
                Kategória
              </label>
              <select
                value={categoryId}
                onChange={(e) => {
                  setCategoryId(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Všetky kategórie</option>
                {categories?.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stav
              </label>
              <select
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value)
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
          </div>
        )}
      </div>

      {/* Equipment Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Náradie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kategória
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stav
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lokácia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Držiteľ
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
              ) : equipment?.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Žiadne náradie nebolo nájdené
                  </td>
                </tr>
              ) : (
                equipment?.items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          {item.photo_url ? (
                            <img
                              src={item.photo_url}
                              alt={item.name}
                              className="h-10 w-10 rounded-lg object-cover"
                            />
                          ) : (
                            <div className="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center">
                              <QrCode className="h-5 w-5 text-gray-400" />
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {item.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {item.internal_code}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.category?.name || '-'}
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.current_location?.name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.current_holder?.full_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/equipment/${item.id}`}
                          className="text-gray-400 hover:text-primary-600"
                          title="Detail"
                        >
                          <Eye className="h-5 w-5" />
                        </Link>
                        <Link
                          to={`/equipment/${item.id}/edit`}
                          className="text-gray-400 hover:text-primary-600"
                          title="Upraviť"
                        >
                          <Edit className="h-5 w-5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {equipment && equipment.pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Zobrazuje sa{' '}
                  <span className="font-medium">
                    {(page - 1) * 20 + 1}
                  </span>{' '}
                  až{' '}
                  <span className="font-medium">
                    {Math.min(page * 20, equipment.total)}
                  </span>{' '}
                  z <span className="font-medium">{equipment.total}</span>{' '}
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
                  disabled={page === equipment.pages}
                  className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
