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
    val isRefreshing: Boolean = false,
    val equipment: List<Equipment> = emptyList(),
    val error: String? = null,
    val currentPage: Int = 1,
    val hasMore: Boolean = false,
    val searchQuery: String = ""
)

@HiltViewModel
class EquipmentListViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(EquipmentListUiState())
    val uiState: StateFlow<EquipmentListUiState> = _uiState.asStateFlow()

    private var searchJob: Job? = null
    private var isInitialized = false

    init {
        loadEquipment()
    }

    fun search(query: String) {
        // Skip if query hasn't changed
        if (query == _uiState.value.searchQuery && isInitialized) return

        searchJob?.cancel()

        searchJob = viewModelScope.launch {
            delay(300) // Debounce
            _uiState.value = _uiState.value.copy(
                searchQuery = query,
                currentPage = 1
            )
            loadEquipmentInternal(clearList = true)
        }
    }

    fun loadEquipment() {
        loadEquipmentInternal(clearList = false)
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true, currentPage = 1)
            loadEquipmentInternal(clearList = true, isRefresh = true)
        }
    }

    private fun loadEquipmentInternal(clearList: Boolean = false, isRefresh: Boolean = false) {
        viewModelScope.launch {
            if (!isRefresh) {
                _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            }

            val searchQuery = _uiState.value.searchQuery.takeIf { it.isNotBlank() }

            equipmentRepository.getEquipment(
                page = _uiState.value.currentPage,
                search = searchQuery
            )
                .onSuccess { response ->
                    isInitialized = true
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        isRefreshing = false,
                        equipment = if (clearList || _uiState.value.currentPage == 1) {
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
                        isRefreshing = false,
                        error = exception.message ?: "Načítanie zlyhalo"
                    )
                }
        }
    }

    fun loadMore() {
        if (_uiState.value.isLoading || !_uiState.value.hasMore) return

        _uiState.value = _uiState.value.copy(currentPage = _uiState.value.currentPage + 1)
        loadEquipmentInternal(clearList = false)
    }
}
