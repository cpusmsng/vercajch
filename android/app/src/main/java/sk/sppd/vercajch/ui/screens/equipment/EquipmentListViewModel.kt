package sk.sppd.vercajch.ui.screens.equipment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.model.Equipment
import sk.sppd.vercajch.data.repository.EquipmentRepository
import javax.inject.Inject

data class EquipmentListUiState(
    val isLoading: Boolean = false,
    val equipment: List<Equipment> = emptyList(),
    val error: String? = null,
    val currentPage: Int = 1,
    val hasMore: Boolean = false
)

@HiltViewModel
class EquipmentListViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(EquipmentListUiState())
    val uiState: StateFlow<EquipmentListUiState> = _uiState.asStateFlow()

    private var searchJob: Job? = null
    private var currentSearchQuery: String? = null

    init {
        loadEquipment()
    }

    fun search(query: String) {
        searchJob?.cancel()
        currentSearchQuery = query.takeIf { it.isNotBlank() }

        searchJob = viewModelScope.launch {
            delay(300) // Debounce
            _uiState.value = _uiState.value.copy(currentPage = 1, equipment = emptyList())
            loadEquipment()
        }
    }

    fun loadEquipment() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            equipmentRepository.getEquipment(
                page = _uiState.value.currentPage,
                search = currentSearchQuery
            )
                .onSuccess { response ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        equipment = if (_uiState.value.currentPage == 1) {
                            response.items
                        } else {
                            _uiState.value.equipment + response.items
                        },
                        hasMore = response.page < response.pages
                    )
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = exception.message ?: "Načítanie zlyhalo"
                    )
                }
        }
    }

    fun loadMore() {
        if (_uiState.value.isLoading || !_uiState.value.hasMore) return

        _uiState.value = _uiState.value.copy(currentPage = _uiState.value.currentPage + 1)
        loadEquipment()
    }
}
