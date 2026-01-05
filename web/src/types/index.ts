export interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  employee_id?: string
  employee_number?: string
  role_id?: string
  role?: Role
  department_id?: string
  department?: Department
  manager_id?: string
  is_active: boolean
  can_access_web?: boolean
  can_access_mobile?: boolean
  avatar_url?: string
  last_login_at?: string
  created_at?: string
  permissions?: string[]
  version?: number
}

export interface Role {
  id: string
  code: string
  name: string
  description?: string
}

export interface Department {
  id: string
  name: string
  code?: string
}

export interface Category {
  id: string
  name: string
  code?: string
  description?: string
  parent_id?: string
  parent_category_id?: string
  default_maintenance_interval_days?: number
  default_calibration_interval_days?: number
  requires_certification?: boolean
  requires_calibration?: boolean
  transfer_requires_approval?: boolean
  icon?: string
  color?: string
  equipment_count?: number
  children?: Category[]
}

export interface Location {
  id: string
  name: string
  type?: 'warehouse' | 'project' | 'vehicle' | 'other'
  code?: string
  address?: string
  gps_lat?: number
  gps_lng?: number
  parent_id?: string
  parent_location_id?: string
  responsible_user_id?: string
  is_active?: boolean
  equipment_count?: number
  children?: Location[]
}

export interface Equipment {
  id: string
  name: string
  description?: string
  category_id?: string
  category?: Category
  model_id?: string
  serial_number?: string
  internal_code?: string
  manufacturer?: string
  model_name?: string
  purchase_date?: string
  purchase_price?: number
  current_value?: number
  warranty_expiry?: string
  condition: 'new' | 'good' | 'fair' | 'poor' | 'broken'
  status: 'available' | 'checked_out' | 'maintenance' | 'retired'
  photo_url?: string
  current_location_id?: string
  current_location?: Location
  current_holder_id?: string
  current_holder?: User
  home_location_id?: string
  is_main_item: boolean
  parent_equipment_id?: string
  is_transferable: boolean
  requires_calibration: boolean
  calibration_interval_days?: number
  last_calibration_date?: string
  next_calibration_date?: string
  calibration_status?: 'valid' | 'expiring' | 'expired' | 'not_required'
  notes?: string
  version: number
  created_at: string
  updated_at?: string
  tags?: EquipmentTag[]
  photos?: EquipmentPhoto[]
}

export interface EquipmentTag {
  id: string
  tag_type: 'qr_code' | 'rfid_nfc' | 'rfid_uhf' | 'barcode'
  tag_value: string
  rfid_uid?: string
  status: 'active' | 'damaged' | 'lost' | 'replaced'
  scan_count: number
  last_scanned_at?: string
}

export interface EquipmentPhoto {
  id: string
  photo_type: 'main' | 'detail' | 'label' | 'damage' | 'calibration'
  file_url: string
  thumbnail_url?: string
  description?: string
  sort_order: number
}

export interface Calibration {
  id: string
  equipment_id: string
  calibration_type: 'initial' | 'periodic' | 'after_repair' | 'verification'
  calibration_date: string
  valid_until: string
  next_calibration_date?: string
  performed_by_type?: 'internal' | 'external' | 'manufacturer'
  performed_by_name?: string
  calibration_lab?: string
  certificate_number?: string
  certificate_url?: string
  result: 'passed' | 'passed_with_adjustment' | 'failed'
  cost?: number
  notes?: string
  days_until_expiry?: number
  status?: 'valid' | 'expiring' | 'expired'
  created_at: string
}

export interface CalibrationDashboard {
  summary: {
    total_requiring_calibration: number
    valid: number
    expiring_30_days: number
    expiring_7_days: number
    expired: number
  }
  upcoming: CalibrationDueItem[]
  expired: CalibrationDueItem[]
  monthly_forecast?: Record<string, number>
}

export interface CalibrationDueItem {
  equipment: Equipment
  days_until_expiry: number
  last_calibration?: Calibration
}

export interface Checkout {
  id: string
  equipment_id: string
  equipment?: Equipment
  user_id: string
  user?: User
  location_id?: string
  location?: Location
  checkout_at: string
  expected_return_at?: string
  actual_return_at?: string
  checkout_condition?: string
  checkout_notes?: string
  return_condition?: string
  return_notes?: string
  status: 'active' | 'returned' | 'overdue'
  created_at: string
}

export interface TransferRequest {
  id: string
  request_type: 'direct' | 'broadcast' | 'offer'
  equipment_id?: string
  equipment?: Equipment
  category_id?: string
  category?: Category
  requester_id: string
  requester?: User
  holder_id?: string
  holder?: User
  location_id?: string
  location?: Location
  location_note?: string
  needed_from?: string
  needed_until?: string
  message?: string
  status: 'pending' | 'accepted' | 'rejected' | 'cancelled' | 'expired' | 'completed' | 'requires_approval'
  requires_leader_approval: boolean
  approved_by?: string
  approved_at?: string
  rejection_reason?: string
  responded_at?: string
  expires_at?: string
  created_at: string
  offers?: TransferOffer[]
}

export interface TransferOffer {
  id: string
  request_id: string
  offerer_id: string
  offerer?: User
  equipment_id: string
  equipment?: Equipment
  message?: string
  status: 'pending' | 'accepted' | 'rejected'
  created_at: string
}

export interface Transfer {
  id: string
  equipment_id: string
  equipment?: Equipment
  request_id?: string
  from_user_id: string
  from_user?: User
  to_user_id: string
  to_user?: User
  location_id?: string
  location?: Location
  from_confirmed_at?: string
  to_confirmed_at?: string
  condition_at_transfer?: string
  photo_url?: string
  notes?: string
  transfer_type: 'peer' | 'checkout' | 'checkin' | 'handover'
  created_at: string
}

export interface MaintenanceRecord {
  id: string
  equipment_id: string
  equipment?: Equipment
  type?: 'scheduled' | 'repair' | 'inspection' | 'calibration'
  maintenance_type?: 'preventive' | 'corrective' | 'inspection'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'scheduled'
  priority?: 'low' | 'normal' | 'high' | 'urgent'
  title?: string
  description?: string
  scheduled_date?: string
  started_at?: string
  completed_at?: string
  performed_by?: string
  performer?: User
  assigned_to?: string
  assignee?: User
  cost?: number
  vendor?: string
  next_maintenance_date?: string
  notes?: string
  created_at?: string
}

export interface Notification {
  id: string
  type: string
  title: string
  message?: string
  related_entity_type?: string
  related_entity_id?: string
  is_read: boolean
  read_at?: string
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface AuthToken {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}
