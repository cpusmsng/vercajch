package sk.sppd.vercajch.ui.screens.scanner

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.BuildConfig
import sk.sppd.vercajch.MainActivity
import sk.sppd.vercajch.data.repository.EquipmentRepository
import sk.sppd.vercajch.util.NfcTagInfo
import javax.inject.Inject

data class ScannerUiState(
    val isLoading: Boolean = false,
    val equipmentId: String? = null,
    val newTagValue: String? = null,
    val error: String? = null,
    val lastScannedValue: String? = null,
    val nfcTagInfo: NfcTagInfo? = null
)

@HiltViewModel
class ScannerViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ScannerUiState())
    val uiState: StateFlow<ScannerUiState> = _uiState.asStateFlow()

    private var isProcessing = false

    init {
        // Listen for NFC tags scanned from MainActivity
        viewModelScope.launch {
            MainActivity.nfcTagScanned.collect { tagInfo ->
                if (tagInfo != null) {
                    onNfcTagScanned(tagInfo)
                    MainActivity.clearNfcTag()
                }
            }
        }
    }

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

                lookupTag(tagValue)
            } finally {
                isProcessing = false
            }
        }
    }

    private fun onNfcTagScanned(tagInfo: NfcTagInfo) {
        if (isProcessing) {
            return
        }

        val tagValue = tagInfo.content ?: tagInfo.id

        if (tagValue == _uiState.value.lastScannedValue) {
            return
        }

        isProcessing = true
        _uiState.value = ScannerUiState(
            isLoading = true,
            lastScannedValue = tagValue,
            nfcTagInfo = tagInfo
        )

        viewModelScope.launch {
            try {
                lookupTag(tagValue)
            } finally {
                isProcessing = false
            }
        }
    }

    private suspend fun lookupTag(tagValue: String) {
        equipmentRepository.lookupTag(tagValue)
            .onSuccess { response ->
                if (response.found && response.equipment != null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        equipmentId = response.equipment.id
                    )
                } else {
                    // New equipment - start onboarding
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        newTagValue = tagValue
                    )
                }
            }
            .onFailure { exception ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = exception.message ?: "Vyhľadávanie zlyhalo"
                )
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
