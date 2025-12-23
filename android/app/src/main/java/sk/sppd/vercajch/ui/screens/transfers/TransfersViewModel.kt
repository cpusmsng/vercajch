package sk.sppd.vercajch.ui.screens.transfers

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.model.TransferRequest
import sk.sppd.vercajch.data.repository.TransferRepository
import javax.inject.Inject

data class TransfersUiState(
    val isLoading: Boolean = false,
    val sentRequests: List<TransferRequest> = emptyList(),
    val receivedRequests: List<TransferRequest> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class TransfersViewModel @Inject constructor(
    private val transferRepository: TransferRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TransfersUiState())
    val uiState: StateFlow<TransfersUiState> = _uiState.asStateFlow()

    fun loadTransfers() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            val sentResult = transferRepository.getSentRequests()
            val receivedResult = transferRepository.getReceivedRequests()

            if (sentResult.isSuccess && receivedResult.isSuccess) {
                _uiState.value = TransfersUiState(
                    sentRequests = sentResult.getOrDefault(emptyList()),
                    receivedRequests = receivedResult.getOrDefault(emptyList())
                )
            } else {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = sentResult.exceptionOrNull()?.message
                        ?: receivedResult.exceptionOrNull()?.message
                        ?: "Načítanie zlyhalo"
                )
            }
        }
    }

    fun acceptRequest(requestId: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            transferRepository.acceptRequest(requestId)
                .onSuccess {
                    loadTransfers()
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
        }
    }

    fun rejectRequest(requestId: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            transferRepository.rejectRequest(requestId)
                .onSuccess {
                    loadTransfers()
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
        }
    }

    fun cancelRequest(requestId: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            transferRepository.cancelRequest(requestId)
                .onSuccess {
                    loadTransfers()
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
        }
    }
}
