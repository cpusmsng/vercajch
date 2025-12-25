import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { TransferRequest, Transfer } from '../types'
import { ArrowLeftRight, Clock, Check, X, Eye } from 'lucide-react'

export default function TransfersPage() {
  const [activeTab, setActiveTab] = useState<
    'pending' | 'active' | 'history' | 'approval'
  >('pending')

  const { data: sentRequests } = useQuery({
    queryKey: ['transfers', 'sent'],
    queryFn: async () => {
      const response = await api.get<TransferRequest[]>(
        '/transfers/requests/sent'
      )
      return response.data
    },
  })

  const { data: receivedRequests } = useQuery({
    queryKey: ['transfers', 'received'],
    queryFn: async () => {
      const response = await api.get<TransferRequest[]>(
        '/transfers/requests/received'
      )
      return response.data
    },
  })

  const { data: pendingApprovals } = useQuery({
    queryKey: ['transfers', 'pending-approval'],
    queryFn: async () => {
      const response = await api.get<TransferRequest[]>(
        '/transfers/pending-approval'
      )
      return response.data
    },
  })

  const { data: history } = useQuery({
    queryKey: ['transfers', 'history'],
    queryFn: async () => {
      const response = await api.get<Transfer[]>('/transfers/history')
      return response.data
    },
    enabled: activeTab === 'history',
  })

  const statusLabels: Record<string, string> = {
    pending: 'Čaká',
    accepted: 'Prijaté',
    rejected: 'Odmietnuté',
    cancelled: 'Zrušené',
    expired: 'Expirované',
    completed: 'Dokončené',
    requires_approval: 'Čaká na schválenie',
  }

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    accepted: 'bg-blue-100 text-blue-800',
    rejected: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
    expired: 'bg-gray-100 text-gray-800',
    completed: 'bg-green-100 text-green-800',
    requires_approval: 'bg-orange-100 text-orange-800',
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Transfery</h1>
        <p className="text-gray-600">
          Správa požiadaviek o transfer náradia medzi používateľmi
        </p>
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
                {(receivedRequests?.length || 0) +
                  (sentRequests?.filter((r) => r.status === 'pending').length ||
                    0)}
              </div>
              <div className="text-sm text-gray-500">Čakajúce</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <ArrowLeftRight className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {sentRequests?.filter((r) => r.status === 'accepted').length ||
                  0}
              </div>
              <div className="text-sm text-gray-500">Aktívne</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {pendingApprovals?.length || 0}
              </div>
              <div className="text-sm text-gray-500">Na schválenie</div>
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
                {history?.length || 0}
              </div>
              <div className="text-sm text-gray-500">Dokončené</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {[
            {
              id: 'pending',
              label: 'Čakajúce',
              count:
                (receivedRequests?.length || 0) +
                (sentRequests?.filter((r) => r.status === 'pending').length ||
                  0),
            },
            {
              id: 'active',
              label: 'Aktívne',
              count:
                sentRequests?.filter((r) => r.status === 'accepted').length ||
                0,
            },
            { id: 'history', label: 'História', count: null },
            {
              id: 'approval',
              label: 'Schválenia',
              count: pendingApprovals?.length || 0,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.count !== null && tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'pending' && (
        <div className="space-y-6">
          {/* Received Requests */}
          {receivedRequests && receivedRequests.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border">
              <div className="p-4 border-b">
                <h3 className="font-semibold text-gray-900">
                  Požiadavky na moje náradie
                </h3>
              </div>
              <div className="divide-y divide-gray-200">
                {receivedRequests.map((request) => (
                  <div
                    key={request.id}
                    className="p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-medium">
                          {request.requester?.full_name?.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">
                          {request.requester?.full_name} žiada o{' '}
                          {request.equipment?.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {request.message}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200">
                        Odmietnuť
                      </button>
                      <button className="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200">
                        Prijať
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sent Requests */}
          {sentRequests && sentRequests.filter((r) => r.status === 'pending').length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border">
              <div className="p-4 border-b">
                <h3 className="font-semibold text-gray-900">
                  Moje odoslané požiadavky
                </h3>
              </div>
              <div className="divide-y divide-gray-200">
                {sentRequests
                  .filter((r) => r.status === 'pending')
                  .map((request) => (
                    <div
                      key={request.id}
                      className="p-4 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-medium text-gray-900">
                          {request.equipment?.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          Od: {request.holder?.full_name}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            statusColors[request.status]
                          }`}
                        >
                          {statusLabels[request.status]}
                        </span>
                        <button className="text-gray-400 hover:text-red-600">
                          <X className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {!receivedRequests?.length &&
            !sentRequests?.filter((r) => r.status === 'pending').length && (
              <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
                <ArrowLeftRight className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Žiadne čakajúce požiadavky</p>
              </div>
            )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Náradie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Od
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Komu
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Dátum
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Akcie
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {history?.map((transfer) => (
                <tr key={transfer.id}>
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">
                      {transfer.equipment?.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {transfer.equipment?.internal_code}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {transfer.from_user?.full_name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {transfer.to_user?.full_name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(transfer.created_at).toLocaleDateString('sk-SK')}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/equipment/${transfer.equipment_id}`}
                      className="text-gray-400 hover:text-primary-600"
                    >
                      <Eye className="h-5 w-5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'approval' && (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          {pendingApprovals && pendingApprovals.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Náradie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Od
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Komu
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Dôvod
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Akcie
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pendingApprovals.map((request) => (
                  <tr key={request.id}>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {request.equipment?.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {request.equipment?.internal_code}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {request.holder?.full_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {request.requester?.full_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {request.message}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button className="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200">
                          Zamietnuť
                        </button>
                        <button className="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200">
                          Schváliť
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center">
              <Check className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Žiadne požiadavky na schválenie</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
