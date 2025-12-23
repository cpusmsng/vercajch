# Equipment Tracking System - Kompletný Prompt pre Claude Code

## Prehľad Projektu

Vytvor full-stack systém na tracking náradia a vybavenia pre firmu s ~1300 zamestnancami, z toho cca 200 mobilných pracovníkov v teréne (plynárenská distribučná spoločnosť).

**Systém pozostáva z:**
1. **Backend API** (FastAPI + PostgreSQL)
2. **Android Aplikácia** (Kotlin + Jetpack Compose) - pre terénnych pracovníkov
3. **Web Aplikácia** (React + TypeScript) - pre manažérov a administrátorov

---

## Tech Stack

### Backend
```
FastAPI (Python 3.11+)
├── PostgreSQL 15+ (databáza)
├── SQLAlchemy 2.0 (ORM)
├── Alembic (migrácie)
├── Pydantic v2 (validácia)
├── JWT + Refresh Tokens (autentifikácia)
├── Python-QRCode (generovanie QR)
├── Celery + Redis (background tasks, notifikácie)
└── MinIO/S3 (storage pre fotky)
```

### Android App
```
Kotlin + Jetpack Compose
├── Material 3 Design
├── MVVM + Clean Architecture
├── Hilt (Dependency Injection)
├── Room (offline SQLite databáza)
├── Retrofit + OkHttp (networking)
├── CameraX + ML Kit (QR/barcode scanning)
├── Android NFC API (NFC tagy)
├── WorkManager (background sync)
└── Bluetooth API (RFID readers, tlačiarne)
```

### Web App
```
React 18 + TypeScript
├── Vite (build tool)
├── Tailwind CSS + shadcn/ui
├── TanStack Query (data fetching)
├── React Router v6
├── Zustand (state management)
├── QRCode.react (QR generovanie)
└── Recharts (grafy)
```

### Infraštruktúra
```
Docker + Docker Compose
├── Nginx (reverse proxy)
├── PostgreSQL container
├── Redis container
├── MinIO container
└── Traefik (voliteľne, pre SSL)
```

---

## Databázový Model

```sql
-- ============================================
-- CORE TABLES
-- ============================================

-- Role a oprávnenia
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,  -- 'worker', 'leader', 'manager', 'admin', 'superadmin'
  name VARCHAR(100) NOT NULL,
  description TEXT,
  is_system_role BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  module VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE role_permissions (
  role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id)
);

-- Oddelenia
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  code VARCHAR(20),
  parent_department_id UUID REFERENCES departments(id),
  manager_id UUID,  -- FK added later
  default_location_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Používatelia
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  employee_number VARCHAR(50),
  
  role_id UUID REFERENCES roles(id),
  department_id UUID REFERENCES departments(id),
  manager_id UUID REFERENCES users(id),
  
  is_active BOOLEAN DEFAULT true,
  can_access_web BOOLEAN DEFAULT false,
  can_access_mobile BOOLEAN DEFAULT true,
  
  allowed_locations UUID[],
  allowed_categories UUID[],
  
  avatar_url VARCHAR(500),
  last_login_at TIMESTAMP,
  last_login_platform VARCHAR(20),
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

-- Lokácie
CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  type VARCHAR(20) NOT NULL,  -- 'warehouse', 'project', 'vehicle', 'other'
  code VARCHAR(20),
  address TEXT,
  gps_lat DECIMAL(10, 8),
  gps_lng DECIMAL(11, 8),
  
  parent_location_id UUID REFERENCES locations(id),
  responsible_user_id UUID REFERENCES users(id),
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Kategórie náradia
CREATE TABLE categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  code VARCHAR(20),
  parent_category_id UUID REFERENCES categories(id),
  
  default_maintenance_interval_days INTEGER,
  requires_certification BOOLEAN DEFAULT false,
  
  icon VARCHAR(50),
  color VARCHAR(7),
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- EQUIPMENT & TAGS
-- ============================================

-- Náradie/Vybavenie
CREATE TABLE equipment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  category_id UUID REFERENCES categories(id),
  model_id UUID REFERENCES equipment_models(id),
  serial_number VARCHAR(100),
  internal_code VARCHAR(50) UNIQUE,
  
  manufacturer VARCHAR(100),
  model VARCHAR(100),
  
  purchase_date DATE,
  purchase_price DECIMAL(12, 2),
  current_value DECIMAL(12, 2),
  warranty_expiry DATE,
  
  condition VARCHAR(20) DEFAULT 'good',  -- 'new', 'good', 'fair', 'poor', 'broken'
  status VARCHAR(20) DEFAULT 'available',  -- 'available', 'checked_out', 'maintenance', 'retired'
  
  photo_url VARCHAR(500),
  
  current_location_id UUID REFERENCES locations(id),
  current_holder_id UUID REFERENCES users(id),
  home_location_id UUID REFERENCES locations(id),
  
  -- Príslušenstvo
  is_main_item BOOLEAN DEFAULT true,
  parent_equipment_id UUID REFERENCES equipment(id),
  is_transferable BOOLEAN DEFAULT true,
  
  -- Kalibrácia
  requires_calibration BOOLEAN DEFAULT false,
  calibration_interval_days INTEGER,
  last_calibration_date DATE,
  next_calibration_date DATE,
  calibration_status VARCHAR(20),  -- 'valid', 'expiring', 'expired', 'not_required'
  
  next_maintenance_date DATE,
  last_maintenance_date DATE,
  
  notes TEXT,
  custom_fields JSONB,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

-- Výrobcovia
CREATE TABLE manufacturers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  website VARCHAR(255),
  support_email VARCHAR(255),
  support_phone VARCHAR(50),
  logo_url VARCHAR(500),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Modely zariadení
CREATE TABLE equipment_models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manufacturer_id UUID REFERENCES manufacturers(id),
  category_id UUID REFERENCES categories(id),
  name VARCHAR(100) NOT NULL,
  full_name VARCHAR(200),
  default_calibration_interval_days INTEGER,
  requires_calibration BOOLEAN DEFAULT false,
  manual_url VARCHAR(500),
  specifications JSONB,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Fotky zariadenia
CREATE TABLE equipment_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) ON DELETE CASCADE NOT NULL,
  photo_type VARCHAR(20) NOT NULL,  -- 'main', 'detail', 'label', 'damage', 'calibration'
  file_url VARCHAR(500) NOT NULL,
  thumbnail_url VARCHAR(500),
  local_path VARCHAR(500),
  is_synced BOOLEAN DEFAULT false,
  description TEXT,
  sort_order INTEGER DEFAULT 0,
  uploaded_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Typy príslušenstva
CREATE TABLE accessory_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  icon VARCHAR(50),
  default_for_categories UUID[],
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Kalibrácie
CREATE TABLE calibrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  calibration_type VARCHAR(20) NOT NULL,  -- 'initial', 'periodic', 'after_repair', 'verification'
  calibration_date DATE NOT NULL,
  valid_until DATE NOT NULL,
  next_calibration_date DATE,
  performed_by_type VARCHAR(20),  -- 'internal', 'external', 'manufacturer'
  performed_by_name VARCHAR(200),
  calibration_lab VARCHAR(200),
  certificate_number VARCHAR(100),
  certificate_url VARCHAR(500),
  result VARCHAR(20) NOT NULL,  -- 'passed', 'passed_with_adjustment', 'failed'
  cost DECIMAL(10, 2),
  notes TEXT,
  attachments JSONB,
  recorded_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Nastavenia upozornení na kalibrácie
CREATE TABLE calibration_reminder_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope_type VARCHAR(20) NOT NULL,  -- 'global', 'category', 'equipment'
  category_id UUID REFERENCES categories(id),
  equipment_id UUID REFERENCES equipment(id),
  days_before INTEGER[] DEFAULT '{30, 14, 7, 1}',
  notify_holder BOOLEAN DEFAULT true,
  notify_manager BOOLEAN DEFAULT true,
  notify_users UUID[],
  notify_push BOOLEAN DEFAULT true,
  notify_email BOOLEAN DEFAULT true,
  is_active BOOLEAN DEFAULT true,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tagy (QR, RFID, Barcode)
CREATE TABLE equipment_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id),
  
  tag_type VARCHAR(20) NOT NULL,  -- 'qr_code', 'rfid_nfc', 'rfid_uhf', 'barcode'
  tag_value VARCHAR(255) UNIQUE NOT NULL,
  
  rfid_uid VARCHAR(32),
  rfid_technology VARCHAR(50),
  
  status VARCHAR(20) DEFAULT 'active',  -- 'active', 'damaged', 'lost', 'replaced'
  
  printed_at TIMESTAMP,
  applied_at TIMESTAMP,
  last_scanned_at TIMESTAMP,
  scan_count INTEGER DEFAULT 0,
  
  batch_id UUID,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- OPERATIONS
-- ============================================

-- Výpožičky (Check-in/Check-out)
CREATE TABLE checkouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  user_id UUID REFERENCES users(id) NOT NULL,
  location_id UUID REFERENCES locations(id),
  
  checkout_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expected_return_at TIMESTAMP,
  actual_return_at TIMESTAMP,
  
  checkout_condition VARCHAR(20),
  checkout_photo_url VARCHAR(500),
  checkout_notes TEXT,
  checkout_gps_lat DECIMAL(10, 8),
  checkout_gps_lng DECIMAL(11, 8),
  
  return_condition VARCHAR(20),
  return_photo_url VARCHAR(500),
  return_notes TEXT,
  return_gps_lat DECIMAL(10, 8),
  return_gps_lng DECIMAL(11, 8),
  
  checked_out_by UUID REFERENCES users(id),
  checked_in_by UUID REFERENCES users(id),
  
  status VARCHAR(20) DEFAULT 'active',  -- 'active', 'returned', 'overdue'
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Požiadavky o transfer (P2P požičiavanie)
CREATE TABLE transfer_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  request_type VARCHAR(20) NOT NULL,  -- 'direct', 'broadcast', 'offer'
  
  equipment_id UUID REFERENCES equipment(id),
  category_id UUID REFERENCES categories(id),
  
  requester_id UUID REFERENCES users(id) NOT NULL,
  holder_id UUID REFERENCES users(id),
  
  location_id UUID REFERENCES locations(id),
  location_note VARCHAR(200),
  
  needed_from TIMESTAMP,
  needed_until TIMESTAMP,
  message TEXT,
  
  status VARCHAR(20) DEFAULT 'pending',
  -- 'pending', 'accepted', 'rejected', 'cancelled', 'expired', 'completed', 'requires_approval'
  
  requires_leader_approval BOOLEAN DEFAULT false,
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP,
  rejection_reason TEXT,
  
  responded_at TIMESTAMP,
  completed_at TIMESTAMP,
  expires_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

-- Ponuky na broadcast požiadavky
CREATE TABLE transfer_offers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id UUID REFERENCES transfer_requests(id) ON DELETE CASCADE,
  offerer_id UUID REFERENCES users(id) NOT NULL,
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  message TEXT,
  status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected'
  created_at TIMESTAMP DEFAULT NOW()
);

-- História úspešných transferov
CREATE TABLE transfers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  request_id UUID REFERENCES transfer_requests(id),
  
  from_user_id UUID REFERENCES users(id) NOT NULL,
  to_user_id UUID REFERENCES users(id) NOT NULL,
  
  location_id UUID REFERENCES locations(id),
  transfer_gps_lat DECIMAL(10, 8),
  transfer_gps_lng DECIMAL(11, 8),
  
  from_confirmed_at TIMESTAMP,
  to_confirmed_at TIMESTAMP,
  
  condition_at_transfer VARCHAR(20),
  photo_url VARCHAR(500),
  notes TEXT,
  
  transfer_type VARCHAR(20) DEFAULT 'peer',  -- 'peer', 'checkout', 'checkin', 'handover'
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Údržba
CREATE TABLE maintenance_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  
  type VARCHAR(20) NOT NULL,  -- 'scheduled', 'repair', 'inspection', 'calibration'
  status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'cancelled'
  priority VARCHAR(20) DEFAULT 'normal',  -- 'low', 'normal', 'high', 'urgent'
  
  title VARCHAR(200),
  description TEXT,
  
  scheduled_date DATE,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  
  performed_by UUID REFERENCES users(id),
  assigned_to UUID REFERENCES users(id),
  
  cost DECIMAL(12, 2),
  vendor VARCHAR(200),
  
  next_maintenance_date DATE,
  
  attachments JSONB,  -- Array of file URLs
  notes TEXT,
  
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PRINTING
-- ============================================

-- Tlačiarne
CREATE TABLE printers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  type VARCHAR(50) NOT NULL,  -- 'zebra_zpl', 'brother_ql', 'dymo', 'generic_escpos'
  
  connection_type VARCHAR(20),  -- 'usb', 'bluetooth', 'network'
  connection_address VARCHAR(255),
  
  dpi INTEGER DEFAULT 203,
  default_template_id UUID,
  
  is_active BOOLEAN DEFAULT true,
  last_seen_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Šablóny štítkov
CREATE TABLE label_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  width_mm DECIMAL(5, 2),
  height_mm DECIMAL(5, 2),
  
  template_type VARCHAR(20),  -- 'zpl', 'escpos', 'json'
  template_content TEXT,
  
  includes_qr BOOLEAN DEFAULT true,
  includes_barcode BOOLEAN DEFAULT false,
  includes_name BOOLEAN DEFAULT true,
  includes_serial BOOLEAN DEFAULT true,
  includes_category BOOLEAN DEFAULT false,
  includes_logo BOOLEAN DEFAULT false,
  
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tlačové úlohy
CREATE TABLE print_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  printer_id UUID REFERENCES printers(id),
  template_id UUID REFERENCES label_templates(id),
  
  status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'printing', 'completed', 'failed'
  
  total_count INTEGER,
  printed_count INTEGER DEFAULT 0,
  failed_count INTEGER DEFAULT 0,
  
  error_message TEXT,
  
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE TABLE print_job_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  print_job_id UUID REFERENCES print_jobs(id) ON DELETE CASCADE,
  equipment_id UUID REFERENCES equipment(id),
  tag_id UUID REFERENCES equipment_tags(id),
  
  status VARCHAR(20) DEFAULT 'pending',
  printed_at TIMESTAMP
);

-- ============================================
-- SYSTEM
-- ============================================

-- Notifikácie
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) NOT NULL,
  
  type VARCHAR(50) NOT NULL,
  title VARCHAR(200) NOT NULL,
  message TEXT,
  
  related_entity_type VARCHAR(50),
  related_entity_id UUID,
  
  is_read BOOLEAN DEFAULT false,
  read_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  
  entity_type VARCHAR(50),
  entity_id UUID,
  
  old_values JSONB,
  new_values JSONB,
  
  ip_address INET,
  user_agent TEXT,
  platform VARCHAR(20),
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Systémové nastavenia
CREATE TABLE system_settings (
  key VARCHAR(100) PRIMARY KEY,
  value JSONB,
  description TEXT,
  updated_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_equipment_location ON equipment(current_location_id);
CREATE INDEX idx_equipment_holder ON equipment(current_holder_id);
CREATE INDEX idx_equipment_category ON equipment(category_id);

CREATE INDEX idx_tags_value ON equipment_tags(tag_value);
CREATE INDEX idx_tags_rfid ON equipment_tags(rfid_uid);
CREATE INDEX idx_tags_equipment ON equipment_tags(equipment_id);

CREATE INDEX idx_checkouts_equipment ON checkouts(equipment_id);
CREATE INDEX idx_checkouts_user ON checkouts(user_id);
CREATE INDEX idx_checkouts_status ON checkouts(status);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);
```

---

## API Endpointy

### Autentifikácia
```
POST   /api/auth/login              # Prihlásenie (email + heslo)
POST   /api/auth/logout             # Odhlásenie
POST   /api/auth/refresh            # Obnovenie JWT
GET    /api/auth/me                 # Aktuálny používateľ + permissions
PUT    /api/auth/password           # Zmena hesla
POST   /api/auth/forgot-password    # Reset hesla
```

### Náradie
```
GET    /api/equipment               # Zoznam (filtre: category, status, location, holder)
POST   /api/equipment               # Vytvoriť [manager+]
GET    /api/equipment/{id}          # Detail
PUT    /api/equipment/{id}          # Upraviť [manager+]
DELETE /api/equipment/{id}          # Zmazať [admin+]
GET    /api/equipment/{id}/history  # História (checkouts, maintenance)
POST   /api/equipment/bulk-import   # Hromadný import [manager+]
GET    /api/equipment/export        # Export CSV/Excel [manager+]

# Fotky
GET    /api/equipment/{id}/photos
POST   /api/equipment/{id}/photos
DELETE /api/equipment/{id}/photos/{photo_id}
POST   /api/photos/sync             # Sync offline fotiek

# Príslušenstvo
GET    /api/equipment/{id}/accessories
POST   /api/equipment/{id}/accessories
DELETE /api/equipment/{id}/accessories/{acc_id}
```

### Onboarding (pridávanie náradia)
```
POST   /api/onboarding/start                      # Začať onboarding session
POST   /api/onboarding/{session}/scan             # Krok 1: Skenovanie tagu
POST   /api/onboarding/{session}/photos           # Krok 2: Upload fotiek
POST   /api/onboarding/{session}/details          # Krok 3: Základné info
POST   /api/onboarding/{session}/accessories      # Krok 4: Príslušenstvo
POST   /api/onboarding/{session}/calibration      # Krok 5: Kalibrácia
POST   /api/onboarding/{session}/complete         # Dokončiť
```

### Výrobcovia a Modely
```
GET    /api/manufacturers
POST   /api/manufacturers
GET    /api/manufacturers/{id}/models
GET    /api/models?category_id={}&manufacturer_id={}
POST   /api/models
GET    /api/accessory-types
```

### Kalibrácie
```
# CRUD
GET    /api/equipment/{id}/calibrations           # História kalibrácií
POST   /api/equipment/{id}/calibrations           # Pridať kalibráciu
PUT    /api/calibrations/{id}                     # Upraviť
POST   /api/calibrations/{id}/certificate         # Upload certifikátu

# Dashboard a reporting
GET    /api/calibrations/dashboard                # Štatistiky a prehľad
GET    /api/calibrations/due?status={}&days={}    # Zariadenia na kalibráciu
GET    /api/calibrations/export?format={}         # Export plánu

# Nastavenia upozornení
GET    /api/calibrations/reminder-settings
POST   /api/calibrations/reminder-settings
GET    /api/calibrations/my-notifications
```

### Check-out / Check-in
```
POST   /api/checkouts                    # Výdaj náradia
PUT    /api/checkouts/{id}/return        # Vrátenie
GET    /api/checkouts                    # História (filtre)
GET    /api/checkouts/active             # Aktívne výpožičky
GET    /api/checkouts/overdue            # Oneskorené
POST   /api/checkouts/{id}/extend        # Predĺženie termínu
```

### Transfery (P2P požičiavanie medzi používateľmi)
```
# Požiadavky
POST   /api/transfers/requests                    # Vytvoriť požiadavku o náradie
GET    /api/transfers/requests/sent               # Moje odoslané požiadavky
GET    /api/transfers/requests/received           # Požiadavky na mňa
GET    /api/transfers/requests/available          # Broadcast požiadavky (kde môžem ponúknuť)
POST   /api/transfers/requests/{id}/respond       # Prijať/Odmietnuť požiadavku
POST   /api/transfers/requests/{id}/cancel        # Zrušiť moju požiadavku

# Ponuky (pre broadcast)
POST   /api/transfers/requests/{id}/offer         # Ponúknuť náradie
POST   /api/transfers/offers/{id}/accept          # Akceptovať ponuku

# Samotný transfer
POST   /api/transfers/{id}/confirm-handover       # Potvrdiť odovzdanie (odovzdávajúci)
POST   /api/transfers/{id}/confirm-receipt        # Potvrdiť príjem (prijímajúci)
GET    /api/transfers/history                     # História transferov

# Schvaľovanie (Leader/Manager)
GET    /api/transfers/pending-approval            # Čakajúce schválenia
POST   /api/transfers/requests/{id}/approve       # Schváliť/Zamietnuť
```

### Tagy
```
GET    /api/tags                         # Zoznam tagov
POST   /api/tags/generate                # Generovať nové QR kódy
POST   /api/tags/{id}/assign             # Priradiť k náradiu
POST   /api/tags/{id}/replace            # Vymeniť poškodený tag
GET    /api/tags/lookup?value={value}    # Vyhľadať podľa QR/RFID hodnoty
POST   /api/tags/rfid/register           # Registrovať RFID tag
POST   /api/tags/rfid/bulk-scan          # Hromadný RFID sken (inventúra)
```

### Tlač
```
GET    /api/printers                     # Zoznam tlačiarní
POST   /api/printers                     # Pridať tlačiareň [admin+]
POST   /api/printers/{id}/test           # Test tlače
GET    /api/label-templates              # Šablóny štítkov
POST   /api/label-templates              # Vytvoriť šablónu [admin+]
POST   /api/label-templates/{id}/preview # Preview s konkrétnym náradím
POST   /api/print-jobs                   # Vytvoriť tlačovú úlohu
GET    /api/print-jobs/{id}              # Stav úlohy
```

### Údržba
```
GET    /api/maintenance                  # Zoznam záznamov
POST   /api/maintenance                  # Vytvoriť záznam
PUT    /api/maintenance/{id}             # Upraviť
PUT    /api/maintenance/{id}/complete    # Dokončiť
GET    /api/maintenance/upcoming         # Nadchádzajúce údržby
GET    /api/maintenance/overdue          # Oneskorené údržby
```

### Používatelia
```
GET    /api/users                        # Zoznam (scope podľa role)
POST   /api/users                        # Vytvoriť [manager+]
GET    /api/users/{id}                   # Detail
PUT    /api/users/{id}                   # Upraviť
DELETE /api/users/{id}                   # Deaktivovať [admin+]
GET    /api/users/{id}/equipment         # Náradie používateľa
GET    /api/users/team                   # Môj tím [leader+]
```

### Lokácie
```
GET    /api/locations                    # Zoznam
POST   /api/locations                    # Vytvoriť [manager+]
PUT    /api/locations/{id}               # Upraviť
DELETE /api/locations/{id}               # Zmazať [admin+]
GET    /api/locations/{id}/equipment     # Náradie na lokácii
GET    /api/locations/tree               # Hierarchická štruktúra
```

### Kategórie
```
GET    /api/categories                   # Zoznam
POST   /api/categories                   # Vytvoriť [manager+]
PUT    /api/categories/{id}              # Upraviť
DELETE /api/categories/{id}              # Zmazať [admin+]
GET    /api/categories/tree              # Hierarchická štruktúra
```

### Reporty
```
GET    /api/reports/equipment-summary    # Súhrn náradia
GET    /api/reports/checkout-stats       # Štatistiky výpožičiek
GET    /api/reports/maintenance-stats    # Štatistiky údržby
GET    /api/reports/user-activity        # Aktivita používateľov
GET    /api/reports/inventory-value      # Hodnota inventáru
GET    /api/reports/export/{type}        # Export reportu (pdf, xlsx)
```

### Notifikácie
```
GET    /api/notifications                # Moje notifikácie
PUT    /api/notifications/{id}/read      # Označiť ako prečítané
PUT    /api/notifications/read-all       # Označiť všetky
DELETE /api/notifications/{id}           # Zmazať
```

### Audit Log [admin+]
```
GET    /api/audit                        # Zoznam (filtre: user, action, entity, date)
GET    /api/audit/export                 # Export
```

### Nastavenia [admin+]
```
GET    /api/settings                     # Všetky nastavenia
PUT    /api/settings/{key}               # Upraviť nastavenie
GET    /api/settings/system              # Systémové info [superadmin]
PUT    /api/settings/system              # Systémové nastavenia [superadmin]
```

---

## Role-Based Access Control (RBAC)

### Prehľad Rolí

| Rola | Kód | Platforma | Popis |
|------|-----|-----------|-------|
| **Field Worker** | `worker` | Android | Terénny pracovník, základné operácie |
| **Team Leader** | `leader` | Android + Web | Vedúci tímu, schvaľovanie |
| **Manager** | `manager` | Web | Vedúci oddelenia, reporting |
| **Admin** | `admin` | Web | Správca systému |
| **Super Admin** | `superadmin` | Web | Plná kontrola |

### Matica Oprávnení

```
                          Worker  Leader  Manager  Admin  SuperAdmin
─────────────────────────────────────────────────────────────────────
ANDROID APP
  Scanner                   ✅      ✅       -       -       -
  Check-out (sebe)          ✅      ✅       -       -       -
  Check-out (tím)           -       ✅       -       -       -
  Check-in                  ✅      ✅       -       -       -
  Nahlásenie problému       ✅      ✅       -       -       -
  Schvaľovanie              -       ✅       -       -       -
  Transfer - požiadať       ✅      ✅       -       -       -
  Transfer - odpovedať      ✅      ✅       -       -       -
  Transfer - schváliť       -       ✅       -       -       -

WEB APP
  Dashboard                 -       ✅       ✅      ✅      ✅
  Equipment - View          -       ✅       ✅      ✅      ✅
  Equipment - Create        -       -        ✅      ✅      ✅
  Equipment - Edit          -       -        ✅      ✅      ✅
  Equipment - Delete        -       -        -       ✅      ✅
  Equipment - Onboard       -       -        ✅      ✅      ✅
  Equipment - Add Photos    ✅      ✅       ✅      ✅      ✅
  Accessories - Manage      -       -        ✅      ✅      ✅
  QR/Tags - Manage          -       -        ✅      ✅      ✅
  Print Labels              -       -        ✅      ✅      ✅
  Calibrations - View       ✅      ✅       ✅      ✅      ✅
  Calibrations - Create     -       ✅       ✅      ✅      ✅
  Calibrations - Settings   -       -        ✅      ✅      ✅
  Users - View Team         -       ✅       ✅      ✅      ✅
  Users - Create            -       -        ✅      ✅      ✅
  Users - Manage Roles      -       -        -       ✅      ✅
  Reports - Own             -       ✅       ✅      ✅      ✅
  Reports - All             -       -        ✅      ✅      ✅
  Transfers - View          -       ✅       ✅      ✅      ✅
  Transfers - Approve       -       ✅       ✅      ✅      ✅
  Audit Log                 -       -        -       ✅      ✅
  Settings                  -       -        ✅      ✅      ✅
  System Settings           -       -        -       -       ✅
```

### Data Scoping

- **Worker**: Vidí len svoje náradie + dostupné na sklade
- **Leader**: Vidí náradie svojho tímu
- **Manager**: Vidí náradie svojho oddelenia
- **Admin/SuperAdmin**: Vidí všetko

---

## Android Aplikácia - Obrazovky

```
📱 ANDROID APP STRUCTURE
═══════════════════════════════════════

🏠 HOME (Dashboard)
├── Moje náradie (počet, stav)
├── Notifikácie (vrátane kalibrácií)
├── Quick actions
│   ├── Skenovať
│   ├── Check-out
│   ├── Check-in
│   └── [Manager] Pridať náradie
└── [Leader] Náradie tímu

➕ ONBOARDING WIZARD [Manager+]
├── Krok 1: Skenovanie
│   ├── QR kód
│   ├── Čiarový kód
│   ├── NFC tag
│   └── Manuálne zadanie
├── Krok 2: Fotografie (1-5)
│   ├── Hlavná [povinná]
│   ├── Detail, Štítok, Poškodenie
│   └── Offline queue pre sync
├── Krok 3: Základné info
│   ├── Názov, Kategória
│   ├── Výrobca (autocomplete)
│   ├── Model (autocomplete)
│   └── Sériové číslo, Kód
├── Krok 4: Príslušenstvo
│   ├── Batérie, Nabíjačky, Kufríky
│   ├── Vlastný QR pre každé
│   └── Zoskupenie pod hlavné
├── Krok 5: Kalibrácia
│   ├── Vyžaduje? [toggle]
│   ├── Interval
│   ├── Posledná kalibrácia
│   └── Certifikát [foto]
└── Krok 6: Súhrn + Dokončenie

📷 SCANNER
├── Camera preview
├── QR/Barcode detection
├── NFC tap support
└── → Equipment detail / Actions

🔧 EQUIPMENT DETAIL
├── Základné info + foto
├── QR kód
├── Stav a lokácia
├── Aktuálny držiteľ
├── Akcie:
│   ├── Check-out (ak dostupné)
│   ├── Check-in (ak moje)
│   ├── Nahlásiť problém
│   └── [Leader] Presunúť

📤 CHECK-OUT FLOW
├── 1. Skenovať / Vybrať náradie
├── 2. Vybrať lokáciu/projekt
├── 3. Odfotiť stav (voliteľné)
├── 4. Poznámka (voliteľné)
├── 5. [Leader] Vybrať používateľa
└── 6. Potvrdiť

📥 CHECK-IN FLOW
├── 1. Skenovať / Vybrať náradie
├── 2. Odfotiť stav
├── 3. Stav náradia (ok/poškodené)
├── 4. Poznámka
└── 5. Potvrdiť

📋 MOJE NÁRADIE
├── Zoznam priradeného náradia
├── Filter / Vyhľadávanie
└── → Equipment detail

⚠️ NAHLÁSENIE PROBLÉMU
├── Typ problému
├── Popis
├── Fotka
├── Priorita
└── Odoslať

🔄 TRANSFERY (P2P požičiavanie)
├── Odoslané požiadavky
├── Prijaté požiadavky
├── Aktívne transfery
├── Požiadať o náradie
│   ├── Priama požiadavka (konkrétne náradie)
│   └── Broadcast (hľadám kategóriu)
├── Odpovedať na požiadavku
│   ├── Prijať/Odmietnuť
│   └── Ponúknuť (pri broadcast)
└── Potvrdiť transfer
    ├── Odovzdanie (foto + stav)
    └── Príjem (foto + stav)

👥 TÍM [Leader only]
├── Členovia tímu
├── Náradie tímu
└── Čakajúce schválenia

⚙️ NASTAVENIA
├── Profil
├── Notifikácie
├── Offline data
├── O aplikácii
└── Odhlásiť
```

---

## Web Aplikácia - Obrazovky

```
🖥️ WEB APP STRUCTURE
═══════════════════════════════════════

📊 DASHBOARD
├── Štatistiky (scope podľa role)
│   ├── Celkom náradia
│   ├── Vydané
│   ├── V údržbe
│   └── Vyžaduje pozornosť
├── Grafy
│   ├── Výpožičky za mesiac
│   └── Stav náradia (pie)
├── Upozornenia
├── [Leader] Čakajúce schválenia
└── [Admin] Systémový stav

🔧 NÁRADIE
├── Zoznam
│   ├── Tabuľka s filtrami
│   ├── Bulk akcie
│   └── Export
├── Detail
│   ├── Info + editácia
│   ├── QR kódy/tagy
│   ├── História výpožičiek
│   ├── História údržby
│   └── Audit log
├── Vytvorenie
├── Hromadný import
└── Výpožičky
    ├── Aktívne
    ├── Oneskorené
    └── História

🏷️ QR A TAGY
├── Zoznam tagov
├── Generovanie
├── Priraďovanie
├── RFID správa
└── Tlač štítkov
    ├── Výber tlačiarne
    ├── Výber šablóny
    └── Preview + tlač

🛠️ ÚDRŽBA
├── Plánovač
├── Nadchádzajúce
├── História
└── Štatistiky

📐 KALIBRÁCIE
├── Dashboard
│   ├── Štatistiky (platné/končiace/expirované)
│   ├── Graf: Plán po mesiacoch
│   └── Kritické (vyžadujú pozornosť)
├── Zoznam zariadení
│   ├── Filter: stav, kategória, obdobie
│   ├── Tabuľka s akciami
│   └── Bulk export
├── Pridať kalibráciu
│   ├── Typ, Dátum, Platnosť
│   ├── Laboratórium, Certifikát
│   ├── Výsledok, Náklady
│   └── Upload certifikátu
├── Nastavenia upozornení
│   ├── Globálne
│   ├── Per kategória
│   └── Per zariadenie
└── Export plánu (PDF/Excel)

👥 POUŽÍVATELIA
├── Zoznam
├── Detail + editácia
├── Vytvorenie
├── Oddelenia
└── Import

📍 LOKÁCIE
├── Zoznam + hierarchia
├── Mapa
└── Detail

📈 REPORTY
├── Náradie
├── Výpožičky
├── Údržba
├── Používatelia
└── Export (PDF, Excel)

🔄 TRANSFERY
├── Dashboard (štatistiky)
├── Čakajúce požiadavky
├── Aktívne transfery
├── História
└── Schválenia [Leader+]

✅ SCHVAĽOVANIE
├── Čakajúce
├── Schválené
└── Zamietnuté

📋 AUDIT LOG [Admin+]
├── Zoznam
├── Filtre
└── Export

⚙️ NASTAVENIA
├── Kategórie
├── Šablóny štítkov
├── Tlačiarne
├── [SuperAdmin] Systém
├── [SuperAdmin] Integrácie
└── [SuperAdmin] Role
```

---

## Kľúčové Implementačné Detaily

### 1. QR Kód Formát
```
URL: https://equip.{domain}/scan/{uuid}
Príklad: https://equip.bagron.eu/scan/7a3b4c5d-1234-5678-9abc-def012345678

Fallback (offline): EQT:{uuid}
```

### 2. Offline Mode (Android)
- Room databáza pre lokálnu cache
- Offline queue pre operácie
- WorkManager pre background sync
- Conflict resolution (server wins)

### 3. NFC Workflow
- Scan NFC tag → Získaj UID
- Lookup v DB → Nájdi equipment
- Ak nenájdené → Ponúkni registráciu
- Zápis URL na NTAG tagy

### 4. Tlač Štítkov
- ZPL pre Zebra tlačiarne
- Brother SDK pre QL série
- ESC/POS pre generické
- Bluetooth + Network podpora

### 5. Notifikácie
- Push cez Firebase (Android)
- Email cez SMTP
- In-app notifikácie
- Webhook integrácie

---

## Projektová Štruktúra

```
equipment-tracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── equipment.py
│   │   │   │   ├── checkouts.py
│   │   │   │   ├── tags.py
│   │   │   │   ├── users.py
│   │   │   │   └── ...
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── permissions.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── android/
│   ├── app/src/main/
│   │   ├── java/.../
│   │   │   ├── di/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   ├── ui/
│   │   │   ├── scanner/
│   │   │   ├── print/
│   │   │   └── sync/
│   │   └── res/
│   └── build.gradle.kts
│
├── web/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## Fázy Implementácie

### Fáza 1 - MVP (4-6 týždňov)
- [ ] Backend: Auth, Equipment CRUD, Checkouts
- [ ] Databáza: Core tabuľky
- [ ] Android: Scanner, Check-out/in, Moje náradie
- [ ] Web: Login, Equipment list, základný Dashboard

### Fáza 2 - QR/Tag Management (2-3 týždne)
- [ ] QR generovanie a priraďovanie
- [ ] NFC podpora (Android)
- [ ] Tlač štítkov

### Fáza 3 - Rozšírené funkcie (3-4 týždne)
- [ ] Údržba a servisy
- [ ] Notifikácie (push, email)
- [ ] Offline mode (Android)
- [ ] Reporty a export

### Fáza 4 - Admin & Polish (2-3 týždne)
- [ ] Audit log
- [ ] Systémové nastavenia
- [ ] Hromadné operácie
- [ ] Performance optimalizácia

---

## Deployment

Aplikácia pobeží na Synology NAS s Docker:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data/uploads:/app/uploads
    restart: always

  web:
    build: ./web
    restart: always

  postgres:
    image: postgres:15-alpine
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: always
```
