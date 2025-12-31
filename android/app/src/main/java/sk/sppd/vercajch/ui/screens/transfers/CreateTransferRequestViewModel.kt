package sk.sppd.vercajch.ui.screens.transfers

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.repository.TransferRepository
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject

data class CreateTransferRequestUiState(
    val isLoading: Boolean = false,
    val success: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class CreateTransferRequestViewModel @Inject constructor(
    private val transferRepository: TransferRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateTransferRequestUiState())
    val uiState: StateFlow<CreateTransferRequestUiState> = _uiState.asStateFlow()

    fun createRequest(
        equipmentId: String,
        holderId: String?,
        neededUntil: String?,
        message: String?
    ) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            // Format dates for API (ISO format with time)
            val neededUntilFormatted = neededUntil?.let {
                "${it}T23:59:59"
            }

            transferRepository.createRequest(
                requestType = "direct",
                equipmentId = equipmentId,
                holderId = holderId,
                neededUntil = neededUntilFormatted,
                message = message
            ).onSuccess {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    success = true
                )
            }.onFailure { e ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Nepodarilo sa vytvoriť požiadavku"
                )
            }
        }
    }
}
