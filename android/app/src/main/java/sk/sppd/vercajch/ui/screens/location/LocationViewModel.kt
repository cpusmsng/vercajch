package sk.sppd.vercajch.ui.screens.location

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import sk.sppd.vercajch.util.BeaconInfo
import sk.sppd.vercajch.util.BeaconManager
import sk.sppd.vercajch.util.GpsLocation
import sk.sppd.vercajch.util.LocationManager
import javax.inject.Inject

data class LocationUiState(
    val isScanning: Boolean = false,
    val nearbyBeacons: List<BeaconInfo> = emptyList(),
    val gpsLocation: GpsLocation? = null,
    val isBluetoothEnabled: Boolean = true,
    val error: String? = null
)

@HiltViewModel
class LocationViewModel @Inject constructor(
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val beaconManager = BeaconManager(context)
    private val locationManager = LocationManager(context)

    private val _uiState = MutableStateFlow(LocationUiState())
    val uiState: StateFlow<LocationUiState> = _uiState.asStateFlow()

    init {
        // Collect beacon updates
        viewModelScope.launch {
            beaconManager.nearbyBeacons.collect { beacons ->
                _uiState.value = _uiState.value.copy(nearbyBeacons = beacons)
            }
        }

        // Collect scanning state
        viewModelScope.launch {
            beaconManager.isScanning.collect { isScanning ->
                _uiState.value = _uiState.value.copy(isScanning = isScanning)
            }
        }

        // Collect GPS location
        viewModelScope.launch {
            locationManager.currentLocation.collect { location ->
                _uiState.value = _uiState.value.copy(gpsLocation = location)
            }
        }

        // Check Bluetooth status
        _uiState.value = _uiState.value.copy(
            isBluetoothEnabled = beaconManager.isBluetoothEnabled
        )
    }

    fun startScanning() {
        if (!beaconManager.isBluetoothEnabled) {
            _uiState.value = _uiState.value.copy(
                isBluetoothEnabled = false,
                error = "Bluetooth je vypnutý"
            )
            return
        }

        beaconManager.clearBeacons()
        beaconManager.startScanning()
        locationManager.startTracking()

        // Also try to get initial GPS location
        viewModelScope.launch {
            try {
                val location = locationManager.getCurrentLocation()
                _uiState.value = _uiState.value.copy(gpsLocation = location)
            } catch (e: Exception) {
                // Ignore GPS errors
            }
        }
    }

    fun stopScanning() {
        beaconManager.stopScanning()
        locationManager.stopTracking()
    }

    override fun onCleared() {
        super.onCleared()
        stopScanning()
    }
}
