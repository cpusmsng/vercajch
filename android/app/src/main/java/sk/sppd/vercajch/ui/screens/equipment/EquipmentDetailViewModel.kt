package sk.sppd.vercajch.ui.screens.equipment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.model.Equipment
import sk.sppd.vercajch.data.repository.EquipmentRepository
import javax.inject.Inject

data class EquipmentDetailUiState(
    val isLoading: Boolean = false,
    val equipment: Equipment? = null,
    val error: String? = null
)

@HiltViewModel
class EquipmentDetailViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(EquipmentDetailUiState())
    val uiState: StateFlow<EquipmentDetailUiState> = _uiState.asStateFlow()

    fun loadEquipment(id: String) {
        viewModelScope.launch {
            _uiState.value = EquipmentDetailUiState(isLoading = true)

            equipmentRepository.getEquipmentById(id)
                .onSuccess { equipment ->
                    _uiState.value = EquipmentDetailUiState(equipment = equipment)
                }
                .onFailure { exception ->
                    _uiState.value = EquipmentDetailUiState(
                        error = exception.message ?: "Načítanie zlyhalo"
                    )
                }
        }
    }
}
