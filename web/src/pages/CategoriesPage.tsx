import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import type { Category } from '../types'
import {
  Search,
  Plus,
  Edit,
  Trash2,
  Folder,
  X,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'

export default function CategoriesPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await api.get<Category[]>('/categories')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/categories/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  // Build tree structure
  const buildTree = (items: Category[] | undefined): Category[] => {
    if (!items) return []
    const map = new Map<string, Category & { children?: Category[] }>()
    const roots: (Category & { children?: Category[] })[] = []

    items.forEach((item) => {
      map.set(item.id, { ...item, children: [] })
    })

    items.forEach((item) => {
      const node = map.get(item.id)!
      if (item.parent_id && map.has(item.parent_id)) {
        map.get(item.parent_id)!.children!.push(node)
      } else {
        roots.push(node)
      }
    })

    return roots
  }

  const tree = buildTree(categories)

  const filteredTree = search
    ? categories?.filter((cat) =>
        cat.name.toLowerCase().includes(search.toLowerCase())
      )
    : null

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const renderCategoryRow = (
    category: Category & { children?: Category[] },
    level: number = 0
  ): React.ReactNode => {
    const hasChildren = category.children && category.children.length > 0
    const isExpanded = expandedIds.has(category.id)

    return (
      <div key={category.id}>
        <div
          className={`flex items-center justify-between p-4 hover:bg-gray-50 border-b ${
            level > 0 ? 'bg-gray-50/50' : ''
          }`}
          style={{ paddingLeft: `${1.5 + level * 1.5}rem` }}
        >
          <div className="flex items-center gap-3">
            {hasChildren ? (
              <button
                onClick={() => toggleExpand(category.id)}
                className="text-gray-400 hover:text-gray-600"
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
            ) : (
              <div className="w-4" />
            )}
            <div
              className="h-8 w-8 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: category.color || '#6366f1' }}
            >
              <Folder className="h-4 w-4 text-white" />
            </div>
            <div>
              <div className="font-medium text-gray-900">{category.name}</div>
              {category.description && (
                <div className="text-sm text-gray-500">
                  {category.description}
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              {category.equipment_count || 0} náradia
            </div>
            {category.requires_calibration && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                Kalibrácia
              </span>
            )}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setEditingCategory(category)
                  setShowModal(true)
                }}
                className="text-gray-400 hover:text-primary-600"
              >
                <Edit className="h-5 w-5" />
              </button>
              <button
                onClick={() => {
                  if (confirm('Naozaj chcete odstrániť túto kategóriu?')) {
                    deleteMutation.mutate(category.id)
                  }
                }}
                className="text-gray-400 hover:text-red-600"
              >
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
        {hasChildren &&
          isExpanded &&
          category.children!.map((child) => renderCategoryRow(child, level + 1))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Kategórie</h1>
          <p className="text-gray-600">Správa kategórií náradia</p>
        </div>
        <button
          onClick={() => {
            setEditingCategory(null)
            setShowModal(true)
          }}
          className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Pridať kategóriu
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Hľadať kategóriu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Categories Tree */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
          </div>
        ) : search && filteredTree ? (
          filteredTree.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              Žiadne kategórie neboli nájdené
            </div>
          ) : (
            filteredTree.map((category) => (
              <div
                key={category.id}
                className="flex items-center justify-between p-4 hover:bg-gray-50 border-b"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="h-8 w-8 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: category.color || '#6366f1' }}
                  >
                    <Folder className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {category.name}
                    </div>
                    {category.description && (
                      <div className="text-sm text-gray-500">
                        {category.description}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setEditingCategory(category)
                      setShowModal(true)
                    }}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <Edit className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Naozaj chcete odstrániť túto kategóriu?')) {
                        deleteMutation.mutate(category.id)
                      }
                    }}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))
          )
        ) : tree.length === 0 ? (
          <div className="p-12 text-center text-gray-500">Žiadne kategórie</div>
        ) : (
          tree.map((category) => renderCategoryRow(category))
        )}
      </div>

      {/* Category Modal */}
      {showModal && (
        <CategoryModal
          category={editingCategory}
          categories={categories || []}
          onClose={() => {
            setShowModal(false)
            setEditingCategory(null)
          }}
          onSuccess={() => {
            setShowModal(false)
            setEditingCategory(null)
            queryClient.invalidateQueries({ queryKey: ['categories'] })
          }}
        />
      )}
    </div>
  )
}

function CategoryModal({
  category,
  categories,
  onClose,
  onSuccess,
}: {
  category: Category | null
  categories: Category[]
  onClose: () => void
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    name: category?.name || '',
    description: category?.description || '',
    parent_id: category?.parent_id || '',
    color: category?.color || '#6366f1',
    requires_calibration: category?.requires_calibration || false,
    default_calibration_interval_days:
      category?.default_calibration_interval_days?.toString() || '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        ...formData,
        parent_id: formData.parent_id || null,
        default_calibration_interval_days: formData.default_calibration_interval_days
          ? parseInt(formData.default_calibration_interval_days)
          : null,
      }

      if (category) {
        await api.patch(`/categories/${category.id}`, payload)
      } else {
        await api.post('/categories', payload)
      }
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Nastala chyba')
    } finally {
      setLoading(false)
    }
  }

  const availableParents = categories.filter((cat) => cat.id !== category?.id)

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {category ? 'Upraviť kategóriu' : 'Nová kategória'}
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
                Názov
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
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
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nadradená kategória
              </label>
              <select
                value={formData.parent_id}
                onChange={(e) =>
                  setFormData({ ...formData, parent_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Žiadna (hlavná kategória)</option>
                {availableParents.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Farba
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) =>
                    setFormData({ ...formData, color: e.target.value })
                  }
                  className="h-10 w-16 border border-gray-300 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={formData.color}
                  onChange={(e) =>
                    setFormData({ ...formData, color: e.target.value })
                  }
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="requires_calibration"
                checked={formData.requires_calibration}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    requires_calibration: e.target.checked,
                  })
                }
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label
                htmlFor="requires_calibration"
                className="text-sm font-medium text-gray-700"
              >
                Vyžaduje kalibráciu
              </label>
            </div>

            {formData.requires_calibration && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Predvolený interval kalibrácie (dní)
                </label>
                <input
                  type="number"
                  value={formData.default_calibration_interval_days}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      default_calibration_interval_days: e.target.value,
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            )}

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
                {loading ? 'Ukladám...' : category ? 'Uložiť' : 'Vytvoriť'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
