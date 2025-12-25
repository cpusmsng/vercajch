import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import type { Equipment, Calibration, Checkout } from '../types'
import { QRCodeSVG } from 'qrcode.react'
import {
  ArrowLeft,
  Edit,
  MapPin,
  User,
  Gauge,
  History,
  Image,
  Tag,
} from 'lucide-react'

export default function EquipmentDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: equipment, isLoading } = useQuery({
    queryKey: ['equipment', id],
    queryFn: async () => {
      const response = await api.get<Equipment>(`/equipment/${id}`)
      return response.data
    },
    enabled: !!id,
  })

  const { data: calibrations } = useQuery({
    queryKey: ['equipment', id, 'calibrations'],
    queryFn: async () => {
      const response = await api.get<Calibration[]>(
        `/calibrations/equipment/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })

  const { data: history } = useQuery({
    queryKey: ['equipment', id, 'history'],
    queryFn: async () => {
      const response = await api.get(`/equipment/${id}/history`)
      return response.data
    },
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (!equipment) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Náradie nebolo nájdené</p>
      </div>
    )
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

  const conditionLabels: Record<string, string> = {
    new: 'Nové',
    good: 'Dobré',
    fair: 'Opotrebované',
    poor: 'Zlé',
    broken: 'Poškodené',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/equipment"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{equipment.name}</h1>
            <p className="text-gray-500">{equipment.internal_code}</p>
          </div>
        </div>
        <Link
          to={`/equipment/${id}/edit`}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <Edit className="h-4 w-4 mr-2" />
          Upraviť
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Photo and Basic Info */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex flex-col md:flex-row gap-6">
              <div className="flex-shrink-0">
                {equipment.photo_url ? (
                  <img
                    src={equipment.photo_url}
                    alt={equipment.name}
                    className="w-48 h-48 object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-48 h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Image className="h-12 w-12 text-gray-400" />
                  </div>
                )}
              </div>
              <div className="flex-1 space-y-4">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      statusColors[equipment.status]
                    }`}
                  >
                    {statusLabels[equipment.status]}
                  </span>
                  <span className="text-sm text-gray-500">
                    Stav: {conditionLabels[equipment.condition]}
                  </span>
                </div>

                {equipment.description && (
                  <p className="text-gray-600">{equipment.description}</p>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-500">Kategória</div>
                    <div className="font-medium">
                      {equipment.category?.name || '-'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Sériové číslo</div>
                    <div className="font-medium">
                      {equipment.serial_number || '-'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Výrobca</div>
                    <div className="font-medium">
                      {equipment.manufacturer || '-'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Model</div>
                    <div className="font-medium">
                      {equipment.model_name || '-'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Location and Holder */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Aktuálne umiestnenie
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <div className="text-sm text-gray-500">Lokácia</div>
                  <div className="font-medium">
                    {equipment.current_location?.name || 'Neurčená'}
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <div className="text-sm text-gray-500">Držiteľ</div>
                  <div className="font-medium">
                    {equipment.current_holder?.full_name || 'Nikto'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Calibration Info */}
          {equipment.requires_calibration && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Kalibrácia
                </h3>
                <Gauge className="h-5 w-5 text-gray-400" />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Interval</div>
                  <div className="font-medium">
                    {equipment.calibration_interval_days} dní
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Posledná</div>
                  <div className="font-medium">
                    {equipment.last_calibration_date || '-'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Nasledujúca</div>
                  <div className="font-medium">
                    {equipment.next_calibration_date || '-'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Stav</div>
                  <div
                    className={`font-medium ${
                      equipment.calibration_status === 'valid'
                        ? 'text-green-600'
                        : equipment.calibration_status === 'expiring'
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}
                  >
                    {equipment.calibration_status === 'valid'
                      ? 'Platná'
                      : equipment.calibration_status === 'expiring'
                      ? 'Končí'
                      : 'Expirovaná'}
                  </div>
                </div>
              </div>

              {calibrations && calibrations.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    História kalibrácií
                  </h4>
                  <div className="space-y-2">
                    {calibrations.slice(0, 3).map((cal) => (
                      <div
                        key={cal.id}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="text-gray-600">
                          {cal.calibration_date} - {cal.calibration_lab}
                        </span>
                        <span
                          className={
                            cal.result === 'passed'
                              ? 'text-green-600'
                              : 'text-red-600'
                          }
                        >
                          {cal.result === 'passed' ? 'Vyhovuje' : 'Nevyhovuje'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* History */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">História</h3>
              <History className="h-5 w-5 text-gray-400" />
            </div>
            {history?.checkouts && history.checkouts.length > 0 ? (
              <div className="space-y-3">
                {history.checkouts.slice(0, 5).map((checkout: Checkout) => (
                  <div
                    key={checkout.id}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {checkout.user?.full_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(checkout.checkout_at).toLocaleDateString(
                          'sk-SK'
                        )}
                        {checkout.actual_return_at && (
                          <>
                            {' '}
                            -{' '}
                            {new Date(
                              checkout.actual_return_at
                            ).toLocaleDateString('sk-SK')}
                          </>
                        )}
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        checkout.status === 'active'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {checkout.status === 'active' ? 'Aktívne' : 'Vrátené'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Žiadna história</p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* QR Code */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">QR Kód</h3>
            <div className="flex justify-center">
              <QRCodeSVG
                value={`https://equip.spp-d.sk/scan/${equipment.id}`}
                size={180}
                level="M"
              />
            </div>
            {equipment.tags && equipment.tags.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="text-sm text-gray-500 mb-2">Tagy</div>
                <div className="space-y-2">
                  {equipment.tags.map((tag) => (
                    <div
                      key={tag.id}
                      className="flex items-center gap-2 text-sm"
                    >
                      <Tag className="h-4 w-4 text-gray-400" />
                      <span className="truncate">{tag.tag_value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Purchase Info */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Kúpa a hodnota
            </h3>
            <div className="space-y-3">
              {equipment.purchase_date && (
                <div>
                  <div className="text-sm text-gray-500">Dátum kúpy</div>
                  <div className="font-medium">{equipment.purchase_date}</div>
                </div>
              )}
              {equipment.purchase_price && (
                <div>
                  <div className="text-sm text-gray-500">Nákupná cena</div>
                  <div className="font-medium">
                    {equipment.purchase_price.toLocaleString('sk-SK')} €
                  </div>
                </div>
              )}
              {equipment.current_value && (
                <div>
                  <div className="text-sm text-gray-500">Aktuálna hodnota</div>
                  <div className="font-medium">
                    {equipment.current_value.toLocaleString('sk-SK')} €
                  </div>
                </div>
              )}
              {equipment.warranty_expiry && (
                <div>
                  <div className="text-sm text-gray-500">Záruka do</div>
                  <div className="font-medium">{equipment.warranty_expiry}</div>
                </div>
              )}
            </div>
          </div>

          {/* Photos */}
          {equipment.photos && equipment.photos.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Fotografie
              </h3>
              <div className="grid grid-cols-3 gap-2">
                {equipment.photos.map((photo) => (
                  <img
                    key={photo.id}
                    src={photo.thumbnail_url || photo.file_url}
                    alt={photo.description || 'Photo'}
                    className="w-full aspect-square object-cover rounded-lg"
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
