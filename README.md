# Vercajch - Equipment Tracking System

Komplexný systém pre sledovanie a správu náradia a vybavenia pre SPP - distribúcia.

## Prehľad

Vercajch je full-stack riešenie pozostávajúce z:

- **Backend API** - FastAPI + PostgreSQL
- **Web Aplikácia** - React + TypeScript + Vite
- **Android Aplikácia** - Kotlin + Jetpack Compose
- **Docker Compose** - Pre jednoduché nasadenie

## Funkcie

### Správa náradia
- QR kód skenner pre identifikáciu
- Onboarding wizard pre nové náradie (6 krokov)
- Fotodokumentácia
- Sledovanie stavu a polohy

### Kalibrácie
- Sledovanie kalibračných intervalov
- Automatické pripomienky
- História kalibrácií

### P2P Transfery
- Priame požiadavky na konkrétne náradie
- Broadcast požiadavky podľa kategórie
- Schvaľovací workflow

### Používatelia
- Role-Based Access Control (RBAC)
- 5 úrovní: worker, leader, manager, admin, superadmin

## Rýchly štart

### Predpoklady
- Docker a Docker Compose
- Node.js 20+ (pre vývoj)
- Python 3.11+ (pre vývoj)
- Android Studio (pre Android vývoj)

### Spustenie s Docker

```bash
# Klonovanie repozitára
git clone <repository-url>
cd vercajch

# Vytvorenie .env súboru
cp .env.example .env
# Upravte .env podľa potreby

# Spustenie všetkých služieb
docker-compose up -d

# Aplikácia bude dostupná na:
# - API: http://localhost:8000
# - Web: http://localhost:80
```

### Vývoj

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Web
cd web
npm install
npm run dev

# Android
# Otvorte android/ v Android Studio
```

## Štruktúra projektu

```
vercajch/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Config, security, database
│   │   ├── models/    # SQLAlchemy models
│   │   └── schemas/   # Pydantic schemas
│   └── Dockerfile
├── web/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   └── Dockerfile
├── android/           # Android app
│   └── app/
│       └── src/
│           └── main/
│               └── java/sk/sppd/vercajch/
├── docker-compose.yml
└── README.md
```

## API Dokumentácia

Po spustení backendu je dokumentácia dostupná na:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Licencia

Proprietárny softvér - SPP - distribúcia, a.s.
