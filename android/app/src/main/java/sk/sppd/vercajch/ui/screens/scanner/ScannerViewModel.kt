package sk.sppd.vercajch.ui.screens.scanner

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.BuildConfig
import sk.sppd.vercajch.data.repository.EquipmentRepository
import javax.inject.Inject

data class ScannerUiState(
    val isLoading: Boolean = false,
    val equipmentId: String? = null,
    val newTagValue: String? = null,
    val error: String? = null,
    val lastScannedValue: String? = null
)

@HiltViewModel
class ScannerViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ScannerUiState())
    val uiState: StateFlow<ScannerUiState> = _uiState.asStateFlow()

    private var isProcessing = false

    fun onBarcodeScanned(value: String) {
        if (isProcessing || value == _uiState.value.lastScannedValue) {
            return
        }

        isProcessing = true
        _uiState.value = ScannerUiState(isLoading = true, lastScannedValue = value)

        viewModelScope.launch {
            try {
                // Extract UUID from QR code URL or use raw value
                val tagValue = extractTagValue(value)

                equipmentRepository.lookupTag(tagValue)
                    .onSuccess { response ->
                        if (response.found && response.equipment != null) {
                            _uiState.value = ScannerUiState(
                                equipmentId = response.equipment.id,
                                lastScannedValue = value
                            )
                        } else {
                            // New equipment - start onboarding
                            _uiState.value = ScannerUiState(
                                newTagValue = tagValue,
                                lastScannedValue = value
                            )
                        }
                    }
                    .onFailure { exception ->
                        _uiState.value = ScannerUiState(
                            error = exception.message ?: "Vyhľadávanie zlyhalo",
                            lastScannedValue = value
                        )
                    }
            } finally {
                isProcessing = false
            }
        }
    }

    private fun extractTagValue(qrContent: String): String {
        // Check if it's a URL from our domain
        val qrBaseUrl = BuildConfig.QR_BASE_URL
        return if (qrContent.startsWith(qrBaseUrl)) {
            qrContent.removePrefix("$qrBaseUrl/")
        } else if (qrContent.startsWith("https://equip.spp-d.sk/scan/")) {
            qrContent.removePrefix("https://equip.spp-d.sk/scan/")
        } else {
            // Assume it's a raw tag value (QR code or RFID)
            qrContent
        }
    }

    fun resetState() {
        _uiState.value = ScannerUiState()
        isProcessing = false
    }
}
