from enum import Enum
from typing import List, Set


class Permission(str, Enum):
    # Equipment
    EQUIPMENT_VIEW = "equipment.view"
    EQUIPMENT_CREATE = "equipment.create"
    EQUIPMENT_EDIT = "equipment.edit"
    EQUIPMENT_DELETE = "equipment.delete"
    EQUIPMENT_ONBOARD = "equipment.onboard"
    EQUIPMENT_ADD_PHOTOS = "equipment.add_photos"
    EQUIPMENT_MANAGE_ACCESSORIES = "equipment.manage_accessories"

    # Checkouts
    CHECKOUT_SELF = "checkouts.self"
    CHECKOUT_TEAM = "checkouts.team"
    CHECKIN = "checkin"

    # Transfers
    TRANSFERS_REQUEST = "transfers.request"
    TRANSFERS_RESPOND = "transfers.respond"
    TRANSFERS_APPROVE = "transfers.approve"
    TRANSFERS_VIEW_TEAM = "transfers.view_team"
    TRANSFERS_VIEW_ALL = "transfers.view_all"
    TRANSFERS_CANCEL_ANY = "transfers.cancel_any"

    # Calibrations
    CALIBRATIONS_VIEW = "calibrations.view"
    CALIBRATIONS_CREATE = "calibrations.create"
    CALIBRATIONS_EDIT = "calibrations.edit"
    CALIBRATIONS_DELETE = "calibrations.delete"
    CALIBRATIONS_EXPORT = "calibrations.export"
    CALIBRATIONS_SETTINGS = "calibrations.settings"

    # Manufacturers & Models
    MANUFACTURERS_VIEW = "manufacturers.view"
    MANUFACTURERS_CREATE = "manufacturers.create"
    MANUFACTURERS_EDIT = "manufacturers.edit"
    MODELS_CREATE = "models.create"

    # Users
    USERS_VIEW = "users.view"
    USERS_VIEW_TEAM = "users.view_team"
    USERS_CREATE = "users.create"
    USERS_EDIT = "users.edit"
    USERS_DELETE = "users.delete"
    USERS_MANAGE_ROLES = "users.manage_roles"

    # Locations
    LOCATIONS_VIEW = "locations.view"
    LOCATIONS_CREATE = "locations.create"
    LOCATIONS_EDIT = "locations.edit"
    LOCATIONS_DELETE = "locations.delete"

    # Categories
    CATEGORIES_VIEW = "categories.view"
    CATEGORIES_CREATE = "categories.create"
    CATEGORIES_EDIT = "categories.edit"
    CATEGORIES_DELETE = "categories.delete"

    # Reports
    REPORTS_OWN = "reports.own"
    REPORTS_TEAM = "reports.team"
    REPORTS_ALL = "reports.all"

    # Maintenance
    MAINTENANCE_VIEW = "maintenance.view"
    MAINTENANCE_CREATE = "maintenance.create"
    MAINTENANCE_EDIT = "maintenance.edit"
    MAINTENANCE_COMPLETE = "maintenance.complete"

    # Tags & Printing
    TAGS_VIEW = "tags.view"
    TAGS_CREATE = "tags.create"
    TAGS_MANAGE = "tags.manage"
    PRINT_LABELS = "print.labels"

    # Admin
    AUDIT_LOG = "audit.log"
    SETTINGS_VIEW = "settings.view"
    SETTINGS_EDIT = "settings.edit"
    SYSTEM_SETTINGS = "system.settings"


class Role(str, Enum):
    WORKER = "worker"
    LEADER = "leader"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


# Role permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.WORKER: {
        Permission.EQUIPMENT_VIEW,
        Permission.EQUIPMENT_ADD_PHOTOS,
        Permission.CHECKOUT_SELF,
        Permission.CHECKIN,
        Permission.TRANSFERS_REQUEST,
        Permission.TRANSFERS_RESPOND,
        Permission.CALIBRATIONS_VIEW,
        Permission.MANUFACTURERS_VIEW,
        Permission.USERS_VIEW,
        Permission.LOCATIONS_VIEW,
        Permission.CATEGORIES_VIEW,
        Permission.REPORTS_OWN,
        Permission.MAINTENANCE_VIEW,
        Permission.TAGS_VIEW,
    },
    Role.LEADER: {
        # Worker permissions
        Permission.EQUIPMENT_VIEW,
        Permission.EQUIPMENT_ADD_PHOTOS,
        Permission.CHECKOUT_SELF,
        Permission.CHECKIN,
        Permission.TRANSFERS_REQUEST,
        Permission.TRANSFERS_RESPOND,
        Permission.CALIBRATIONS_VIEW,
        Permission.MANUFACTURERS_VIEW,
        Permission.USERS_VIEW,
        Permission.LOCATIONS_VIEW,
        Permission.CATEGORIES_VIEW,
        Permission.REPORTS_OWN,
        Permission.MAINTENANCE_VIEW,
        Permission.TAGS_VIEW,
        # Additional
        Permission.CHECKOUT_TEAM,
        Permission.TRANSFERS_APPROVE,
        Permission.TRANSFERS_VIEW_TEAM,
        Permission.CALIBRATIONS_CREATE,
        Permission.USERS_VIEW_TEAM,
        Permission.REPORTS_TEAM,
        Permission.MAINTENANCE_CREATE,
    },
    Role.MANAGER: {
        # Leader permissions
        Permission.EQUIPMENT_VIEW,
        Permission.EQUIPMENT_ADD_PHOTOS,
        Permission.CHECKOUT_SELF,
        Permission.CHECKIN,
        Permission.TRANSFERS_REQUEST,
        Permission.TRANSFERS_RESPOND,
        Permission.CALIBRATIONS_VIEW,
        Permission.MANUFACTURERS_VIEW,
        Permission.USERS_VIEW,
        Permission.LOCATIONS_VIEW,
        Permission.CATEGORIES_VIEW,
        Permission.REPORTS_OWN,
        Permission.MAINTENANCE_VIEW,
        Permission.TAGS_VIEW,
        Permission.CHECKOUT_TEAM,
        Permission.TRANSFERS_APPROVE,
        Permission.TRANSFERS_VIEW_TEAM,
        Permission.CALIBRATIONS_CREATE,
        Permission.USERS_VIEW_TEAM,
        Permission.REPORTS_TEAM,
        Permission.MAINTENANCE_CREATE,
        # Additional
        Permission.EQUIPMENT_CREATE,
        Permission.EQUIPMENT_EDIT,
        Permission.EQUIPMENT_ONBOARD,
        Permission.EQUIPMENT_MANAGE_ACCESSORIES,
        Permission.TRANSFERS_VIEW_ALL,
        Permission.CALIBRATIONS_EDIT,
        Permission.CALIBRATIONS_EXPORT,
        Permission.CALIBRATIONS_SETTINGS,
        Permission.MANUFACTURERS_CREATE,
        Permission.MANUFACTURERS_EDIT,
        Permission.MODELS_CREATE,
        Permission.USERS_CREATE,
        Permission.USERS_EDIT,
        Permission.LOCATIONS_CREATE,
        Permission.LOCATIONS_EDIT,
        Permission.CATEGORIES_CREATE,
        Permission.CATEGORIES_EDIT,
        Permission.REPORTS_ALL,
        Permission.MAINTENANCE_EDIT,
        Permission.MAINTENANCE_COMPLETE,
        Permission.TAGS_CREATE,
        Permission.TAGS_MANAGE,
        Permission.PRINT_LABELS,
        Permission.SETTINGS_VIEW,
    },
    Role.ADMIN: {
        # All Manager permissions plus
        Permission.EQUIPMENT_DELETE,
        Permission.TRANSFERS_CANCEL_ANY,
        Permission.CALIBRATIONS_DELETE,
        Permission.USERS_DELETE,
        Permission.LOCATIONS_DELETE,
        Permission.CATEGORIES_DELETE,
        Permission.USERS_MANAGE_ROLES,
        Permission.AUDIT_LOG,
        Permission.SETTINGS_EDIT,
    },
    Role.SUPERADMIN: set(Permission),  # All permissions
}


def get_role_permissions(role: Role) -> Set[Permission]:
    """Get all permissions for a role, including inherited ones"""
    permissions = ROLE_PERMISSIONS.get(role, set())

    # Add inherited permissions
    if role == Role.ADMIN:
        permissions = permissions.union(ROLE_PERMISSIONS[Role.MANAGER])
    elif role == Role.SUPERADMIN:
        permissions = set(Permission)

    return permissions


def has_permission(user_role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in get_role_permissions(user_role)
