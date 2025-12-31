"""
Database seed script for initial data.
Run with: python -m app.db.seed
"""
import asyncio
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy import select
from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User, Role, Department
from app.models.equipment import Category, Location, Manufacturer, EquipmentModel, Equipment, EquipmentTag


async def seed_roles(session):
    """Create default roles"""
    roles = [
        {"code": "worker", "name": "Pracovnik", "description": "Zakladny uzivatel", "is_system_role": True},
        {"code": "leader", "name": "Veduci", "description": "Veduci timu", "is_system_role": True},
        {"code": "manager", "name": "Manager", "description": "Manazer oddelenia", "is_system_role": True},
        {"code": "admin", "name": "Administrator", "description": "Systemovy administrator", "is_system_role": True},
        {"code": "superadmin", "name": "Super Administrator", "description": "Hlavny administrator", "is_system_role": True},
    ]

    created_roles = {}
    for role_data in roles:
        # Check if exists
        result = await session.execute(
            select(Role).where(Role.code == role_data["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_roles[role_data["code"]] = existing
            print(f"Role '{role_data['code']}' already exists")
        else:
            role = Role(**role_data)
            session.add(role)
            created_roles[role_data["code"]] = role
            print(f"Created role: {role_data['name']}")

    await session.commit()
    return created_roles


async def seed_departments(session):
    """Create default departments"""
    departments = [
        {"name": "IT oddelenie", "code": "IT"},
        {"name": "Technicke oddelenie", "code": "TECH"},
        {"name": "Administrativne oddelenie", "code": "ADMIN"},
        {"name": "Sklad", "code": "SKLAD"},
        {"name": "Vedenie", "code": "MGT"},
    ]

    created_departments = {}
    for dept_data in departments:
        result = await session.execute(
            select(Department).where(Department.code == dept_data["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_departments[dept_data["code"]] = existing
            print(f"Department '{dept_data['code']}' already exists")
        else:
            dept = Department(**dept_data)
            session.add(dept)
            created_departments[dept_data["code"]] = dept
            print(f"Created department: {dept_data['name']}")

    await session.commit()
    return created_departments


async def seed_users(session, roles, departments):
    """Create default users"""
    users = [
        {
            "email": "admin@spp-d.sk",
            "full_name": "System Administrator",
            "role_code": "superadmin",
            "dept_code": "IT",
            "password": "admin123",
            "can_access_web": True,
            "can_access_mobile": True,
        },
        {
            "email": "manager@spp-d.sk",
            "full_name": "Jan Manager",
            "role_code": "manager",
            "dept_code": "TECH",
            "password": "manager123",
            "can_access_web": True,
            "can_access_mobile": True,
        },
        {
            "email": "leader@spp-d.sk",
            "full_name": "Peter Veduci",
            "role_code": "leader",
            "dept_code": "TECH",
            "password": "leader123",
            "can_access_web": True,
            "can_access_mobile": True,
        },
        {
            "email": "worker1@spp-d.sk",
            "full_name": "Milan Pracovnik",
            "role_code": "worker",
            "dept_code": "TECH",
            "password": "worker123",
            "can_access_web": False,
            "can_access_mobile": True,
        },
        {
            "email": "worker2@spp-d.sk",
            "full_name": "Jozef Technik",
            "role_code": "worker",
            "dept_code": "TECH",
            "password": "worker123",
            "can_access_web": False,
            "can_access_mobile": True,
        },
    ]

    created_users = {}
    for user_data in users:
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_users[user_data["email"]] = existing
            print(f"User '{user_data['email']}' already exists")
        else:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=get_password_hash(user_data["password"]),
                role_id=roles[user_data["role_code"]].id,
                department_id=departments[user_data["dept_code"]].id,
                can_access_web=user_data["can_access_web"],
                can_access_mobile=user_data["can_access_mobile"],
                is_active=True,
            )
            session.add(user)
            created_users[user_data["email"]] = user
            print(f"Created user: {user_data['full_name']} ({user_data['email']})")

    await session.commit()
    return created_users


async def seed_categories(session):
    """Create equipment categories"""
    categories = [
        {"name": "Rucne naradie", "code": "HAND", "icon": "wrench", "color": "#2196F3"},
        {"name": "Elektrocentraly", "code": "GEN", "icon": "bolt", "color": "#FF9800", "requires_certification": True},
        {"name": "Meracie pristroje", "code": "MEAS", "icon": "straighten", "color": "#4CAF50", "requires_certification": True},
        {"name": "Zvaracie pristroje", "code": "WELD", "icon": "local_fire_department", "color": "#F44336", "requires_certification": True},
        {"name": "Elektricke naradie", "code": "ELEC", "icon": "power", "color": "#9C27B0"},
        {"name": "Bezpecnostne vybavenie", "code": "SAFE", "icon": "security", "color": "#E91E63"},
        {"name": "Strojne vybavenie", "code": "MACH", "icon": "settings", "color": "#607D8B"},
        {"name": "IT vybavenie", "code": "IT", "icon": "computer", "color": "#00BCD4"},
        {"name": "Rebrike a lesa", "code": "LADD", "icon": "stairs", "color": "#795548"},
        {"name": "Ostatne", "code": "OTHER", "icon": "category", "color": "#9E9E9E"},
    ]

    created_categories = {}
    for cat_data in categories:
        result = await session.execute(
            select(Category).where(Category.code == cat_data["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_categories[cat_data["code"]] = existing
            print(f"Category '{cat_data['code']}' already exists")
        else:
            cat = Category(**cat_data)
            session.add(cat)
            created_categories[cat_data["code"]] = cat
            print(f"Created category: {cat_data['name']}")

    await session.commit()
    return created_categories


async def seed_locations(session):
    """Create default locations"""
    locations = [
        {"name": "Hlavny sklad", "code": "MAIN", "type": "warehouse"},
        {"name": "Pobocka Bratislava", "code": "BA", "type": "warehouse"},
        {"name": "Pobocka Kosice", "code": "KE", "type": "warehouse"},
        {"name": "Projekt A", "code": "PROJ-A", "type": "project"},
        {"name": "Projekt B", "code": "PROJ-B", "type": "project"},
        {"name": "Sluzobne vozidlo 1", "code": "VEH-1", "type": "vehicle"},
        {"name": "Sluzobne vozidlo 2", "code": "VEH-2", "type": "vehicle"},
    ]

    created_locations = {}
    for loc_data in locations:
        result = await session.execute(
            select(Location).where(Location.code == loc_data["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_locations[loc_data["code"]] = existing
            print(f"Location '{loc_data['code']}' already exists")
        else:
            loc = Location(**loc_data)
            session.add(loc)
            created_locations[loc_data["code"]] = loc
            print(f"Created location: {loc_data['name']}")

    await session.commit()
    return created_locations


async def seed_manufacturers(session):
    """Create some manufacturers"""
    manufacturers = [
        {"name": "Bosch", "website": "https://www.bosch.sk"},
        {"name": "Makita", "website": "https://www.makita.sk"},
        {"name": "DeWalt", "website": "https://www.dewalt.sk"},
        {"name": "Milwaukee", "website": "https://www.milwaukeetool.eu"},
        {"name": "Hilti", "website": "https://www.hilti.sk"},
        {"name": "Fluke", "website": "https://www.fluke.com"},
        {"name": "Testo", "website": "https://www.testo.com"},
    ]

    created_manufacturers = {}
    for mfr_data in manufacturers:
        result = await session.execute(
            select(Manufacturer).where(Manufacturer.name == mfr_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            created_manufacturers[mfr_data["name"]] = existing
            print(f"Manufacturer '{mfr_data['name']}' already exists")
        else:
            mfr = Manufacturer(**mfr_data)
            session.add(mfr)
            created_manufacturers[mfr_data["name"]] = mfr
            print(f"Created manufacturer: {mfr_data['name']}")

    await session.commit()
    return created_manufacturers


async def seed_equipment(session, categories, locations, users):
    """Create sample equipment"""
    equipment_list = [
        {
            "name": "Akumulatorovy vrtak Bosch GSR 18V",
            "internal_code": "EQ-001",
            "serial_number": "BSH-2024-001",
            "category_code": "ELEC",
            "location_code": "MAIN",
            "holder_email": "worker1@spp-d.sk",
            "status": "available",
            "condition": "good",
            "purchase_price": Decimal("299.90"),
        },
        {
            "name": "Multimeter Fluke 117",
            "internal_code": "EQ-002",
            "serial_number": "FLK-2024-002",
            "category_code": "MEAS",
            "location_code": "MAIN",
            "holder_email": None,
            "status": "available",
            "condition": "good",
            "requires_calibration": True,
            "purchase_price": Decimal("450.00"),
        },
        {
            "name": "Uhlovka Makita GA5030",
            "internal_code": "EQ-003",
            "serial_number": "MAK-2024-003",
            "category_code": "ELEC",
            "location_code": "BA",
            "holder_email": "worker2@spp-d.sk",
            "status": "checked_out",
            "condition": "good",
            "purchase_price": Decimal("89.90"),
        },
        {
            "name": "Zvaraci invertor ESAB",
            "internal_code": "EQ-004",
            "serial_number": "ESB-2024-004",
            "category_code": "WELD",
            "location_code": "MAIN",
            "holder_email": None,
            "status": "available",
            "condition": "good",
            "requires_calibration": True,
            "purchase_price": Decimal("1299.00"),
        },
        {
            "name": "Elektrocentrala Honda EU22i",
            "internal_code": "EQ-005",
            "serial_number": "HND-2024-005",
            "category_code": "GEN",
            "location_code": "PROJ-A",
            "holder_email": "leader@spp-d.sk",
            "status": "checked_out",
            "condition": "good",
            "purchase_price": Decimal("2499.00"),
        },
        {
            "name": "Kladivo Hilti TE 30-A36",
            "internal_code": "EQ-006",
            "serial_number": "HLT-2024-006",
            "category_code": "ELEC",
            "location_code": "MAIN",
            "holder_email": None,
            "status": "available",
            "condition": "fair",
            "purchase_price": Decimal("1199.00"),
        },
        {
            "name": "Laserovy diaľkomer Bosch GLM 50",
            "internal_code": "EQ-007",
            "serial_number": "BSH-2024-007",
            "category_code": "MEAS",
            "location_code": "MAIN",
            "holder_email": None,
            "status": "available",
            "condition": "good",
            "purchase_price": Decimal("159.90"),
        },
        {
            "name": "Notebook Dell Latitude 5540",
            "internal_code": "EQ-008",
            "serial_number": "DELL-2024-008",
            "category_code": "IT",
            "location_code": "MAIN",
            "holder_email": "manager@spp-d.sk",
            "status": "checked_out",
            "condition": "good",
            "purchase_price": Decimal("1299.00"),
        },
        {
            "name": "Hlinikovy rebrik 3x12",
            "internal_code": "EQ-009",
            "serial_number": "LAD-2024-009",
            "category_code": "LADD",
            "location_code": "MAIN",
            "holder_email": None,
            "status": "available",
            "condition": "good",
            "purchase_price": Decimal("249.90"),
        },
        {
            "name": "Prilba ochrana zraku 3M",
            "internal_code": "EQ-010",
            "serial_number": "3M-2024-010",
            "category_code": "SAFE",
            "location_code": "SKLAD",
            "holder_email": None,
            "status": "available",
            "condition": "new",
            "purchase_price": Decimal("79.90"),
        },
    ]

    for eq_data in equipment_list:
        result = await session.execute(
            select(Equipment).where(Equipment.internal_code == eq_data["internal_code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Equipment '{eq_data['internal_code']}' already exists")
            continue

        category = categories.get(eq_data.pop("category_code"))
        location = locations.get(eq_data.pop("location_code"))
        holder_email = eq_data.pop("holder_email", None)
        holder = users.get(holder_email) if holder_email else None

        eq = Equipment(
            **eq_data,
            category_id=category.id if category else None,
            current_location_id=location.id if location else None,
            current_holder_id=holder.id if holder else None,
            is_main_item=True,
            purchase_date=date.today() - timedelta(days=30),
            current_value=eq_data.get("purchase_price", Decimal("0")) * Decimal("0.9"),
        )
        session.add(eq)
        print(f"Created equipment: {eq_data['name']}")

    await session.commit()


async def main():
    """Run all seed functions"""
    print("Starting database seed...")

    async with async_session_maker() as session:
        try:
            roles = await seed_roles(session)
            departments = await seed_departments(session)
            users = await seed_users(session, roles, departments)
            categories = await seed_categories(session)
            locations = await seed_locations(session)
            manufacturers = await seed_manufacturers(session)
            await seed_equipment(session, categories, locations, users)

            print("\nDatabase seed completed successfully!")
            print(f"Created {len(roles)} roles")
            print(f"Created {len(departments)} departments")
            print(f"Created {len(users)} users")
            print(f"Created {len(categories)} categories")
            print(f"Created {len(locations)} locations")
            print(f"Created {len(manufacturers)} manufacturers")

        except Exception as e:
            print(f"Error during seed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
