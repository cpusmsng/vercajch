# Onboarding Náradia a Kalibračný Modul

## 1. Onboarding Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ONBOARDING NOVÉHO NÁRADIA                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  1. SCAN │───►│ 2. FOTO  │───►│ 3. INFO  │───►│ 4. PRÍS- │───►│ 5. KALIB │
│  QR/RFID │    │  (1-5x)  │    │  Detail  │    │ LUŠENSTVO│    │  RÁCIA   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
  Skenuj         Odfotiť        Vyplniť:        Pridať:        Ak potrebuje:
  - QR kód       - Hlavná       - Názov         - Batéria      - Dátum kalib.
  - Čiar. kód    - Detail       - Kategória     - Nabíjačka    - Platnosť
  - RFID tag     - Štítok       - Výrobca       - Kufrík       - Certifikát
  - Manuálne     - Poškodenia   - Model         - Káble        - Interval
                                - Sériové č.    - Nadstavce
                                - Poznámky      (každé s QR)
```

---

## 2. Databázový Model

```sql
-- ============================================
-- ROZŠÍRENIE EQUIPMENT TABUĽKY
-- ============================================

ALTER TABLE equipment ADD COLUMN is_main_item BOOLEAN DEFAULT true;  -- Je to hlavné náradie?
ALTER TABLE equipment ADD COLUMN parent_equipment_id UUID REFERENCES equipment(id);  -- Ak je príslušenstvo
ALTER TABLE equipment ADD COLUMN requires_calibration BOOLEAN DEFAULT false;
ALTER TABLE equipment ADD COLUMN calibration_interval_days INTEGER;  -- Napr. 365 = ročne
ALTER TABLE equipment ADD COLUMN last_calibration_date DATE;
ALTER TABLE equipment ADD COLUMN next_calibration_date DATE;
ALTER TABLE equipment ADD COLUMN calibration_status VARCHAR(20);  -- 'valid', 'expiring', 'expired', 'not_required'

-- ============================================
-- FOTKY ZARIADENIA
-- ============================================

CREATE TABLE equipment_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) ON DELETE CASCADE NOT NULL,
  
  photo_type VARCHAR(20) NOT NULL,  
  -- 'main'        = Hlavná fotka (zobrazuje sa v zozname)
  -- 'detail'      = Detailná fotka
  -- 'label'       = Fotka štítku/sériového čísla
  -- 'damage'      = Fotka poškodenia
  -- 'accessory'   = Fotka príslušenstva
  -- 'calibration' = Fotka kalibračného štítku
  
  file_url VARCHAR(500) NOT NULL,
  thumbnail_url VARCHAR(500),
  
  -- Offline sync
  local_path VARCHAR(500),  -- Cesta na zariadení (pre sync)
  is_synced BOOLEAN DEFAULT false,
  sync_error TEXT,
  
  -- Metadata
  file_size_bytes INTEGER,
  width INTEGER,
  height INTEGER,
  
  description TEXT,
  taken_at TIMESTAMP,
  uploaded_at TIMESTAMP,
  uploaded_by UUID REFERENCES users(id),
  
  sort_order INTEGER DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- VÝROBCOVIA A MODELY
-- ============================================

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

CREATE TABLE equipment_models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manufacturer_id UUID REFERENCES manufacturers(id),
  category_id UUID REFERENCES categories(id),
  
  name VARCHAR(100) NOT NULL,  -- "DFR-250"
  full_name VARCHAR(200),       -- "Detektor úniku plynu DFR-250"
  
  -- Predvolené hodnoty pri onboardingu
  default_calibration_interval_days INTEGER,
  requires_calibration BOOLEAN DEFAULT false,
  
  -- Dokumentácia
  manual_url VARCHAR(500),
  datasheet_url VARCHAR(500),
  
  specifications JSONB,  -- Technické parametre
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Prepojenie equipment s modelom
ALTER TABLE equipment ADD COLUMN model_id UUID REFERENCES equipment_models(id);

-- ============================================
-- PRÍSLUŠENSTVO (ACCESSORY SETS)
-- ============================================

CREATE TABLE accessory_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,  -- "Batéria", "Nabíjačka", "Kufrík"
  icon VARCHAR(50),
  
  -- Predvolené pre kategórie
  default_for_categories UUID[],  -- Automaticky ponúkať pri onboardingu
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Príslušenstvo je tiež equipment, len s parent_equipment_id
-- Môže mať vlastný QR/tag

-- ============================================
-- KALIBRÁCIE
-- ============================================

CREATE TABLE calibrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  
  -- Typ kalibrácie
  calibration_type VARCHAR(20) NOT NULL,
  -- 'initial'     = Prvotná kalibrácia (z výroby)
  -- 'periodic'    = Pravidelná kalibrácia
  -- 'after_repair'= Po oprave
  -- 'verification'= Overenie (medzikalibrácia)
  
  -- Dátumy
  calibration_date DATE NOT NULL,
  valid_until DATE NOT NULL,
  next_calibration_date DATE,
  
  -- Kto kalibroval
  performed_by_type VARCHAR(20),  -- 'internal', 'external', 'manufacturer'
  performed_by_name VARCHAR(200),
  calibration_lab VARCHAR(200),
  
  -- Certifikát
  certificate_number VARCHAR(100),
  certificate_url VARCHAR(500),
  
  -- Výsledky
  result VARCHAR(20) NOT NULL,  -- 'passed', 'passed_with_adjustment', 'failed'
  notes TEXT,
  
  -- Náklady
  cost DECIMAL(10, 2),
  cost_currency VARCHAR(3) DEFAULT 'EUR',
  
  -- Prílohy
  attachments JSONB,  -- Array of {name, url, type}
  
  -- Kto zaznamenal
  recorded_by UUID REFERENCES users(id),
  recorded_at TIMESTAMP DEFAULT NOW(),
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- NASTAVENIA UPOZORNENÍ NA KALIBRÁCIE
-- ============================================

CREATE TABLE calibration_reminder_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Môže byť globálne, per kategória, alebo per equipment
  scope_type VARCHAR(20) NOT NULL,  -- 'global', 'category', 'equipment'
  category_id UUID REFERENCES categories(id),
  equipment_id UUID REFERENCES equipment(id),
  
  -- Koľko dní pred expiráciou upozorniť
  days_before INTEGER[] DEFAULT '{30, 14, 7, 1}',  -- Viackrát
  
  -- Koho upozorniť
  notify_holder BOOLEAN DEFAULT true,       -- Aktuálneho držiteľa
  notify_manager BOOLEAN DEFAULT true,      -- Manažéra kategórie/oddelenia
  notify_users UUID[],                      -- Konkrétnych používateľov
  
  -- Ako upozorniť
  notify_push BOOLEAN DEFAULT true,
  notify_email BOOLEAN DEFAULT true,
  notify_in_app BOOLEAN DEFAULT true,
  
  is_active BOOLEAN DEFAULT true,
  
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Odoslané upozornenia (aby sme neposlali duplicitne)
CREATE TABLE calibration_reminders_sent (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  calibration_id UUID REFERENCES calibrations(id),
  
  reminder_type VARCHAR(20),  -- '30_days', '14_days', '7_days', '1_day', 'expired'
  sent_to UUID REFERENCES users(id),
  sent_via VARCHAR(20),  -- 'push', 'email', 'in_app'
  
  sent_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXY
-- ============================================

CREATE INDEX idx_equipment_parent ON equipment(parent_equipment_id);
CREATE INDEX idx_equipment_calibration ON equipment(next_calibration_date) WHERE requires_calibration = true;
CREATE INDEX idx_equipment_photos ON equipment_photos(equipment_id);
CREATE INDEX idx_calibrations_equipment ON calibrations(equipment_id);
CREATE INDEX idx_calibrations_valid ON calibrations(valid_until);
```

---

## 3. API Endpointy

### 3.1 Onboarding

```python
# === ONBOARDING ===

# Začať onboarding - vygeneruje session ID
POST /api/onboarding/start
Response: { 
  "session_id": "uuid",
  "expires_at": "...",
  "steps": ["scan", "photos", "details", "accessories", "calibration"]
}

# Krok 1: Skenovanie/Priradenie tagu
POST /api/onboarding/{session_id}/scan
{
  "tag_type": "qr_code",       # qr_code | barcode | rfid_nfc | rfid_uhf | manual
  "tag_value": "ABC123456",    # Hodnota zo skenu
  "rfid_uid": "04:A2:B3:...",  # Pre RFID
  "manual_code": null          # Pre manuálne zadanie
}
Response: {
  "tag_id": "uuid",
  "is_new_tag": true,
  "existing_equipment": null   # Alebo equipment ak tag už existuje
}

# Krok 2: Upload fotiek
POST /api/onboarding/{session_id}/photos
Content-Type: multipart/form-data
{
  "photo": <file>,
  "photo_type": "main",        # main | detail | label | damage
  "description": "Predná strana"
}
Response: {
  "photo_id": "uuid",
  "url": "...",
  "thumbnail_url": "..."
}

# Krok 3: Základné info
POST /api/onboarding/{session_id}/details
{
  "name": "Detektor úniku plynu",
  "category_id": "uuid",
  "manufacturer_id": "uuid",    # Alebo manufacturer_name pre nového
  "manufacturer_name": null,
  "model_id": "uuid",           # Alebo model_name pre nový
  "model_name": null,
  "serial_number": "SN123456",
  "internal_code": "DET-001",   # Interné označenie
  "purchase_date": "2024-01-15",
  "purchase_price": 1500.00,
  "warranty_expiry": "2026-01-15",
  "notes": "Zakúpené pre tím A",
  "custom_fields": {}
}

# Krok 4: Príslušenstvo
POST /api/onboarding/{session_id}/accessories
{
  "accessories": [
    {
      "name": "Batéria Li-Ion 2Ah",
      "accessory_type_id": "uuid",
      "tag_value": "BAT-001",      # Voliteľné - ak má vlastný štítok
      "serial_number": "BAT123",
      "quantity": 2                 # Počet kusov
    },
    {
      "name": "Nabíjačka",
      "accessory_type_id": "uuid",
      "tag_value": null
    },
    {
      "name": "Kufrík",
      "accessory_type_id": "uuid",
      "tag_value": "CASE-001"
    }
  ]
}

# Krok 5: Kalibrácia (ak potrebuje)
POST /api/onboarding/{session_id}/calibration
{
  "requires_calibration": true,
  "calibration_interval_days": 365,
  "initial_calibration": {
    "calibration_date": "2024-01-10",
    "valid_until": "2025-01-10",
    "certificate_number": "CAL-2024-001",
    "performed_by_name": "SMÚ Bratislava",
    "calibration_lab": "Slovenský metrologický ústav"
  }
}

# Dokončiť onboarding
POST /api/onboarding/{session_id}/complete
{
  "initial_location_id": "uuid",
  "initial_holder_id": "uuid"     # Voliteľné - hneď priradiť
}
Response: {
  "equipment_id": "uuid",
  "accessories": [{"id": "uuid", "name": "..."}],
  "tag_id": "uuid"
}

# === MANUFACTURERS & MODELS ===

GET    /api/manufacturers
POST   /api/manufacturers
GET    /api/manufacturers/{id}/models

GET    /api/models?category_id={}&manufacturer_id={}
POST   /api/models

# === PHOTOS ===

GET    /api/equipment/{id}/photos
POST   /api/equipment/{id}/photos
DELETE /api/equipment/{id}/photos/{photo_id}
PUT    /api/equipment/{id}/photos/{photo_id}  # Update description, type
PUT    /api/equipment/{id}/photos/reorder     # Zmena poradia

# Sync fotiek z offline
POST   /api/photos/sync
Content-Type: multipart/form-data
{
  "photos": [
    { "equipment_id": "uuid", "local_id": "local-123", "photo": <file>, ... }
  ]
}

# === ACCESSORIES ===

GET    /api/equipment/{id}/accessories       # Príslušenstvo k náradiu
POST   /api/equipment/{id}/accessories       # Pridať príslušenstvo
DELETE /api/equipment/{id}/accessories/{acc_id}  # Odstrániť
PUT    /api/equipment/{id}/accessories/{acc_id}/detach  # Odpojiť (stane sa samostatným)

GET    /api/accessory-types                  # Typy príslušenstva
POST   /api/accessory-types
```

### 3.2 Kalibrácie

```python
# === CALIBRATIONS ===

# Zoznam kalibrácií pre náradie
GET    /api/equipment/{id}/calibrations
Response: [
  {
    "id": "uuid",
    "calibration_date": "2024-01-10",
    "valid_until": "2025-01-10",
    "result": "passed",
    "certificate_number": "CAL-2024-001",
    "days_until_expiry": 180,
    "status": "valid"  # valid | expiring | expired
  }
]

# Pridať novú kalibráciu
POST   /api/equipment/{id}/calibrations
{
  "calibration_type": "periodic",
  "calibration_date": "2024-06-15",
  "valid_until": "2025-06-15",
  "performed_by_type": "external",
  "performed_by_name": "SMÚ Bratislava",
  "calibration_lab": "Slovenský metrologický ústav",
  "certificate_number": "CAL-2024-156",
  "result": "passed",
  "cost": 150.00,
  "notes": "Bez pripomienok"
}

# Upload certifikátu
POST   /api/equipment/{id}/calibrations/{cal_id}/certificate
Content-Type: multipart/form-data
{ "file": <pdf> }

# === CALIBRATION DASHBOARD ===

# Prehľad kalibrácií (pre web)
GET    /api/calibrations/dashboard
{
  "scope": "all",              # all | department | category
  "department_id": null,
  "category_id": null
}
Response: {
  "summary": {
    "total_requiring_calibration": 145,
    "valid": 120,
    "expiring_30_days": 15,
    "expiring_7_days": 5,
    "expired": 5
  },
  "upcoming": [
    { "equipment": {...}, "days_until_expiry": 5, "last_calibration": {...} }
  ],
  "expired": [
    { "equipment": {...}, "days_overdue": 10, "last_calibration": {...} }
  ]
}

# Zoznam zariadení na kalibráciu
GET    /api/calibrations/due
{
  "status": "expiring",        # expiring | expired | all
  "days_ahead": 30,
  "category_id": null,
  "department_id": null
}

# Export kalibračného plánu
GET    /api/calibrations/export
{
  "format": "xlsx",            # xlsx | pdf | csv
  "year": 2024,
  "include_completed": false
}

# === CALIBRATION REMINDERS ===

# Moje nastavenia upozornení
GET    /api/calibrations/reminder-settings

# Nastavenie globálnych upozornení [Admin]
POST   /api/calibrations/reminder-settings
{
  "scope_type": "global",
  "days_before": [30, 14, 7, 1],
  "notify_holder": true,
  "notify_manager": true,
  "notify_push": true,
  "notify_email": true
}

# Nastavenie pre kategóriu [Manager]
POST   /api/calibrations/reminder-settings
{
  "scope_type": "category",
  "category_id": "uuid",
  "days_before": [60, 30, 14, 7],  # Iný interval
  "notify_users": ["uuid1", "uuid2"]  # Špecifickí ľudia
}

# Nastavenie pre konkrétne zariadenie
POST   /api/calibrations/reminder-settings
{
  "scope_type": "equipment",
  "equipment_id": "uuid",
  "days_before": [14, 7, 3, 1],
  "notify_email": true,
  "notify_push": true
}

# Moje notifikácie o kalibráciách
GET    /api/calibrations/my-notifications

# Označiť notifikáciu ako prečítanú
PUT    /api/calibrations/notifications/{id}/read
```

---

## 4. Android Aplikácia - Onboarding Flow

### 4.1 Navigácia

```
📱 ANDROID APP - ONBOARDING
══════════════════════════════════════════════════════

🏠 HOME
└── [FAB Button] "Pridať náradie" (ak má oprávnenie)

➕ ONBOARDING WIZARD
├── Krok 1: Skenovanie
│   ├── QR kód (kamera)
│   ├── Čiarový kód (kamera)
│   ├── NFC tag (tap)
│   ├── RFID (external reader)
│   └── Manuálne zadanie
│
├── Krok 2: Fotografie
│   ├── Hlavná fotka [povinná]
│   ├── + Pridať ďalšiu (max 5)
│   ├── Typ fotky (dropdown)
│   └── Popis (voliteľné)
│
├── Krok 3: Základné info
│   ├── Názov [povinné]
│   ├── Kategória [povinná]
│   ├── Výrobca (autocomplete + nový)
│   ├── Model (autocomplete + nový)
│   ├── Sériové číslo
│   ├── Interný kód
│   └── Poznámky
│
├── Krok 4: Príslušenstvo
│   ├── [+] Pridať príslušenstvo
│   │   ├── Typ (batéria, nabíjačka, ...)
│   │   ├── Názov
│   │   ├── QR/čiarový kód (voliteľné)
│   │   └── Počet kusov
│   └── Zoznam pridaného
│
├── Krok 5: Kalibrácia (ak kategória vyžaduje)
│   ├── Vyžaduje kalibráciu? [toggle]
│   ├── Interval (dni/mesiace/roky)
│   ├── Posledná kalibrácia
│   │   ├── Dátum
│   │   ├── Platnosť do
│   │   ├── Číslo certifikátu
│   │   ├── Kto kalibroval
│   │   └── [Foto certifikátu]
│   └── Nastaviť upozornenia
│
└── Krok 6: Súhrn + Dokončenie
    ├── Preview všetkých údajov
    ├── Priradiť lokáciu
    ├── Priradiť držiteľa (voliteľné)
    └── [Dokončiť]
```

### 4.2 Implementácia

```kotlin
// screens/onboarding/OnboardingWizardScreen.kt

@Composable
fun OnboardingWizardScreen(
    onComplete: (Equipment) -> Unit,
    onCancel: () -> Unit
) {
    val viewModel: OnboardingViewModel = hiltViewModel()
    val state by viewModel.state.collectAsState()
    
    val steps = listOf(
        OnboardingStep.SCAN,
        OnboardingStep.PHOTOS,
        OnboardingStep.DETAILS,
        OnboardingStep.ACCESSORIES,
        OnboardingStep.CALIBRATION,
        OnboardingStep.SUMMARY
    )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Pridať náradie (${state.currentStep + 1}/${steps.size})") },
                navigationIcon = {
                    IconButton(onClick = {
                        if (state.currentStep > 0) viewModel.previousStep()
                        else onCancel()
                    }) {
                        Icon(if (state.currentStep > 0) Icons.ArrowBack else Icons.Close, null)
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            
            // Progress indicator
            LinearProgressIndicator(
                progress = (state.currentStep + 1).toFloat() / steps.size,
                modifier = Modifier.fillMaxWidth()
            )
            
            // Step content
            when (steps[state.currentStep]) {
                OnboardingStep.SCAN -> ScanStep(
                    onScanned = { tagValue, tagType ->
                        viewModel.setTag(tagValue, tagType)
                        viewModel.nextStep()
                    }
                )
                
                OnboardingStep.PHOTOS -> PhotosStep(
                    photos = state.photos,
                    onAddPhoto = { uri, type, description ->
                        viewModel.addPhoto(uri, type, description)
                    },
                    onRemovePhoto = { viewModel.removePhoto(it) },
                    onNext = { viewModel.nextStep() }
                )
                
                OnboardingStep.DETAILS -> DetailsStep(
                    details = state.details,
                    categories = state.categories,
                    manufacturers = state.manufacturers,
                    models = state.models,
                    onDetailsChanged = { viewModel.updateDetails(it) },
                    onNext = { viewModel.nextStep() }
                )
                
                OnboardingStep.ACCESSORIES -> AccessoriesStep(
                    accessories = state.accessories,
                    accessoryTypes = state.accessoryTypes,
                    onAddAccessory = { viewModel.addAccessory(it) },
                    onRemoveAccessory = { viewModel.removeAccessory(it) },
                    onScanAccessory = { /* Open scanner for accessory tag */ },
                    onNext = { viewModel.nextStep() }
                )
                
                OnboardingStep.CALIBRATION -> CalibrationStep(
                    calibration = state.calibration,
                    requiresCalibration = state.details.category?.requiresCalibration ?: false,
                    onCalibrationChanged = { viewModel.updateCalibration(it) },
                    onNext = { viewModel.nextStep() }
                )
                
                OnboardingStep.SUMMARY -> SummaryStep(
                    state = state,
                    locations = state.locations,
                    users = state.users,
                    onLocationSelected = { viewModel.setLocation(it) },
                    onHolderSelected = { viewModel.setHolder(it) },
                    onComplete = {
                        viewModel.complete { equipment ->
                            onComplete(equipment)
                        }
                    }
                )
            }
        }
    }
}

// Krok 2: Fotografie
@Composable
fun PhotosStep(
    photos: List<OnboardingPhoto>,
    onAddPhoto: (Uri, PhotoType, String?) -> Unit,
    onRemovePhoto: (OnboardingPhoto) -> Unit,
    onNext: () -> Unit
) {
    var showCamera by remember { mutableStateOf(false) }
    var selectedPhotoType by remember { mutableStateOf(PhotoType.MAIN) }
    var photoDescription by remember { mutableStateOf("") }
    
    val cameraLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) {
            // Handle captured photo
        }
    }
    
    Column(modifier = Modifier.padding(16.dp)) {
        
        Text(
            "Fotografie náradia",
            style = MaterialTheme.typography.headlineSmall
        )
        
        Text(
            "Pridajte aspoň jednu hlavnú fotku. Môžete pridať až 5 fotografií.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Grid fotiek
        LazyVerticalGrid(
            columns = GridCells.Fixed(3),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(photos) { photo ->
                PhotoCard(
                    photo = photo,
                    onRemove = { onRemovePhoto(photo) }
                )
            }
            
            if (photos.size < 5) {
                item {
                    AddPhotoCard(onClick = { showCamera = true })
                }
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Ďalej
        Button(
            onClick = onNext,
            enabled = photos.any { it.type == PhotoType.MAIN },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Pokračovať")
        }
        
        if (photos.none { it.type == PhotoType.MAIN }) {
            Text(
                "Pridajte hlavnú fotku pre pokračovanie",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
    }
    
    // Camera dialog
    if (showCamera) {
        PhotoCaptureDialog(
            onCapture = { uri ->
                onAddPhoto(uri, selectedPhotoType, photoDescription.ifBlank { null })
                showCamera = false
            },
            onDismiss = { showCamera = false },
            photoType = selectedPhotoType,
            onPhotoTypeChange = { selectedPhotoType = it },
            description = photoDescription,
            onDescriptionChange = { photoDescription = it }
        )
    }
}

// Krok 4: Príslušenstvo
@Composable
fun AccessoriesStep(
    accessories: List<AccessoryItem>,
    accessoryTypes: List<AccessoryType>,
    onAddAccessory: (AccessoryItem) -> Unit,
    onRemoveAccessory: (AccessoryItem) -> Unit,
    onScanAccessory: (AccessoryItem) -> Unit,
    onNext: () -> Unit
) {
    var showAddDialog by remember { mutableStateOf(false) }
    
    Column(modifier = Modifier.padding(16.dp)) {
        
        Text(
            "Príslušenstvo",
            style = MaterialTheme.typography.headlineSmall
        )
        
        Text(
            "Pridajte príslušenstvo, ktoré patrí k tomuto náradiu (batérie, nabíjačky, kufríky...)",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Zoznam príslušenstva
        if (accessories.isEmpty()) {
            EmptyState(
                icon = Icons.Extension,
                title = "Žiadne príslušenstvo",
                subtitle = "Kliknutím pridáte príslušenstvo"
            )
        } else {
            LazyColumn {
                items(accessories) { accessory ->
                    AccessoryCard(
                        accessory = accessory,
                        onRemove = { onRemoveAccessory(accessory) },
                        onScan = { onScanAccessory(accessory) }
                    )
                }
            }
        }
        
        // Pridať
        OutlinedButton(
            onClick = { showAddDialog = true },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Add, null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Pridať príslušenstvo")
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Môžeme preskočiť
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(
                onClick = onNext,
                modifier = Modifier.weight(1f)
            ) {
                Text("Preskočiť")
            }
            Button(
                onClick = onNext,
                modifier = Modifier.weight(1f)
            ) {
                Text("Pokračovať")
            }
        }
    }
    
    if (showAddDialog) {
        AddAccessoryDialog(
            accessoryTypes = accessoryTypes,
            onAdd = { 
                onAddAccessory(it)
                showAddDialog = false
            },
            onDismiss = { showAddDialog = false }
        )
    }
}

// Krok 5: Kalibrácia
@Composable
fun CalibrationStep(
    calibration: CalibrationData?,
    requiresCalibration: Boolean,
    onCalibrationChanged: (CalibrationData?) -> Unit,
    onNext: () -> Unit
) {
    var enabled by remember { mutableStateOf(requiresCalibration) }
    var intervalValue by remember { mutableStateOf("12") }
    var intervalUnit by remember { mutableStateOf("months") }
    var calibrationDate by remember { mutableStateOf<LocalDate?>(null) }
    var validUntil by remember { mutableStateOf<LocalDate?>(null) }
    var certificateNumber by remember { mutableStateOf("") }
    var calibratedBy by remember { mutableStateOf("") }
    var certificatePhotoUri by remember { mutableStateOf<Uri?>(null) }
    
    Column(modifier = Modifier.padding(16.dp)) {
        
        Text(
            "Kalibrácia",
            style = MaterialTheme.typography.headlineSmall
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Toggle
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Vyžaduje kalibráciu", style = MaterialTheme.typography.bodyLarge)
                Text(
                    "Zariadenie bude sledované pre kalibráciu",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Switch(
                checked = enabled,
                onCheckedChange = { enabled = it }
            )
        }
        
        if (enabled) {
            Spacer(modifier = Modifier.height(24.dp))
            
            // Interval
            Text("Interval kalibrácie", style = MaterialTheme.typography.labelLarge)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = intervalValue,
                    onValueChange = { intervalValue = it },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
                ExposedDropdownMenuBox(...) {
                    // months, years, days
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            Divider()
            Spacer(modifier = Modifier.height(16.dp))
            
            // Posledná kalibrácia
            Text("Posledná kalibrácia", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            
            // Dátum kalibrácie
            DatePickerField(
                label = "Dátum kalibrácie",
                value = calibrationDate,
                onValueChange = { calibrationDate = it }
            )
            
            // Platnosť do
            DatePickerField(
                label = "Platnosť do",
                value = validUntil,
                onValueChange = { validUntil = it }
            )
            
            // Číslo certifikátu
            OutlinedTextField(
                value = certificateNumber,
                onValueChange = { certificateNumber = it },
                label = { Text("Číslo certifikátu") },
                modifier = Modifier.fillMaxWidth()
            )
            
            // Kto kalibroval
            OutlinedTextField(
                value = calibratedBy,
                onValueChange = { calibratedBy = it },
                label = { Text("Kalibračné laboratórium") },
                modifier = Modifier.fillMaxWidth()
            )
            
            // Foto certifikátu
            Spacer(modifier = Modifier.height(8.dp))
            if (certificatePhotoUri != null) {
                AsyncImage(
                    model = certificatePhotoUri,
                    contentDescription = "Certifikát",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(150.dp)
                        .clip(RoundedCornerShape(8.dp))
                )
            }
            OutlinedButton(
                onClick = { /* Take photo */ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.CameraAlt, null)
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (certificatePhotoUri == null) "Odfotiť certifikát" else "Zmeniť fotku")
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        Button(
            onClick = {
                if (enabled) {
                    onCalibrationChanged(CalibrationData(
                        intervalDays = calculateDays(intervalValue, intervalUnit),
                        lastCalibration = calibrationDate,
                        validUntil = validUntil,
                        certificateNumber = certificateNumber,
                        calibratedBy = calibratedBy
                    ))
                } else {
                    onCalibrationChanged(null)
                }
                onNext()
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Pokračovať")
        }
    }
}
```

---

## 5. Web Aplikácia - Kalibračný Dashboard

### 5.1 Obrazovky

```
🖥️ WEB APP - KALIBRÁCIE
══════════════════════════════════════════════════════

📊 CALIBRATIONS DASHBOARD
├── Štatistiky
│   ├── Celkom zariadení s kalibráciou: 145
│   ├── Platné: 120 (82%)
│   ├── Končí do 30 dní: 15
│   ├── Končí do 7 dní: 5
│   └── Expirované: 5
│
├── Graf: Kalibrácie po mesiacoch (nasledujúcich 12)
│
├── Kritické (expirované + do 7 dní)
│   └── Tabuľka s akciami
│
└── Export ročného plánu

📋 CALIBRATIONS LIST
├── Filtre
│   ├── Stav (platné/končiace/expirované)
│   ├── Kategória
│   ├── Oddelenie
│   └── Obdobie
│
├── Tabuľka
│   ├── Náradie
│   ├── Kategória
│   ├── Posledná kalibrácia
│   ├── Platnosť do
│   ├── Zostáva dní
│   ├── Stav
│   └── Akcie
│
└── Bulk akcie
    ├── Export
    └── Hromadné plánovanie

➕ ADD/EDIT CALIBRATION DIALOG
├── Typ kalibrácie
├── Dátum
├── Platnosť do
├── Laboratórium
├── Číslo certifikátu
├── Náklady
├── Výsledok
├── Upload certifikátu
└── Poznámky

⚙️ CALIBRATION SETTINGS
├── Globálne nastavenia
│   ├── Predvolený interval upozornení
│   └── Koho upozorňovať
│
├── Per kategória
│   └── Override intervalov
│
└── Kalibračné laboratóriá
    ├── Zoznam
    ├── Kontakty
    └── Ceny
```

### 5.2 React Komponenty

```typescript
// pages/CalibrationDashboard.tsx

export function CalibrationDashboard() {
  const { data: stats } = useQuery(['calibrations', 'stats'], fetchCalibrationStats);
  const { data: critical } = useQuery(['calibrations', 'critical'], fetchCriticalCalibrations);
  const { data: upcoming } = useQuery(['calibrations', 'upcoming'], fetchUpcomingCalibrations);
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Kalibrácie</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => exportCalibrationPlan()}>
            <Download className="w-4 h-4 mr-2" />
            Export plánu
          </Button>
          <Button onClick={() => setShowSettings(true)}>
            <Settings className="w-4 h-4 mr-2" />
            Nastavenia
          </Button>
        </div>
      </div>
      
      {/* Štatistiky */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <StatCard
          title="Celkom sledovaných"
          value={stats?.total}
          icon={<Gauge className="w-6 h-6" />}
        />
        <StatCard
          title="Platné"
          value={stats?.valid}
          percentage={stats?.validPercentage}
          variant="success"
        />
        <StatCard
          title="Končí do 30 dní"
          value={stats?.expiring30}
          variant="warning"
          onClick={() => navigate('/calibrations?status=expiring30')}
        />
        <StatCard
          title="Končí do 7 dní"
          value={stats?.expiring7}
          variant="danger"
          onClick={() => navigate('/calibrations?status=expiring7')}
        />
        <StatCard
          title="Expirované"
          value={stats?.expired}
          variant="danger"
          onClick={() => navigate('/calibrations?status=expired')}
        />
      </div>
      
      {/* Graf */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Plánované kalibrácie</CardTitle>
        </CardHeader>
        <CardContent>
          <CalibrationChart data={stats?.monthlyForecast} />
        </CardContent>
      </Card>
      
      {/* Kritické - potrebujú okamžitú pozornosť */}
      {(critical?.length > 0) && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Vyžaduje okamžitú pozornosť ({critical.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CriticalCalibrationTable data={critical} />
          </CardContent>
        </Card>
      )}
      
      {/* Nadchádzajúce */}
      <Card>
        <CardHeader>
          <CardTitle>Nadchádzajúce kalibrácie (30 dní)</CardTitle>
        </CardHeader>
        <CardContent>
          <UpcomingCalibrationTable data={upcoming} />
        </CardContent>
      </Card>
    </div>
  );
}

// Tabuľka kalibrácií
function CalibrationTable({ data, onAddCalibration }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Náradie</TableHead>
          <TableHead>Kategória</TableHead>
          <TableHead>Posledná kalibrácia</TableHead>
          <TableHead>Platnosť do</TableHead>
          <TableHead>Zostáva</TableHead>
          <TableHead>Stav</TableHead>
          <TableHead>Akcie</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data?.map((item) => (
          <TableRow key={item.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                <img 
                  src={item.equipment.photoUrl} 
                  className="w-10 h-10 rounded object-cover" 
                />
                <div>
                  <div className="font-medium">{item.equipment.name}</div>
                  <div className="text-sm text-gray-500">{item.equipment.internalCode}</div>
                </div>
              </div>
            </TableCell>
            <TableCell>{item.equipment.category?.name}</TableCell>
            <TableCell>
              {item.lastCalibration ? (
                <div>
                  <div>{formatDate(item.lastCalibration.calibrationDate)}</div>
                  <div className="text-sm text-gray-500">
                    {item.lastCalibration.calibrationLab}
                  </div>
                </div>
              ) : (
                <span className="text-gray-400">Žiadna</span>
              )}
            </TableCell>
            <TableCell>{formatDate(item.validUntil)}</TableCell>
            <TableCell>
              <DaysRemaining days={item.daysRemaining} />
            </TableCell>
            <TableCell>
              <CalibrationStatusBadge status={item.status} />
            </TableCell>
            <TableCell>
              <div className="flex gap-1">
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => onAddCalibration(item.equipment)}
                >
                  <Plus className="w-4 h-4" />
                </Button>
                <Button 
                  size="sm" 
                  variant="ghost"
                  onClick={() => navigate(`/equipment/${item.equipment.id}`)}
                >
                  <Eye className="w-4 h-4" />
                </Button>
                {item.lastCalibration?.certificateUrl && (
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => window.open(item.lastCalibration.certificateUrl)}
                  >
                    <FileText className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

// Dialog pre pridanie kalibrácie
function AddCalibrationDialog({ equipment, onSave, onClose }) {
  const [formData, setFormData] = useState({
    calibrationType: 'periodic',
    calibrationDate: new Date(),
    validUntil: addYears(new Date(), 1),
    performedByType: 'external',
    performedByName: '',
    calibrationLab: '',
    certificateNumber: '',
    result: 'passed',
    cost: '',
    notes: ''
  });
  
  const [certificateFile, setCertificateFile] = useState(null);
  
  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Pridať kalibráciu</DialogTitle>
          <DialogDescription>
            {equipment.name} ({equipment.internalCode})
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Typ */}
          <div>
            <Label>Typ kalibrácie</Label>
            <Select 
              value={formData.calibrationType}
              onValueChange={(v) => setFormData({...formData, calibrationType: v})}
            >
              <SelectItem value="periodic">Pravidelná</SelectItem>
              <SelectItem value="initial">Prvotná</SelectItem>
              <SelectItem value="after_repair">Po oprave</SelectItem>
              <SelectItem value="verification">Overenie</SelectItem>
            </Select>
          </div>
          
          {/* Dátumy */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Dátum kalibrácie</Label>
              <DatePicker 
                value={formData.calibrationDate}
                onChange={(d) => setFormData({...formData, calibrationDate: d})}
              />
            </div>
            <div>
              <Label>Platnosť do</Label>
              <DatePicker 
                value={formData.validUntil}
                onChange={(d) => setFormData({...formData, validUntil: d})}
              />
            </div>
          </div>
          
          {/* Kto kalibroval */}
          <div>
            <Label>Kalibračné laboratórium</Label>
            <Input 
              value={formData.calibrationLab}
              onChange={(e) => setFormData({...formData, calibrationLab: e.target.value})}
              placeholder="Napr. SMÚ Bratislava"
            />
          </div>
          
          {/* Číslo certifikátu */}
          <div>
            <Label>Číslo certifikátu</Label>
            <Input 
              value={formData.certificateNumber}
              onChange={(e) => setFormData({...formData, certificateNumber: e.target.value})}
            />
          </div>
          
          {/* Výsledok */}
          <div>
            <Label>Výsledok</Label>
            <Select 
              value={formData.result}
              onValueChange={(v) => setFormData({...formData, result: v})}
            >
              <SelectItem value="passed">Vyhovuje</SelectItem>
              <SelectItem value="passed_with_adjustment">Vyhovuje po úprave</SelectItem>
              <SelectItem value="failed">Nevyhovuje</SelectItem>
            </Select>
          </div>
          
          {/* Náklady */}
          <div>
            <Label>Náklady (€)</Label>
            <Input 
              type="number"
              value={formData.cost}
              onChange={(e) => setFormData({...formData, cost: e.target.value})}
            />
          </div>
          
          {/* Certifikát */}
          <div>
            <Label>Certifikát (PDF/obrázok)</Label>
            <FileUpload 
              accept=".pdf,image/*"
              value={certificateFile}
              onChange={setCertificateFile}
            />
          </div>
          
          {/* Poznámky */}
          <div>
            <Label>Poznámky</Label>
            <Textarea 
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Zrušiť</Button>
          <Button onClick={() => onSave(formData, certificateFile)}>Uložiť</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## 6. Notifikácie a Upozornenia

### 6.1 Background Job (Backend)

```python
# jobs/calibration_reminders.py

from celery import shared_task
from datetime import date, timedelta

@shared_task
def check_calibration_reminders():
    """Spúšťa sa denne - kontroluje expirácie kalibrácií"""
    
    today = date.today()
    
    # Načítaj nastavenia upozornení
    settings = get_active_reminder_settings()
    
    for setting in settings:
        # Nájdi zariadenia podľa scope
        equipment_list = get_equipment_for_scope(setting)
        
        for equipment in equipment_list:
            if not equipment.next_calibration_date:
                continue
            
            days_until = (equipment.next_calibration_date - today).days
            
            # Skontroluj či treba poslať upozornenie
            for reminder_days in setting.days_before:
                if days_until == reminder_days:
                    send_calibration_reminder(equipment, days_until, setting)
                    break
            
            # Expirované
            if days_until < 0:
                send_calibration_expired(equipment, abs(days_until), setting)


def send_calibration_reminder(equipment, days_until, setting):
    """Pošle upozornenie o blížiacej sa kalibrácii"""
    
    # Skontroluj či sme už neposlali
    reminder_type = f"{days_until}_days"
    if was_reminder_sent(equipment.id, reminder_type, today):
        return
    
    recipients = get_reminder_recipients(equipment, setting)
    
    for user in recipients:
        # Push notifikácia
        if setting.notify_push:
            send_push_notification(
                user_id=user.id,
                title="Blíži sa kalibrácia",
                body=f"{equipment.name} - kalibrácia končí za {days_until} dní",
                data={"type": "calibration", "equipment_id": str(equipment.id)}
            )
        
        # Email
        if setting.notify_email:
            send_email(
                to=user.email,
                template="calibration_reminder",
                context={
                    "equipment": equipment,
                    "days_until": days_until,
                    "calibration_date": equipment.next_calibration_date
                }
            )
        
        # In-app
        if setting.notify_in_app:
            create_notification(
                user_id=user.id,
                type="calibration_reminder",
                title="Blíži sa kalibrácia",
                message=f"{equipment.name} - kalibrácia končí za {days_until} dní",
                related_entity_type="equipment",
                related_entity_id=equipment.id
            )
        
        # Zaznamenaš že sme poslali
        log_reminder_sent(equipment.id, reminder_type, user.id)


def get_reminder_recipients(equipment, setting):
    """Určí komu poslať upozornenie"""
    recipients = []
    
    if setting.notify_holder and equipment.current_holder:
        recipients.append(equipment.current_holder)
    
    if setting.notify_manager:
        # Manager kategórie alebo oddelenia
        if equipment.category and equipment.category.manager:
            recipients.append(equipment.category.manager)
        if equipment.current_holder and equipment.current_holder.manager:
            recipients.append(equipment.current_holder.manager)
    
    if setting.notify_users:
        for user_id in setting.notify_users:
            user = get_user(user_id)
            if user:
                recipients.append(user)
    
    # Deduplikácia
    return list({u.id: u for u in recipients}.values())
```

### 6.2 Typy Notifikácií

```typescript
enum CalibrationNotificationType {
  CALIBRATION_DUE_30_DAYS = 'calibration_due_30',
  CALIBRATION_DUE_14_DAYS = 'calibration_due_14',
  CALIBRATION_DUE_7_DAYS = 'calibration_due_7',
  CALIBRATION_DUE_1_DAY = 'calibration_due_1',
  CALIBRATION_EXPIRED = 'calibration_expired',
  CALIBRATION_COMPLETED = 'calibration_completed',
}
```

---

## 7. Doplnenie do RBAC

```sql
-- Nové permissions pre onboarding a kalibrácie
INSERT INTO permissions (code, name, module) VALUES
-- Onboarding
('equipment.onboard', 'Onboarding náradia', 'equipment'),
('equipment.add_photos', 'Pridať fotky', 'equipment'),
('equipment.manage_accessories', 'Spravovať príslušenstvo', 'equipment'),

-- Manufacturers & Models
('manufacturers.view', 'Zobraziť výrobcov', 'manufacturers'),
('manufacturers.create', 'Vytvoriť výrobcu', 'manufacturers'),
('manufacturers.edit', 'Upraviť výrobcu', 'manufacturers'),
('models.create', 'Vytvoriť model', 'models'),

-- Calibrations
('calibrations.view', 'Zobraziť kalibrácie', 'calibrations'),
('calibrations.create', 'Pridať kalibráciu', 'calibrations'),
('calibrations.edit', 'Upraviť kalibráciu', 'calibrations'),
('calibrations.delete', 'Zmazať kalibráciu', 'calibrations'),
('calibrations.export', 'Exportovať kalibrácie', 'calibrations'),
('calibrations.settings', 'Nastavenia kalibrácií', 'calibrations');
```

| Permission | Worker | Leader | Manager | Admin |
|------------|:------:|:------:|:-------:|:-----:|
| equipment.onboard | - | - | ✅ | ✅ |
| equipment.add_photos | ✅ | ✅ | ✅ | ✅ |
| calibrations.view | ✅ | ✅ | ✅ | ✅ |
| calibrations.create | - | ✅ | ✅ | ✅ |
| calibrations.settings | - | - | ✅ | ✅ |

---

## 8. Sumár Nových Funkcionalít

### Onboarding:
- 6-krokový wizard (Scan → Foto → Info → Príslušenstvo → Kalibrácia → Súhrn)
- Multi-foto s typmi (hlavná, detail, štítok, poškodenie)
- Offline sync fotiek
- Katalóg výrobcov a modelov
- Príslušenstvo s vlastnými QR/tagmi
- Hierarchia: hlavné náradie → príslušenstvo

### Kalibrácie:
- Záznam kalibrácií s certifikátmi
- Automatické notifikácie (30/14/7/1 deň pred)
- Dashboard s prehľadom stavu
- Export kalibračného plánu
- Nastaviteľné upozornenia (globálne, per kategória, per zariadenie)
- História kalibrácií

### Nové tabuľky:
- `equipment_photos`
- `manufacturers`
- `equipment_models`
- `accessory_types`
- `calibrations`
- `calibration_reminder_settings`
- `calibration_reminders_sent`
