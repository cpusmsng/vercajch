import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import {
  Settings,
  Bell,
  Printer,
  Shield,
  Database,
  Save,
  Check,
  X,
  Plus,
  Trash2,
  Edit,
} from 'lucide-react'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<
    'general' | 'notifications' | 'printing' | 'security'
  >('general')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Nastavenia</h1>
        <p className="text-gray-600">Konfigurácia systému</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64">
          <nav className="bg-white rounded-xl shadow-sm border p-2 space-y-1">
            {[
              { id: 'general', label: 'Všeobecné', icon: Settings },
              { id: 'notifications', label: 'Notifikácie', icon: Bell },
              { id: 'printing', label: 'Tlač', icon: Printer },
              { id: 'security', label: 'Bezpečnosť', icon: Shield },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === item.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'general' && <GeneralSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
          {activeTab === 'printing' && <PrintingSettings />}
          {activeTab === 'security' && <SecuritySettings />}
        </div>
      </div>
    </div>
  )
}

function GeneralSettings() {
  const queryClient = useQueryClient()
  const [settings, setSettings] = useState({
    company_name: 'SPP - distribúcia',
    default_checkout_days: '14',
    max_checkout_extensions: '3',
    require_photo_on_checkout: true,
    require_photo_on_return: true,
    auto_assign_internal_code: true,
    internal_code_prefix: 'SPP',
  })
  const [saved, setSaved] = useState(false)

  const { data: systemSettings, isLoading } = useQuery({
    queryKey: ['settings', 'general'],
    queryFn: async () => {
      const response = await api.get('/settings')
      return response.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      await api.patch('/settings', data)
    },
    onSuccess: () => {
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })

  const handleSave = () => {
    saveMutation.mutate({
      ...settings,
      default_checkout_days: parseInt(settings.default_checkout_days),
      max_checkout_extensions: parseInt(settings.max_checkout_extensions),
    })
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Všeobecné nastavenia
      </h2>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Názov spoločnosti
          </label>
          <input
            type="text"
            value={settings.company_name}
            onChange={(e) =>
              setSettings({ ...settings, company_name: e.target.value })
            }
            className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Predvolená doba výpožičky (dní)
            </label>
            <input
              type="number"
              value={settings.default_checkout_days}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  default_checkout_days: e.target.value,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max. počet predĺžení
            </label>
            <input
              type="number"
              value={settings.max_checkout_extensions}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  max_checkout_extensions: e.target.value,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.require_photo_on_checkout}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  require_photo_on_checkout: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Vyžadovať fotku pri výpožičke
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.require_photo_on_return}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  require_photo_on_return: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Vyžadovať fotku pri vrátení
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.auto_assign_internal_code}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  auto_assign_internal_code: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Automaticky prideľovať interný kód
            </span>
          </label>
        </div>

        {settings.auto_assign_internal_code && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prefix interného kódu
            </label>
            <input
              type="text"
              value={settings.internal_code_prefix}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  internal_code_prefix: e.target.value,
                })
              }
              className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        )}

        <div className="pt-4 border-t flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {saveMutation.isPending ? 'Ukladám...' : 'Uložiť zmeny'}
          </button>
          {saved && (
            <span className="text-green-600 flex items-center gap-1">
              <Check className="h-4 w-4" />
              Uložené
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function NotificationSettings() {
  const [settings, setSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    calibration_reminder_days: [30, 14, 7, 1],
    checkout_overdue_reminder: true,
    transfer_notifications: true,
  })

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Nastavenia notifikácií
      </h2>

      <div className="space-y-6">
        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.email_notifications}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  email_notifications: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Povoliť emailové notifikácie
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.push_notifications}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  push_notifications: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Povoliť push notifikácie
            </span>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pripomenutie kalibrácie (dní pred)
          </label>
          <div className="flex flex-wrap gap-2">
            {settings.calibration_reminder_days.map((days, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
              >
                {days} dní
                <button
                  onClick={() =>
                    setSettings({
                      ...settings,
                      calibration_reminder_days:
                        settings.calibration_reminder_days.filter(
                          (_, i) => i !== index
                        ),
                    })
                  }
                  className="ml-2 text-primary-500 hover:text-primary-700"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.checkout_overdue_reminder}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  checkout_overdue_reminder: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Pripomienky oneskorených výpožičiek
            </span>
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.transfer_notifications}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  transfer_notifications: e.target.checked,
                })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">
              Notifikácie o transferoch
            </span>
          </label>
        </div>

        <div className="pt-4 border-t">
          <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            <Save className="h-4 w-4 mr-2" />
            Uložiť zmeny
          </button>
        </div>
      </div>
    </div>
  )
}

function PrintingSettings() {
  const queryClient = useQueryClient()
  const [showPrinterModal, setShowPrinterModal] = useState(false)

  const { data: printers } = useQuery({
    queryKey: ['printers'],
    queryFn: async () => {
      const response = await api.get('/printing/printers')
      return response.data
    },
  })

  const { data: templates } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      const response = await api.get('/printing/templates')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Tlačiarne</h2>
          <button
            onClick={() => setShowPrinterModal(true)}
            className="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
          >
            <Plus className="h-4 w-4 mr-1" />
            Pridať
          </button>
        </div>

        {printers && printers.length > 0 ? (
          <div className="space-y-3">
            {printers.map((printer: any) => (
              <div
                key={printer.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Printer className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium text-gray-900">
                      {printer.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {printer.ip_address}:{printer.port}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      printer.is_online
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {printer.is_online ? 'Online' : 'Offline'}
                  </span>
                  <button className="text-gray-400 hover:text-primary-600">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="text-gray-400 hover:text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            Žiadne tlačiarne nie sú nakonfigurované
          </p>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">
          Šablóny štítkov
        </h2>

        {templates && templates.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template: any) => (
              <div
                key={template.id}
                className="border rounded-lg p-4 hover:border-primary-300 cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-900">
                    {template.name}
                  </div>
                  {template.is_default && (
                    <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded">
                      Predvolená
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-500">
                  {template.width}x{template.height}mm
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            Žiadne šablóny nie sú nakonfigurované
          </p>
        )}
      </div>
    </div>
  )
}

function SecuritySettings() {
  const [settings, setSettings] = useState({
    password_min_length: 8,
    password_require_uppercase: true,
    password_require_number: true,
    password_require_special: false,
    session_timeout_minutes: 480,
    max_login_attempts: 5,
    lockout_duration_minutes: 30,
  })

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Bezpečnostné nastavenia
      </h2>

      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-4">
            Požiadavky na heslo
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Minimálna dĺžka hesla
              </label>
              <input
                type="number"
                value={settings.password_min_length}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    password_min_length: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <div className="mt-4 space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.password_require_uppercase}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    password_require_uppercase: e.target.checked,
                  })
                }
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">
                Vyžadovať veľké písmeno
              </span>
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.password_require_number}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    password_require_number: e.target.checked,
                  })
                }
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">Vyžadovať číslo</span>
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.password_require_special}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    password_require_special: e.target.checked,
                  })
                }
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">
                Vyžadovať špeciálny znak
              </span>
            </label>
          </div>
        </div>

        <div className="pt-4 border-t">
          <h3 className="text-sm font-medium text-gray-900 mb-4">
            Nastavenia relácie
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Timeout relácie (min)
              </label>
              <input
                type="number"
                value={settings.session_timeout_minutes}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    session_timeout_minutes: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max. pokusov o prihlásenie
              </label>
              <input
                type="number"
                value={settings.max_login_attempts}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    max_login_attempts: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Doba uzamknutia (min)
              </label>
              <input
                type="number"
                value={settings.lockout_duration_minutes}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    lockout_duration_minutes: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        <div className="pt-4 border-t">
          <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            <Save className="h-4 w-4 mr-2" />
            Uložiť zmeny
          </button>
        </div>
      </div>
    </div>
  )
}
