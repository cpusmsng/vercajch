import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import type { Location } from '../types'
import {
  Search,
  Plus,
  Edit,
  Trash2,
  MapPin,
  X,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'

export default function LocationsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingLocation, setEditingLocation] = useState<Location | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: async () => {
      const response = await api.get<Location[]>('/locations')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/locations/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
    },
  })

  // Build tree structure
  const buildTree = (items: Location[] | undefined): Location[] => {
    if (!items) return []
    const map = new Map<string, Location & { children?: Location[] }>()
    const roots: (Location & { children?: Location[] })[] = []

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

  const tree = buildTree(locations)

  const filteredTree = search
    ? locations?.filter(
        (loc) =>
          loc.name.toLowerCase().includes(search.toLowerCase()) ||
          loc.code?.toLowerCase().includes(search.toLowerCase())
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

  const renderLocationRow = (
    location: Location & { children?: Location[] },
    level: number = 0
  ): React.ReactNode => {
    const hasChildren = location.children && location.children.length > 0
    const isExpanded = expandedIds.has(location.id)

    return (
      <div key={location.id}>
        <div
          className={`flex items-center justify-between p-4 hover:bg-gray-50 border-b ${
            level > 0 ? 'bg-gray-50/50' : ''
          }`}
          style={{ paddingLeft: `${1.5 + level * 1.5}rem` }}
        >
          <div className="flex items-center gap-3">
            {hasChildren ? (
              <button
                onClick={() => toggleExpand(location.id)}
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
            <MapPin className="h-5 w-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">{location.name}</div>
              {location.code && (
                <div className="text-sm text-gray-500">{location.code}</div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              {location.equipment_count || 0} náradia
            </span>
            <button
              onClick={() => {
                setEditingLocation(location)
                setShowModal(true)
              }}
              className="text-gray-400 hover:text-primary-600"
            >
              <Edit className="h-5 w-5" />
            </button>
            <button
              onClick={() => {
                if (
                  confirm('Naozaj chcete odstrániť túto lokáciu?')
                ) {
                  deleteMutation.mutate(location.id)
                }
              }}
              className="text-gray-400 hover:text-red-600"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          </div>
        </div>
        {hasChildren &&
          isExpanded &&
          location.children!.map((child) => renderLocationRow(child, level + 1))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lokácie</h1>
          <p className="text-gray-600">Správa skladov a lokácií</p>
        </div>
        <button
          onClick={() => {
            setEditingLocation(null)
            setShowModal(true)
          }}
          className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Pridať lokáciu
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Hľadať lokáciu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Locations Tree */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
          </div>
        ) : search && filteredTree ? (
          filteredTree.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              Žiadne lokácie neboli nájdené
            </div>
          ) : (
            filteredTree.map((location) => (
              <div
                key={location.id}
                className="flex items-center justify-between p-4 hover:bg-gray-50 border-b"
              >
                <div className="flex items-center gap-3">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium text-gray-900">
                      {location.name}
                    </div>
                    {location.code && (
                      <div className="text-sm text-gray-500">{location.code}</div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setEditingLocation(location)
                      setShowModal(true)
                    }}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <Edit className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => {
                      if (
                        confirm('Naozaj chcete odstrániť túto lokáciu?')
                      ) {
                        deleteMutation.mutate(location.id)
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
          <div className="p-12 text-center text-gray-500">
            Žiadne lokácie
          </div>
        ) : (
          tree.map((location) => renderLocationRow(location))
        )}
      </div>

      {/* Location Modal */}
      {showModal && (
        <LocationModal
          location={editingLocation}
          locations={locations || []}
          onClose={() => {
            setShowModal(false)
            setEditingLocation(null)
          }}
          onSuccess={() => {
            setShowModal(false)
            setEditingLocation(null)
            queryClient.invalidateQueries({ queryKey: ['locations'] })
          }}
        />
      )}
    </div>
  )
}

function LocationModal({
  location,
  locations,
  onClose,
  onSuccess,
}: {
  location: Location | null
  locations: Location[]
  onClose: () => void
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    name: location?.name || '',
    code: location?.code || '',
    parent_id: location?.parent_id || '',
    address: location?.address || '',
    gps_lat: location?.gps_lat?.toString() || '',
    gps_lng: location?.gps_lng?.toString() || '',
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
        gps_lat: formData.gps_lat ? parseFloat(formData.gps_lat) : null,
        gps_lng: formData.gps_lng ? parseFloat(formData.gps_lng) : null,
      }

      if (location) {
        await api.patch(`/locations/${location.id}`, payload)
      } else {
        await api.post('/locations', payload)
      }
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Nastala chyba')
    } finally {
      setLoading(false)
    }
  }

  const availableParents = locations.filter((loc) => loc.id !== location?.id)

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {location ? 'Upraviť lokáciu' : 'Nová lokácia'}
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
                Kód
              </label>
              <input
                type="text"
                value={formData.code}
                onChange={(e) =>
                  setFormData({ ...formData, code: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nadradená lokácia
              </label>
              <select
                value={formData.parent_id}
                onChange={(e) =>
                  setFormData({ ...formData, parent_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Žiadna (hlavná lokácia)</option>
                {availableParents.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Adresa
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) =>
                  setFormData({ ...formData, address: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  GPS Lat
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.gps_lat}
                  onChange={(e) =>
                    setFormData({ ...formData, gps_lat: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  GPS Lng
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.gps_lng}
                  onChange={(e) =>
                    setFormData({ ...formData, gps_lng: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
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
                {loading ? 'Ukladám...' : location ? 'Uložiť' : 'Vytvoriť'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
