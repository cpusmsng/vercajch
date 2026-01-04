package sk.sppd.vercajch.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val email: String,
    @SerialName("full_name") val fullName: String?,
    @SerialName("employee_number") val employeeNumber: String? = null,
    val phone: String? = null,
    @SerialName("is_active") val isActive: Boolean = true,
    val role: Role? = null,
    val department: Department? = null
)

@Serializable
data class Role(
    val id: String,
    val name: String,
    val code: String? = null,
    val description: String? = null
)

@Serializable
data class Department(
    val id: String,
    val name: String,
    val code: String? = null
)

@Serializable
data class Equipment(
    val id: String,
    val name: String,
    @SerialName("internal_code") val internalCode: String,
    @SerialName("serial_number") val serialNumber: String?,
    val manufacturer: String?,
    @SerialName("model_name") val modelName: String?,
    val description: String?,
    val status: String,
    val condition: String,
    @SerialName("photo_url") val photoUrl: String?,
    @SerialName("requires_calibration") val requiresCalibration: Boolean,
    @SerialName("calibration_interval_days") val calibrationIntervalDays: Int?,
    @SerialName("last_calibration_date") val lastCalibrationDate: String?,
    @SerialName("next_calibration_date") val nextCalibrationDate: String?,
    @SerialName("calibration_status") val calibrationStatus: String?,
    val category: Category?,
    @SerialName("current_location") val currentLocation: Location?,
    @SerialName("current_holder") val currentHolder: User?,
    @SerialName("purchase_date") val purchaseDate: String?,
    @SerialName("purchase_price") val purchasePrice: Double?,
    @SerialName("current_value") val currentValue: Double?,
    val tags: List<EquipmentTag>?
)

@Serializable
data class EquipmentTag(
    val id: String,
    @SerialName("tag_type") val tagType: String,
    @SerialName("tag_value") val tagValue: String
)

@Serializable
data class Category(
    val id: String,
    val name: String,
    val code: String? = null,
    val description: String? = null,
    val color: String? = null,
    @SerialName("requires_calibration") val requiresCalibration: Boolean = false,
    @SerialName("default_calibration_interval_days") val defaultCalibrationIntervalDays: Int? = null
)

@Serializable
data class Location(
    val id: String,
    val name: String,
    val code: String?,
    val address: String?,
    @SerialName("gps_lat") val gpsLat: Double?,
    @SerialName("gps_lng") val gpsLng: Double?
)

@Serializable
data class Manufacturer(
    val id: String,
    val name: String,
    val website: String?,
    @SerialName("support_contact") val supportContact: String?
)

@Serializable
data class AccessoryType(
    val id: String,
    val name: String,
    @SerialName("category_id") val categoryId: String?
)

@Serializable
data class TransferRequest(
    val id: String,
    @SerialName("equipment_id") val equipmentId: String? = null,
    @SerialName("requester_id") val requesterId: String,
    @SerialName("holder_id") val holderId: String?,
    val status: String,
    @SerialName("request_type") val requestType: String,
    val message: String?,
    @SerialName("needed_from") val neededFrom: String? = null,
    @SerialName("needed_until") val neededUntil: String? = null,
    @SerialName("expires_at") val expiresAt: String?,
    @SerialName("created_at") val createdAt: String? = null,
    val equipment: Equipment?,
    val requester: User?,
    val holder: User?,
    val category: Category? = null
)

@Serializable
data class CreateTransferRequest(
    @SerialName("request_type") val requestType: String,
    @SerialName("equipment_id") val equipmentId: String? = null,
    @SerialName("category_id") val categoryId: String? = null,
    @SerialName("holder_id") val holderId: String? = null,
    @SerialName("needed_from") val neededFrom: String? = null,
    @SerialName("needed_until") val neededUntil: String? = null,
    val message: String? = null
)

@Serializable
data class TransferOffer(
    val id: String,
    @SerialName("request_id") val requestId: String,
    @SerialName("equipment_id") val equipmentId: String,
    @SerialName("offerer_id") val offererId: String,
    val status: String,
    val equipment: Equipment?,
    val offerer: User?
)

@Serializable
data class OnboardingSession(
    @SerialName("session_id") val sessionId: String,
    @SerialName("current_step") val currentStep: Int,
    @SerialName("total_steps") val totalSteps: Int,
    val data: OnboardingData?,
    @SerialName("created_at") val createdAt: String?
)

@Serializable
data class OnboardingData(
    @SerialName("tag_value") val tagValue: String? = null,
    @SerialName("tag_type") val tagType: String? = null,
    val photos: List<String>? = null,
    val name: String? = null,
    val description: String? = null,
    @SerialName("category_id") val categoryId: String? = null,
    @SerialName("location_id") val locationId: String? = null,
    @SerialName("serial_number") val serialNumber: String? = null,
    @SerialName("manufacturer_id") val manufacturerId: String? = null,
    @SerialName("model_id") val modelId: String? = null,
    val accessories: List<String>? = null,
    @SerialName("requires_calibration") val requiresCalibration: Boolean? = null,
    @SerialName("calibration_interval_days") val calibrationIntervalDays: Int? = null,
    @SerialName("last_calibration_date") val lastCalibrationDate: String? = null,
    @SerialName("calibration_lab") val calibrationLab: String? = null,
    @SerialName("certificate_number") val certificateNumber: String? = null
)

@Serializable
data class Calibration(
    val id: String,
    @SerialName("equipment_id") val equipmentId: String,
    @SerialName("calibration_date") val calibrationDate: String,
    @SerialName("calibration_lab") val calibrationLab: String?,
    @SerialName("certificate_number") val certificateNumber: String?,
    val result: String,
    @SerialName("valid_until") val validUntil: String?,
    val notes: String?,
    val equipment: Equipment?
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String
)

@Serializable
data class LoginResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    @SerialName("token_type") val tokenType: String,
    val user: User
)

@Serializable
data class PaginatedResponse<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val size: Int,
    val pages: Int
)

@Serializable
data class TagLookupResponse(
    val found: Boolean,
    val equipment: Equipment?,
    @SerialName("tag_type") val tagType: String?,
    @SerialName("tag_value") val tagValue: String?
)
