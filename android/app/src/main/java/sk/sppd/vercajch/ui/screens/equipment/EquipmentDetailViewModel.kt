package sk.sppd.vercajch.ui.screens.equipment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.data.model.Equipment
import sk.sppd.vercajch.data.model.EquipmentUpdate
import sk.sppd.vercajch.data.model.UpdateResult
import sk.sppd.vercajch.data.repository.EquipmentRepository
import javax.inject.Inject

data class EquipmentDetailUiState(
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val isSaving: Boolean = false,
    val equipment: Equipment? = null,
    val error: String? = null,
    val conflictDetected: Boolean = false,
    val conflictMessage: String? = null,
    val saveSuccess: Boolean = false
)

@HiltViewModel
class EquipmentDetailViewModel @Inject constructor(
    private val equipmentRepository: EquipmentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(EquipmentDetailUiState())
    val uiState: StateFlow<EquipmentDetailUiState> = _uiState.asStateFlow()

    private var currentEquipmentId: String? = null

    fun loadEquipment(id: String) {
        currentEquipmentId = id
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

    fun refresh() {
        val id = currentEquipmentId ?: return
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true, conflictDetected = false, conflictMessage = null)

            equipmentRepository.getEquipmentById(id)
                .onSuccess { equipment ->
                    _uiState.value = _uiState.value.copy(
                        isRefreshing = false,
                        equipment = equipment
                    )
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isRefreshing = false,
                        error = exception.message ?: "Obnovenie zlyhalo"
                    )
                }
        }
    }

    fun updateEquipment(update: EquipmentUpdate) {
        val id = currentEquipmentId ?: return
        val currentVersion = _uiState.value.equipment?.version ?: 1

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSaving = true, error = null)

            val updateWithVersion = update.copy(version = currentVersion)
            when (val result = equipmentRepository.updateEquipment(id, updateWithVersion)) {
                is UpdateResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isSaving = false,
                        equipment = result.data,
                        saveSuccess = true
                    )
                }
                is UpdateResult.Conflict -> {
                    _uiState.value = _uiState.value.copy(
                        isSaving = false,
                        conflictDetected = true,
                        conflictMessage = result.message
                    )
                }
                is UpdateResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isSaving = false,
                        error = result.message
                    )
                }
            }
        }
    }

    fun clearSaveSuccess() {
        _uiState.value = _uiState.value.copy(saveSuccess = false)
    }

    fun clearConflict() {
        _uiState.value = _uiState.value.copy(conflictDetected = false, conflictMessage = null)
    }
}
