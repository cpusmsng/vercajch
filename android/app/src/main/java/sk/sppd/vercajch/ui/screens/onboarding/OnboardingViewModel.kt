package sk.sppd.vercajch.ui.screens.onboarding

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.model.AccessoryType
import sk.sppd.vercajch.data.model.Category
import sk.sppd.vercajch.data.model.Location
import sk.sppd.vercajch.data.repository.EquipmentRepository
import sk.sppd.vercajch.data.repository.OnboardingRepository
import java.io.File
import javax.inject.Inject

data class OnboardingUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val sessionId: String? = null,
    val currentStep: Int = 1,
    val completedEquipmentId: String? = null,

    // Step 1: Tag
    val tagValue: String = "",

    // Step 2: Photos
    val photos: List<Uri> = emptyList(),
    val uploadedPhotoIds: List<String> = emptyList(),

    // Step 3: Details
    val name: String = "",
    val description: String = "",
    val serialNumber: String = "",
    val categoryId: String? = null,
    val locationId: String? = null,
    val categories: List<Category> = emptyList(),
    val locations: List<Location> = emptyList(),

    // Step 4: Accessories
    val accessoryTypes: List<String> = emptyList(),
    val selectedAccessories: Set<String> = emptySet(),

    // Step 5: Calibration
    val requiresCalibration: Boolean = false,
    val calibrationIntervalDays: String = "",
    val lastCalibrationDate: String = "",
    val calibrationLab: String = "",
    val certificateNumber: String = ""
)

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val onboardingRepository: OnboardingRepository,
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun startOnboarding(initialTagValue: String?) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            // Load categories and locations
            val categories = equipmentRepository.getCategories().getOrNull() ?: emptyList()
            val locations = equipmentRepository.getLocations().getOrNull() ?: emptyList()

            onboardingRepository.startOnboarding()
                .onSuccess { session ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        sessionId = session.sessionId,
                        tagValue = initialTagValue ?: "",
                        categories = categories,
                        locations = locations
                    )
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
        }
    }

    fun updateTagValue(value: String) {
        _uiState.value = _uiState.value.copy(tagValue = value)
    }

    fun addPhoto(context: Context, uri: Uri) {
        _uiState.value = _uiState.value.copy(
            photos = _uiState.value.photos + uri
        )
    }

    fun removePhoto(index: Int) {
        _uiState.value = _uiState.value.copy(
            photos = _uiState.value.photos.filterIndexed { i, _ -> i != index }
        )
    }

    fun updateName(value: String) {
        _uiState.value = _uiState.value.copy(name = value)
    }

    fun updateDescription(value: String) {
        _uiState.value = _uiState.value.copy(description = value)
    }

    fun updateSerialNumber(value: String) {
        _uiState.value = _uiState.value.copy(serialNumber = value)
    }

    fun updateCategory(id: String) {
        val category = _uiState.value.categories.find { it.id == id }
        _uiState.value = _uiState.value.copy(
            categoryId = id,
            requiresCalibration = category?.requiresCertification ?: false,
            calibrationIntervalDays = category?.defaultMaintenanceIntervalDays?.toString() ?: ""
        )

        // Load accessory types for category
        viewModelScope.launch {
            equipmentRepository.getAccessoryTypes(id)
                .onSuccess { types ->
                    _uiState.value = _uiState.value.copy(
                        accessoryTypes = types.map { it.name }
                    )
                }
        }
    }

    fun updateLocation(id: String) {
        _uiState.value = _uiState.value.copy(locationId = id)
    }

    fun toggleAccessory(name: String) {
        val current = _uiState.value.selectedAccessories
        _uiState.value = _uiState.value.copy(
            selectedAccessories = if (current.contains(name)) {
                current - name
            } else {
                current + name
            }
        )
    }

    fun updateRequiresCalibration(value: Boolean) {
        _uiState.value = _uiState.value.copy(requiresCalibration = value)
    }

    fun updateCalibrationInterval(value: String) {
        _uiState.value = _uiState.value.copy(calibrationIntervalDays = value)
    }

    fun updateLastCalibrationDate(value: String) {
        _uiState.value = _uiState.value.copy(lastCalibrationDate = value)
    }

    fun updateCalibrationLab(value: String) {
        _uiState.value = _uiState.value.copy(calibrationLab = value)
    }

    fun updateCertificateNumber(value: String) {
        _uiState.value = _uiState.value.copy(certificateNumber = value)
    }

    fun canProceed(): Boolean {
        return when (_uiState.value.currentStep) {
            1 -> _uiState.value.tagValue.isNotBlank()
            2 -> true // Photos are optional
            3 -> _uiState.value.name.isNotBlank() &&
                    _uiState.value.categoryId != null &&
                    _uiState.value.locationId != null
            4 -> true // Accessories are optional
            5 -> !_uiState.value.requiresCalibration ||
                    _uiState.value.calibrationIntervalDays.isNotBlank()
            6 -> true
            else -> false
        }
    }

    fun nextStep() {
        if (_uiState.value.currentStep < 6) {
            _uiState.value = _uiState.value.copy(
                currentStep = _uiState.value.currentStep + 1,
                error = null
            )
        }
    }

    fun previousStep() {
        if (_uiState.value.currentStep > 1) {
            _uiState.value = _uiState.value.copy(
                currentStep = _uiState.value.currentStep - 1,
                error = null
            )
        }
    }

    fun complete() {
        val sessionId = _uiState.value.sessionId ?: return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            // Submit all steps
            val state = _uiState.value

            // Step 1: Tag
            onboardingRepository.submitStep(sessionId, 1, mapOf(
                "tag_value" to state.tagValue,
                "tag_type" to "qr"
            ))

            // Step 2: Photos (simplified - would need actual file upload)
            onboardingRepository.submitStep(sessionId, 2, mapOf(
                "photos" to state.uploadedPhotoIds
            ))

            // Step 3: Details
            onboardingRepository.submitStep(sessionId, 3, mapOf(
                "name" to state.name,
                "description" to state.description.takeIf { it.isNotBlank() },
                "category_id" to state.categoryId,
                "location_id" to state.locationId,
                "serial_number" to state.serialNumber.takeIf { it.isNotBlank() }
            ))

            // Step 4: Accessories
            onboardingRepository.submitStep(sessionId, 4, mapOf(
                "accessories" to state.selectedAccessories.toList()
            ))

            // Step 5: Calibration
            if (state.requiresCalibration) {
                onboardingRepository.submitStep(sessionId, 5, mapOf(
                    "requires_calibration" to true,
                    "calibration_interval_days" to state.calibrationIntervalDays.toIntOrNull(),
                    "last_calibration_date" to state.lastCalibrationDate.takeIf { it.isNotBlank() },
                    "calibration_lab" to state.calibrationLab.takeIf { it.isNotBlank() },
                    "certificate_number" to state.certificateNumber.takeIf { it.isNotBlank() }
                ))
            } else {
                onboardingRepository.submitStep(sessionId, 5, mapOf(
                    "requires_calibration" to false
                ))
            }

            // Complete
            onboardingRepository.complete(sessionId)
                .onSuccess { equipment ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        completedEquipmentId = equipment.id
                    )
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message ?: "Uloženie zlyhalo"
                    )
                }
        }
    }

    fun cancelOnboarding() {
        val sessionId = _uiState.value.sessionId ?: return
        viewModelScope.launch {
            onboardingRepository.cancel(sessionId)
        }
    }
}
