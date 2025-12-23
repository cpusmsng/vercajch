# Požičiavanie Náradia Medzi Používateľmi (P2P Transfer)

## 1. Prehľad Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SCENÁRE PRENOSU NÁRADIA                              │
└─────────────────────────────────────────────────────────────────────────┘

SCENÁR 1: Priamy prenos (Worker → Worker)
═══════════════════════════════════════════
Worker A má vŕtačku → Worker B ju potrebuje → A odovzdá B

  [Worker A]                              [Worker B]
      │                                        │
      │  ◄─── B: "Požiadavka o vŕtačku" ───   │
      │                                        │
      ├── A: Schváli/Odmietne                  │
      │                                        │
      │  ─── A: "Odovzdávam ti" ───►           │
      │                                        │
      │      ◄─── B: Potvrdí príjem ───        │
      │                                        │
      ▼                                        ▼
   [Nemá]                              [Má vŕtačku]


SCENÁR 2: Požiadavka o náradie (bez konkrétneho držiteľa)
═══════════════════════════════════════════════════════════
Worker B potrebuje vŕtačku → Pošle požiadavku → Ktokoľvek môže ponúknuť

  [Worker B]                    [Systém]                    [Worker A, C, D...]
      │                            │                              │
      │ ── "Potrebujem vŕtačku" ──►│                              │
      │                            │──► Notifikácia všetkým ──────►│
      │                            │    s dostupnou vŕtačkou       │
      │                            │                              │
      │   ◄── A: "Môžem ti dať" ──│◄────────────────────────────── │
      │                            │                              │
      │ ── B: Akceptuje ponuku A ─►│                              │
      │                            │                              │
      └────────── Štandardný transfer ────────────────────────────┘


SCENÁR 3: Transfer so schválením Leadera
═════════════════════════════════════════
(Pre cenné náradie alebo medzi tímami)

  [Worker A]        [Leader]         [Worker B]
      │                │                  │
      │ ◄── Požiadavka od B ──────────────│
      │                │                  │
      │ ── Schvaľujem ►│                  │
      │                │                  │
      │                │◄── Leader check ─│
      │                │                  │
      │                │── Schválené ────►│
      │                │                  │
      └────── Štandardný transfer ────────┘
```

---

## 2. Databázový Model

```sql
-- ============================================
-- TRANSFER REQUESTS (Požiadavky o náradie)
-- ============================================

CREATE TABLE transfer_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Typ požiadavky
  request_type VARCHAR(20) NOT NULL,  
  -- 'direct'     = Priama požiadavka na konkrétne náradie od konkrétneho usera
  -- 'broadcast'  = Všeobecná požiadavka (ktokoľvek môže ponúknuť)
  -- 'offer'      = Ponuka náradia (A ponúka B)
  
  -- Náradie
  equipment_id UUID REFERENCES equipment(id),
  category_id UUID REFERENCES categories(id),  -- Pre broadcast: "potrebujem niečo z kategórie X"
  
  -- Účastníci
  requester_id UUID REFERENCES users(id) NOT NULL,  -- Kto žiada
  holder_id UUID REFERENCES users(id),              -- Kto má náradie (pre direct)
  
  -- Lokácia stretnutia
  location_id UUID REFERENCES locations(id),
  location_note VARCHAR(200),  -- "Pri bielej dodávke", "Vstup do budovy A"
  
  -- Čas
  needed_from TIMESTAMP,       -- Odkedy potrebujem
  needed_until TIMESTAMP,      -- Dokedy potrebujem
  
  -- Správa
  message TEXT,                -- "Potrebujem na zajtra, mám to vrátiť do piatku"
  
  -- Stav
  status VARCHAR(20) DEFAULT 'pending',
  -- 'pending'           = Čaká na odpoveď
  -- 'accepted'          = Schválené, čaká na fyzický prenos
  -- 'rejected'          = Odmietnuté
  -- 'cancelled'         = Zrušené žiadateľom
  -- 'expired'           = Vypršala platnosť
  -- 'completed'         = Prenos dokončený
  -- 'requires_approval' = Čaká na schválenie leadera
  
  -- Schvaľovanie (ak potrebné)
  requires_leader_approval BOOLEAN DEFAULT false,
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP,
  rejection_reason TEXT,
  
  -- Timestamps
  responded_at TIMESTAMP,
  completed_at TIMESTAMP,
  expires_at TIMESTAMP,  -- Auto-expire ak bez odpovede
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

-- Pre broadcast požiadavky - kto ponúkol
CREATE TABLE transfer_offers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id UUID REFERENCES transfer_requests(id) ON DELETE CASCADE,
  
  offerer_id UUID REFERENCES users(id) NOT NULL,
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  
  message TEXT,
  
  status VARCHAR(20) DEFAULT 'pending',
  -- 'pending'  = Čaká na výber
  -- 'accepted' = Žiadateľ vybral túto ponuku
  -- 'rejected' = Žiadateľ vybral inú ponuku
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- História transferov (úspešne dokončené)
CREATE TABLE transfers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  equipment_id UUID REFERENCES equipment(id) NOT NULL,
  request_id UUID REFERENCES transfer_requests(id),  -- Ak vznikol z požiadavky
  
  -- Kto komu
  from_user_id UUID REFERENCES users(id) NOT NULL,
  to_user_id UUID REFERENCES users(id) NOT NULL,
  
  -- Kde a kedy
  location_id UUID REFERENCES locations(id),
  transfer_gps_lat DECIMAL(10, 8),
  transfer_gps_lng DECIMAL(11, 8),
  
  -- Potvrdenie oboch strán
  from_confirmed_at TIMESTAMP,  -- Odovzdávajúci potvrdil
  to_confirmed_at TIMESTAMP,    -- Prijímajúci potvrdil
  
  -- Stav pri prenose
  condition_at_transfer VARCHAR(20),
  photo_url VARCHAR(500),
  notes TEXT,
  
  -- Typ transferu
  transfer_type VARCHAR(20) DEFAULT 'peer',
  -- 'peer'      = Medzi workermi
  -- 'checkout'  = Zo skladu
  -- 'checkin'   = Na sklad
  -- 'handover'  = Odovzdanie služby
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Nastavenia pre kategórie - či vyžadujú schválenie
ALTER TABLE categories ADD COLUMN transfer_requires_approval BOOLEAN DEFAULT false;
ALTER TABLE categories ADD COLUMN max_transfer_days INTEGER;  -- Max doba požičania

-- Nastavenia pre equipment - individuálne override
ALTER TABLE equipment ADD COLUMN transfer_requires_approval BOOLEAN;
ALTER TABLE equipment ADD COLUMN is_transferable BOOLEAN DEFAULT true;  -- Niektoré sa nesmú požičiavať
```

---

## 3. API Endpointy

```python
# === TRANSFER REQUESTS ===

# Vytvoriť požiadavku o náradie
POST /api/transfers/requests
{
  "request_type": "direct",           # direct | broadcast
  "equipment_id": "uuid",             # Pre direct
  "category_id": "uuid",              # Pre broadcast (voliteľné)
  "holder_id": "uuid",                # Pre direct - od koho chcem
  "message": "Potrebujem na zajtra ráno",
  "needed_from": "2024-01-15T08:00:00",
  "needed_until": "2024-01-15T18:00:00",
  "location_id": "uuid",              # Kde sa stretneme
  "location_note": "Pri vstupe do areálu"
}

# Moje požiadavky (odoslané)
GET /api/transfers/requests/sent
Response: [{ request_id, equipment, holder, status, created_at, ... }]

# Požiadavky na mňa (prijaté)
GET /api/transfers/requests/received
Response: [{ request_id, equipment, requester, status, created_at, ... }]

# Broadcast požiadavky (kde môžem ponúknuť)
GET /api/transfers/requests/available
Response: [{ request_id, requester, category, message, needed_from, ... }]

# Odpovedať na požiadavku
POST /api/transfers/requests/{id}/respond
{
  "action": "accept",        # accept | reject
  "message": "OK, stretneme sa o 10:00",
  "rejection_reason": null   # Ak reject
}

# Zrušiť moju požiadavku
POST /api/transfers/requests/{id}/cancel

# === OFFERS (pre broadcast) ===

# Ponúknuť náradie na broadcast požiadavku
POST /api/transfers/requests/{id}/offer
{
  "equipment_id": "uuid",
  "message": "Mám voľnú, môžem ti dať"
}

# Akceptovať ponuku
POST /api/transfers/offers/{id}/accept

# === TRANSFERS ===

# Potvrdiť odovzdanie (odovzdávajúci)
POST /api/transfers/{id}/confirm-handover
{
  "condition": "good",
  "photo_url": "...",        # Voliteľné
  "notes": "Odovzdané OK",
  "gps_lat": 48.1234,
  "gps_lng": 17.1234
}

# Potvrdiť príjem (prijímajúci)
POST /api/transfers/{id}/confirm-receipt
{
  "condition": "good",
  "notes": "Prijaté OK"
}

# História transferov náradia
GET /api/equipment/{id}/transfers
Response: [{ from_user, to_user, date, location, ... }]

# Moja história transferov
GET /api/transfers/history
Response: [{ equipment, from/to, date, ... }]

# === LEADER APPROVAL ===

# Čakajúce schválenia (pre leadera)
GET /api/transfers/pending-approval

# Schváliť/Zamietnuť transfer
POST /api/transfers/requests/{id}/approve
{
  "approved": true,
  "notes": "OK, ale vráť do piatku"
}
```

---

## 4. Android UI - Obrazovky

### 4.1 Navigácia

```
📱 ANDROID APP - TRANSFER FEATURES
══════════════════════════════════════════════════════

🏠 HOME
├── [Badge] Čakajúce požiadavky (3)
├── [Badge] Aktívne transfery (1)
└── Quick Action: "Požiadať o náradie"

📋 MOJE NÁRADIE
└── Pri každom náradí:
    ├── [Button] "Ponúknuť"
    └── [Button] "Odovzdať kolegovi"

🔔 NOTIFIKÁCIE
├── "Peter ťa žiada o vŕtačku Makita"
├── "Jano prijal tvoju požiadavku"
└── "Transfer dokončený"

📤 TRANSFERY (nová sekcia)
├── Odoslané požiadavky
├── Prijaté požiadavky
├── Aktívne transfery
└── História
```

### 4.2 Flow: Požiadať o náradie

```kotlin
// screens/transfer/RequestEquipmentScreen.kt

@Composable
fun RequestEquipmentScreen(
    equipmentId: String? = null,  // Ak už vieme ktoré
    onComplete: () -> Unit
) {
    var requestType by remember { mutableStateOf(if (equipmentId != null) "direct" else "broadcast") }
    var selectedEquipment by remember { mutableStateOf<Equipment?>(null) }
    var selectedHolder by remember { mutableStateOf<User?>(null) }
    var message by remember { mutableStateOf("") }
    var neededFrom by remember { mutableStateOf<LocalDateTime?>(null) }
    var neededUntil by remember { mutableStateOf<LocalDateTime?>(null) }
    var meetingLocation by remember { mutableStateOf("") }
    
    Column(modifier = Modifier.padding(16.dp)) {
        
        // Typ požiadavky
        if (equipmentId == null) {
            SegmentedButton(
                options = listOf("Konkrétne náradie", "Hľadám náradie"),
                selected = requestType,
                onSelect = { requestType = it }
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        when (requestType) {
            "direct" -> {
                // Výber náradia (ak ešte nie je vybrané)
                if (selectedEquipment == null) {
                    EquipmentSearchField(
                        label = "Aké náradie potrebuješ?",
                        onSelect = { equipment ->
                            selectedEquipment = equipment
                            selectedHolder = equipment.currentHolder
                        }
                    )
                } else {
                    EquipmentCard(equipment = selectedEquipment!!)
                    
                    // Kto to má
                    if (selectedHolder != null) {
                        UserCard(
                            user = selectedHolder!!,
                            label = "Požiadaš od:"
                        )
                    }
                }
            }
            
            "broadcast" -> {
                // Kategória alebo popis
                CategorySelector(
                    label = "Akú kategóriu potrebuješ?",
                    onSelect = { /* ... */ }
                )
                
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it },
                    label = { Text("Popis (čo presne potrebuješ)") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Časový rozsah
        Row {
            DateTimePicker(
                label = "Od kedy",
                value = neededFrom,
                onValueChange = { neededFrom = it },
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.width(8.dp))
            DateTimePicker(
                label = "Do kedy",
                value = neededUntil,
                onValueChange = { neededUntil = it },
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Miesto stretnutia
        OutlinedTextField(
            value = meetingLocation,
            onValueChange = { meetingLocation = it },
            label = { Text("Kde sa stretneme?") },
            placeholder = { Text("Napr. 'Pri bielej dodávke'") },
            modifier = Modifier.fillMaxWidth()
        )
        
        // Správa
        OutlinedTextField(
            value = message,
            onValueChange = { message = it },
            label = { Text("Správa (voliteľné)") },
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Odoslať
        Button(
            onClick = { /* Submit request */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Odoslať požiadavku")
        }
    }
}
```

### 4.3 Flow: Prijatá požiadavka

```kotlin
// screens/transfer/ReceivedRequestScreen.kt

@Composable
fun ReceivedRequestScreen(
    request: TransferRequest,
    onRespond: (Boolean, String?) -> Unit
) {
    Column(modifier = Modifier.padding(16.dp)) {
        
        // Kto žiada
        UserCard(
            user = request.requester,
            label = "Žiada:",
            showPhone = true  // Možnosť zavolať
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // O čo žiada
        EquipmentCard(equipment = request.equipment)
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Detaily
        InfoRow(icon = Icons.Calendar, label = "Od", value = request.neededFrom.format())
        InfoRow(icon = Icons.Calendar, label = "Do", value = request.neededUntil.format())
        InfoRow(icon = Icons.MapPin, label = "Kde", value = request.locationNote ?: "Neurčené")
        
        if (request.message.isNotBlank()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "\"${request.message}\"",
                style = MaterialTheme.typography.bodyMedium,
                fontStyle = FontStyle.Italic
            )
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Akcie
        var rejectReason by remember { mutableStateOf("") }
        var showRejectDialog by remember { mutableStateOf(false) }
        
        Row(modifier = Modifier.fillMaxWidth()) {
            OutlinedButton(
                onClick = { showRejectDialog = true },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = MaterialTheme.colorScheme.error
                )
            ) {
                Icon(Icons.Close, null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Odmietnuť")
            }
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Button(
                onClick = { onRespond(true, null) },
                modifier = Modifier.weight(1f)
            ) {
                Icon(Icons.Check, null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Súhlasím")
            }
        }
        
        // Reject dialog
        if (showRejectDialog) {
            AlertDialog(
                onDismissRequest = { showRejectDialog = false },
                title = { Text("Dôvod odmietnutia") },
                text = {
                    OutlinedTextField(
                        value = rejectReason,
                        onValueChange = { rejectReason = it },
                        label = { Text("Prečo nemôžeš požičať?") },
                        modifier = Modifier.fillMaxWidth()
                    )
                },
                confirmButton = {
                    TextButton(onClick = { 
                        onRespond(false, rejectReason)
                        showRejectDialog = false
                    }) {
                        Text("Odmietnuť")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showRejectDialog = false }) {
                        Text("Zrušiť")
                    }
                }
            )
        }
    }
}
```

### 4.4 Flow: Potvrdenie transferu

```kotlin
// screens/transfer/ConfirmTransferScreen.kt

@Composable
fun ConfirmTransferScreen(
    transfer: Transfer,
    isGiver: Boolean,  // true = odovzdávam, false = prijímam
    onConfirm: (TransferConfirmation) -> Unit
) {
    var condition by remember { mutableStateOf("good") }
    var photoUri by remember { mutableStateOf<Uri?>(null) }
    var notes by remember { mutableStateOf("") }
    
    val cameraLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) { /* Handle photo */ }
    }
    
    Column(modifier = Modifier.padding(16.dp)) {
        
        Text(
            text = if (isGiver) "Odovzdanie náradia" else "Príjem náradia",
            style = MaterialTheme.typography.headlineSmall
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Náradie
        EquipmentCard(equipment = transfer.equipment)
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Druhá strana
        UserCard(
            user = if (isGiver) transfer.toUser else transfer.fromUser,
            label = if (isGiver) "Odovzdávaš:" else "Prijímaš od:"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Stav náradia
        Text("Stav náradia:", style = MaterialTheme.typography.labelLarge)
        Spacer(modifier = Modifier.height(8.dp))
        
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ConditionChip("V poriadku", "good", condition) { condition = it }
            ConditionChip("Opotrebované", "fair", condition) { condition = it }
            ConditionChip("Poškodené", "poor", condition) { condition = it }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Fotka
        if (photoUri != null) {
            AsyncImage(
                model = photoUri,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .clip(RoundedCornerShape(8.dp))
            )
        }
        
        OutlinedButton(
            onClick = { 
                val uri = createTempPhotoUri()
                photoUri = uri
                cameraLauncher.launch(uri)
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Camera, null)
            Spacer(modifier = Modifier.width(4.dp))
            Text(if (photoUri == null) "Odfotiť stav" else "Zmeniť fotku")
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Poznámka
        OutlinedTextField(
            value = notes,
            onValueChange = { notes = it },
            label = { Text("Poznámka (voliteľné)") },
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Potvrdiť
        Button(
            onClick = {
                onConfirm(TransferConfirmation(
                    condition = condition,
                    photoUri = photoUri,
                    notes = notes,
                    gpsLocation = getCurrentLocation()
                ))
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(if (isGiver) "Potvrdiť odovzdanie" else "Potvrdiť príjem")
        }
    }
}
```

---

## 5. Web UI - Manažér View

```typescript
// pages/TransfersPage.tsx

export function TransfersPage() {
  const [activeTab, setActiveTab] = useState<'pending' | 'active' | 'history'>('pending');
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Transfery náradia</h1>
      
      {/* Štatistiky */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard title="Čakajúce požiadavky" value={stats.pending} />
        <StatCard title="Aktívne transfery" value={stats.active} />
        <StatCard title="Dnes dokončené" value={stats.todayCompleted} />
        <StatCard title="Priemerný čas" value={`${stats.avgTime}h`} />
      </div>
      
      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="pending">
            Čakajúce
            {stats.pending > 0 && <Badge className="ml-2">{stats.pending}</Badge>}
          </TabsTrigger>
          <TabsTrigger value="active">Aktívne</TabsTrigger>
          <TabsTrigger value="history">História</TabsTrigger>
          <TabsTrigger value="approval">
            Schválenia
            {stats.pendingApproval > 0 && <Badge className="ml-2">{stats.pendingApproval}</Badge>}
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="pending">
          <PendingTransfersTable />
        </TabsContent>
        
        <TabsContent value="active">
          <ActiveTransfersTable />
        </TabsContent>
        
        <TabsContent value="history">
          <TransferHistoryTable />
        </TabsContent>
        
        <TabsContent value="approval">
          <PendingApprovalsTable />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Tabuľka čakajúcich schválení (pre Leadera/Managera)
function PendingApprovalsTable() {
  const { data: requests } = useQuery(['transfers', 'pending-approval'], fetchPendingApprovals);
  
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Náradie</TableHead>
          <TableHead>Od</TableHead>
          <TableHead>Komu</TableHead>
          <TableHead>Dôvod</TableHead>
          <TableHead>Obdobie</TableHead>
          <TableHead>Akcie</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {requests?.map((req) => (
          <TableRow key={req.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                <img src={req.equipment.photoUrl} className="w-10 h-10 rounded" />
                <div>
                  <div className="font-medium">{req.equipment.name}</div>
                  <div className="text-sm text-gray-500">{req.equipment.internalCode}</div>
                </div>
              </div>
            </TableCell>
            <TableCell>{req.holder.fullName}</TableCell>
            <TableCell>{req.requester.fullName}</TableCell>
            <TableCell>{req.message}</TableCell>
            <TableCell>
              {formatDate(req.neededFrom)} - {formatDate(req.neededUntil)}
            </TableCell>
            <TableCell>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => handleReject(req.id)}>
                  Zamietnuť
                </Button>
                <Button size="sm" onClick={() => handleApprove(req.id)}>
                  Schváliť
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

---

## 6. Notifikácie

```typescript
// Typy notifikácií pre transfery

enum TransferNotificationType {
  // Pre držiteľa
  TRANSFER_REQUESTED = 'transfer_requested',      // "Peter ťa žiada o vŕtačku"
  
  // Pre žiadateľa
  TRANSFER_ACCEPTED = 'transfer_accepted',        // "Jano súhlasil s požičaním"
  TRANSFER_REJECTED = 'transfer_rejected',        // "Jano odmietol požiadavku"
  OFFER_RECEIVED = 'offer_received',              // "Jano ti ponúka vŕtačku" (broadcast)
  
  // Pre oboch
  TRANSFER_REMINDER = 'transfer_reminder',        // "Nezabudni odovzdať/vyzdvihnúť"
  TRANSFER_CONFIRMED = 'transfer_confirmed',      // "Transfer dokončený"
  
  // Pre leadera
  TRANSFER_APPROVAL_NEEDED = 'transfer_approval', // "Schváľ transfer medzi A a B"
  
  // Systémové
  TRANSFER_EXPIRED = 'transfer_expired',          // "Požiadavka vypršala"
  TRANSFER_OVERDUE = 'transfer_overdue',          // "Náradie malo byť vrátené"
}
```

---

## 7. Business Rules

```python
# services/transfer_service.py

class TransferService:
    
    def can_request_transfer(self, equipment: Equipment, requester: User) -> tuple[bool, str]:
        """Skontroluje či môže používateľ požiadať o transfer"""
        
        # Náradie nie je prenositeľné
        if not equipment.is_transferable:
            return False, "Toto náradie nie je možné požičiavať"
        
        # Náradie nie je vydané nikomu
        if equipment.status != 'checked_out':
            return False, "Náradie nie je aktuálne vydané"
        
        # Náradie už má žiadateľ
        if equipment.current_holder_id == requester.id:
            return False, "Toto náradie už máš"
        
        # Náradie je v údržbe
        if equipment.status == 'maintenance':
            return False, "Náradie je v údržbe"
        
        # Už existuje aktívna požiadavka
        existing = self.get_pending_request(equipment.id, requester.id)
        if existing:
            return False, "Už máš aktívnu požiadavku na toto náradie"
        
        return True, None
    
    def requires_approval(self, equipment: Equipment, from_user: User, to_user: User) -> bool:
        """Určí či transfer vyžaduje schválenie leadera"""
        
        # Explicitné nastavenie na náradí
        if equipment.transfer_requires_approval is not None:
            return equipment.transfer_requires_approval
        
        # Nastavenie kategórie
        if equipment.category and equipment.category.transfer_requires_approval:
            return True
        
        # Transfer medzi rôznymi tímami
        if from_user.manager_id != to_user.manager_id:
            return True
        
        # Vysoká hodnota
        if equipment.current_value and equipment.current_value > 500:
            return True
        
        return False
    
    def get_potential_holders(self, category_id: UUID, requester: User) -> list[Equipment]:
        """Pre broadcast - nájdi všetko dostupné náradie v kategórii"""
        return self.db.query(Equipment).filter(
            Equipment.category_id == category_id,
            Equipment.status == 'checked_out',
            Equipment.current_holder_id != requester.id,
            Equipment.is_transferable == True
        ).all()
    
    def complete_transfer(self, transfer: Transfer):
        """Dokončí transfer a aktualizuje stav náradia"""
        
        # Obe strany potvrdili
        if not transfer.from_confirmed_at or not transfer.to_confirmed_at:
            raise ValueError("Obe strany musia potvrdiť transfer")
        
        equipment = transfer.equipment
        
        # Aktualizuj držiteľa
        equipment.current_holder_id = transfer.to_user_id
        equipment.updated_at = datetime.utcnow()
        
        # Vytvor checkout záznam
        checkout = Checkout(
            equipment_id=equipment.id,
            user_id=transfer.to_user_id,
            checkout_at=transfer.to_confirmed_at,
            checked_out_by=transfer.from_user_id,
            checkout_condition=transfer.condition_at_transfer,
            checkout_notes=f"Transfer od {transfer.from_user.full_name}"
        )
        
        # Uzavri predchádzajúci checkout
        previous_checkout = self.get_active_checkout(equipment.id)
        if previous_checkout:
            previous_checkout.actual_return_at = transfer.from_confirmed_at
            previous_checkout.checked_in_by = transfer.to_user_id
            previous_checkout.return_notes = f"Transfer pre {transfer.to_user.full_name}"
        
        # Audit log
        self.audit_log.log(
            action='equipment.transferred',
            entity_type='equipment',
            entity_id=equipment.id,
            old_values={'holder_id': str(transfer.from_user_id)},
            new_values={'holder_id': str(transfer.to_user_id)}
        )
        
        self.db.commit()
```

---

## 8. Doplnenie do RBAC

```sql
-- Nové permissions pre transfery
INSERT INTO permissions (code, name, module) VALUES
('transfers.request', 'Požiadať o transfer', 'transfers'),
('transfers.respond', 'Odpovedať na transfer', 'transfers'),
('transfers.approve', 'Schvaľovať transfery', 'transfers'),
('transfers.view_team', 'Vidieť transfery tímu', 'transfers'),
('transfers.view_all', 'Vidieť všetky transfery', 'transfers'),
('transfers.cancel_any', 'Zrušiť akýkoľvek transfer', 'transfers');

-- Priradenie k rolám
-- Worker: request, respond
-- Leader: + approve (svoj tím), view_team
-- Manager: + view_all, cancel_any
-- Admin: všetko
```

---

## 9. Sumár Zmien

### Nové tabuľky:
- `transfer_requests` - Požiadavky o náradie
- `transfer_offers` - Ponuky na broadcast požiadavky  
- `transfers` - História transferov

### Nové API endpointy:
- `POST /api/transfers/requests` - Vytvoriť požiadavku
- `POST /api/transfers/requests/{id}/respond` - Prijať/Odmietnuť
- `POST /api/transfers/requests/{id}/offer` - Ponúknuť náradie
- `POST /api/transfers/{id}/confirm-handover` - Potvrdiť odovzdanie
- `POST /api/transfers/{id}/confirm-receipt` - Potvrdiť príjem
- `POST /api/transfers/requests/{id}/approve` - Leader schválenie

### Nové Android obrazovky:
- Požiadať o náradie
- Prijaté požiadavky
- Potvrdenie transferu
- História transferov

### Nové Web sekcie:
- Transfers dashboard
- Pending approvals
- Transfer history
