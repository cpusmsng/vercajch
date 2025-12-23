import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import type { User, Role, Department, PaginatedResponse } from '../types'
import {
  Search,
  Plus,
  Filter,
  ChevronLeft,
  ChevronRight,
  Edit,
  UserCheck,
  UserX,
  X,
} from 'lucide-react'

export default function UsersPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const { data: users, isLoading } = useQuery({
    queryKey: ['users', page, search, roleFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        size: '20',
      })
      if (search) params.append('search', search)
      if (roleFilter) params.append('role_id', roleFilter)

      const response = await api.get<PaginatedResponse<User>>(
        `/users?${params}`
      )
      return response.data
    },
  })

  const { data: roles } = useQuery({
    queryKey: ['roles'],
    queryFn: async () => {
      const response = await api.get<Role[]>('/users/roles')
      return response.data
    },
  })

  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn: async () => {
      const response = await api.get<Department[]>('/users/departments')
      return response.data
    },
  })

  const toggleActiveMutation = useMutation({
    mutationFn: async ({ id, isActive }: { id: string; isActive: boolean }) => {
      await api.patch(`/users/${id}`, { is_active: isActive })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const roleLabels: Record<string, string> = {
    worker: 'Pracovník',
    leader: 'Vedúci',
    manager: 'Manažér',
    admin: 'Administrátor',
    superadmin: 'Super Admin',
  }

  const roleColors: Record<string, string> = {
    worker: 'bg-gray-100 text-gray-800',
    leader: 'bg-blue-100 text-blue-800',
    manager: 'bg-purple-100 text-purple-800',
    admin: 'bg-orange-100 text-orange-800',
    superadmin: 'bg-red-100 text-red-800',
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Používatelia</h1>
          <p className="text-gray-600">Správa používateľov a ich oprávnení</p>
        </div>
        <button
          onClick={() => {
            setEditingUser(null)
            setShowModal(true)
          }}
          className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Pridať používateľa
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Hľadať podľa mena, emailu..."
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
                Rola
              </label>
              <select
                value={roleFilter}
                onChange={(e) => {
                  setRoleFilter(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Všetky role</option>
                {roles?.map((role) => (
                  <option key={role.id} value={role.id}>
                    {roleLabels[role.name] || role.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Používateľ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rola
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Oddelenie
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
              ) : users?.items.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-12 text-center text-gray-500"
                  >
                    Žiadni používatelia neboli nájdení
                  </td>
                </tr>
              ) : (
                users?.items.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-primary-600 font-medium">
                            {user.full_name?.charAt(0) || user.email.charAt(0)}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.full_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {user.employee_id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          roleColors[user.role?.name || ''] ||
                          'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {roleLabels[user.role?.name || ''] ||
                          user.role?.name ||
                          '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.department?.name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? 'Aktívny' : 'Neaktívny'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => {
                            setEditingUser(user)
                            setShowModal(true)
                          }}
                          className="text-gray-400 hover:text-primary-600"
                          title="Upraviť"
                        >
                          <Edit className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() =>
                            toggleActiveMutation.mutate({
                              id: user.id,
                              isActive: !user.is_active,
                            })
                          }
                          className={`${
                            user.is_active
                              ? 'text-gray-400 hover:text-red-600'
                              : 'text-gray-400 hover:text-green-600'
                          }`}
                          title={user.is_active ? 'Deaktivovať' : 'Aktivovať'}
                        >
                          {user.is_active ? (
                            <UserX className="h-5 w-5" />
                          ) : (
                            <UserCheck className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {users && users.pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Zobrazuje sa{' '}
                  <span className="font-medium">{(page - 1) * 20 + 1}</span> až{' '}
                  <span className="font-medium">
                    {Math.min(page * 20, users.total)}
                  </span>{' '}
                  z <span className="font-medium">{users.total}</span>{' '}
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
                  disabled={page === users.pages}
                  className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Modal */}
      {showModal && (
        <UserModal
          user={editingUser}
          roles={roles || []}
          departments={departments || []}
          onClose={() => {
            setShowModal(false)
            setEditingUser(null)
          }}
          onSuccess={() => {
            setShowModal(false)
            setEditingUser(null)
            queryClient.invalidateQueries({ queryKey: ['users'] })
          }}
        />
      )}
    </div>
  )
}

function UserModal({
  user,
  roles,
  departments,
  onClose,
  onSuccess,
}: {
  user: User | null
  roles: Role[]
  departments: Department[]
  onClose: () => void
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    email: user?.email || '',
    full_name: user?.full_name || '',
    employee_id: user?.employee_id || '',
    phone: user?.phone || '',
    role_id: user?.role_id || '',
    department_id: user?.department_id || '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = { ...formData }
      if (!payload.password) {
        delete (payload as any).password
      }

      if (user) {
        await api.patch(`/users/${user.id}`, payload)
      } else {
        await api.post('/users', payload)
      }
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
        <div
          className="fixed inset-0 bg-black/50"
          onClick={onClose}
        />
        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {user ? 'Upraviť používateľa' : 'Nový používateľ'}
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
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meno a priezvisko
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) =>
                    setFormData({ ...formData, full_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Osobné číslo
                </label>
                <input
                  type="text"
                  value={formData.employee_id}
                  onChange={(e) =>
                    setFormData({ ...formData, employee_id: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefón
                </label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rola
                </label>
                <select
                  value={formData.role_id}
                  onChange={(e) =>
                    setFormData({ ...formData, role_id: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Vyberte rolu</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Oddelenie
                </label>
                <select
                  value={formData.department_id}
                  onChange={(e) =>
                    setFormData({ ...formData, department_id: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Vyberte oddelenie</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Heslo {user && '(nechajte prázdne pre zachovanie)'}
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  {...(!user && { required: true })}
                />
              </div>
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
                disabled={loading}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Ukladám...' : user ? 'Uložiť' : 'Vytvoriť'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
