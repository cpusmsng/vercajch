import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import type { Equipment } from '../types'
import { ArrowLeft, Search, Send, Clock, User } from 'lucide-react'

interface TransferFormData {
  equipment_id: string
  holder_id: string | null
  message: string
  needed_until: string | null
}

export default function CreateTransferPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null)
  const [message, setMessage] = useState('')
  const [duration, setDuration] = useState<number | null>(null)
  const [customDate, setCustomDate] = useState('')

  const { data: equipment, isLoading: loadingEquipment } = useQuery({
    queryKey: ['equipment', 'available', searchQuery],
    queryFn: async () => {
      const response = await api.get<{ items: Equipment[] }>('/equipment', {
        params: { search: searchQuery || undefined, status: 'available', limit: 20 }
      })
      return response.data.items
    },
  })

  const createRequestMutation = useMutation({
    mutationFn: async (data: TransferFormData) => {
      return api.post('/transfers/requests', {
        request_type: 'direct',
        equipment_id: data.equipment_id,
        holder_id: data.holder_id,
        message: data.message || null,
        needed_until: data.needed_until,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers'] })
      navigate('/transfers')
    },
  })

  const handleSubmit = () => {
    if (!selectedEquipment) return

    let neededUntil: string | null = null
    if (duration && duration > 0) {
      const date = new Date()
      date.setDate(date.getDate() + duration)
      neededUntil = date.toISOString().split('T')[0]
    } else if (customDate) {
      neededUntil = customDate
    }

    createRequestMutation.mutate({
      equipment_id: selectedEquipment.id,
      holder_id: selectedEquipment.current_holder?.id || null,
      message,
      needed_until: neededUntil,
    })
  }

  const durationOptions = [
    { days: 1, label: '1 deň' },
    { days: 3, label: '3 dni' },
    { days: 7, label: '1 týždeň' },
    { days: 14, label: '2 týždne' },
    { days: 30, label: '1 mesiac' },
    { days: 0, label: 'Vlastný dátum' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nová požiadavka na transfer</h1>
          <p className="text-gray-600">Vyberte náradie a vyplňte podrobnosti požiadavky</p>
        </div>
      </div>

      {!selectedEquipment ? (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">1. Vyberte náradie</h2>

          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Hľadať náradie..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {loadingEquipment ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : equipment && equipment.length > 0 ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {equipment.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setSelectedEquipment(item)}
                  className="w-full p-4 border rounded-lg hover:border-primary-500 hover:bg-primary-50 text-left transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">{item.internal_code}</div>
                    </div>
                    {item.current_holder && (
                      <div className="text-sm text-gray-500 flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {item.current_holder.full_name}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              {searchQuery ? 'Žiadne náradie nenájdené' : 'Zadajte hľadaný výraz'}
            </p>
          )}
        </div>
      ) : (
        <>
          <div className="bg-primary-50 border border-primary-200 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-gray-900">{selectedEquipment.name}</div>
                <div className="text-sm text-gray-600">{selectedEquipment.internal_code}</div>
                {selectedEquipment.current_holder && (
                  <div className="text-sm text-gray-600 mt-1">
                    Držiteľ: {selectedEquipment.current_holder.full_name}
                  </div>
                )}
              </div>
              <button
                onClick={() => setSelectedEquipment(null)}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Zmeniť
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Ako dlho potrebujete náradie?</h2>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
              {durationOptions.map((option) => (
                <button
                  key={option.days}
                  onClick={() => {
                    setDuration(option.days)
                    if (option.days !== 0) setCustomDate('')
                  }}
                  className={`p-3 border rounded-lg text-sm font-medium transition-colors ${
                    duration === option.days
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'hover:border-gray-300'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>

            {duration === 0 && (
              <input
                type="date"
                value={customDate}
                onChange={(e) => setCustomDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">3. Správa (voliteľná)</h2>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Napíšte dôvod požiadavky..."
              rows={3}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {createRequestMutation.error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              Chyba pri vytváraní požiadavky. Skúste to znova.
            </div>
          )}

          <div className="flex justify-end gap-3">
            <button
              onClick={() => navigate('/transfers')}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              Zrušiť
            </button>
            <button
              onClick={handleSubmit}
              disabled={createRequestMutation.isPending}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
            >
              {createRequestMutation.isPending ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Odoslať požiadavku
            </button>
          </div>
        </>
      )}
    </div>
  )
}
