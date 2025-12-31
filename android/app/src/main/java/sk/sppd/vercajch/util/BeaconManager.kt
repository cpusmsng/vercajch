package sk.sppd.vercajch.util

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Build
import android.os.ParcelUuid
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.nio.ByteBuffer
import java.util.UUID

data class BeaconInfo(
    val id: String,
    val type: BeaconType,
    val uuid: String? = null,
    val major: Int? = null,
    val minor: Int? = null,
    val namespace: String? = null,
    val instance: String? = null,
    val rssi: Int,
    val distance: Double,
    val macAddress: String
)

enum class BeaconType {
    IBEACON,
    EDDYSTONE_UID,
    EDDYSTONE_URL,
    ALTBEACON,
    UNKNOWN
}

class BeaconManager(private val context: Context) {

    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager?.adapter
    private var bluetoothLeScanner: BluetoothLeScanner? = null

    private val _nearbyBeacons = MutableStateFlow<List<BeaconInfo>>(emptyList())
    val nearbyBeacons: StateFlow<List<BeaconInfo>> = _nearbyBeacons.asStateFlow()

    private val _isScanning = MutableStateFlow(false)
    val isScanning: StateFlow<Boolean> = _isScanning.asStateFlow()

    private val discoveredBeacons = mutableMapOf<String, BeaconInfo>()

    val isBluetoothSupported: Boolean
        get() = bluetoothAdapter != null

    val isBluetoothEnabled: Boolean
        get() = bluetoothAdapter?.isEnabled == true

    private val scanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            processResult(result)
        }

        override fun onBatchScanResults(results: List<ScanResult>) {
            results.forEach { processResult(it) }
        }

        override fun onScanFailed(errorCode: Int) {
            _isScanning.value = false
        }
    }

    @SuppressLint("MissingPermission")
    private fun processResult(result: ScanResult) {
        val beacon = parseBeacon(result) ?: return
        discoveredBeacons[beacon.macAddress] = beacon
        _nearbyBeacons.value = discoveredBeacons.values
            .sortedBy { it.distance }
            .toList()
    }

    private fun parseBeacon(result: ScanResult): BeaconInfo? {
        val scanRecord = result.scanRecord ?: return null
        val bytes = scanRecord.bytes ?: return null
        val rssi = result.rssi
        val macAddress = result.device?.address ?: return null

        // Try to parse as iBeacon
        parseIBeacon(bytes, rssi, macAddress)?.let { return it }

        // Try to parse as Eddystone
        parseEddystone(scanRecord, rssi, macAddress)?.let { return it }

        // Try to parse as AltBeacon
        parseAltBeacon(bytes, rssi, macAddress)?.let { return it }

        return null
    }

    private fun parseIBeacon(bytes: ByteArray, rssi: Int, macAddress: String): BeaconInfo? {
        // iBeacon format: 0x02 0x15 [UUID 16 bytes] [Major 2 bytes] [Minor 2 bytes] [TxPower 1 byte]
        val startByte = bytes.indexOfFirst { it == 0x02.toByte() && bytes.getOrNull(bytes.indexOf(it) + 1) == 0x15.toByte() }
        if (startByte == -1 || startByte + 23 > bytes.size) return null

        try {
            val uuidBytes = bytes.sliceArray(startByte + 2 until startByte + 18)
            val uuid = formatUUID(uuidBytes)

            val major = ((bytes[startByte + 18].toInt() and 0xFF) shl 8) or (bytes[startByte + 19].toInt() and 0xFF)
            val minor = ((bytes[startByte + 20].toInt() and 0xFF) shl 8) or (bytes[startByte + 21].toInt() and 0xFF)
            val txPower = bytes[startByte + 22].toInt()

            val distance = calculateDistance(txPower, rssi)

            return BeaconInfo(
                id = "$uuid:$major:$minor",
                type = BeaconType.IBEACON,
                uuid = uuid,
                major = major,
                minor = minor,
                rssi = rssi,
                distance = distance,
                macAddress = macAddress
            )
        } catch (e: Exception) {
            return null
        }
    }

    private fun parseEddystone(scanRecord: android.bluetooth.le.ScanRecord, rssi: Int, macAddress: String): BeaconInfo? {
        val serviceData = scanRecord.getServiceData(ParcelUuid.fromString(EDDYSTONE_SERVICE_UUID))
            ?: return null

        if (serviceData.isEmpty()) return null

        return when (serviceData[0].toInt()) {
            0x00 -> parseEddystoneUid(serviceData, rssi, macAddress)
            0x10 -> parseEddystoneUrl(serviceData, rssi, macAddress)
            else -> null
        }
    }

    private fun parseEddystoneUid(data: ByteArray, rssi: Int, macAddress: String): BeaconInfo? {
        if (data.size < 18) return null

        val txPower = data[1].toInt()
        val namespace = data.sliceArray(2..11).toHexString()
        val instance = data.sliceArray(12..17).toHexString()

        val distance = calculateDistance(txPower, rssi)

        return BeaconInfo(
            id = "$namespace:$instance",
            type = BeaconType.EDDYSTONE_UID,
            namespace = namespace,
            instance = instance,
            rssi = rssi,
            distance = distance,
            macAddress = macAddress
        )
    }

    private fun parseEddystoneUrl(data: ByteArray, rssi: Int, macAddress: String): BeaconInfo? {
        if (data.size < 3) return null

        val txPower = data[1].toInt()
        val urlScheme = when (data[2].toInt()) {
            0 -> "http://www."
            1 -> "https://www."
            2 -> "http://"
            3 -> "https://"
            else -> ""
        }

        val url = urlScheme + String(data.sliceArray(3 until data.size))
        val distance = calculateDistance(txPower, rssi)

        return BeaconInfo(
            id = url,
            type = BeaconType.EDDYSTONE_URL,
            rssi = rssi,
            distance = distance,
            macAddress = macAddress
        )
    }

    private fun parseAltBeacon(bytes: ByteArray, rssi: Int, macAddress: String): BeaconInfo? {
        // AltBeacon format: [MfgId 2 bytes] 0xBE 0xAC [ID 20 bytes] [RefRSSI 1 byte] [MfgReserved 1 byte]
        val startByte = bytes.indexOfFirst {
            it == 0xBE.toByte() && bytes.getOrNull(bytes.indexOf(it) + 1) == 0xAC.toByte()
        }
        if (startByte == -1 || startByte + 22 > bytes.size) return null

        try {
            val idBytes = bytes.sliceArray(startByte + 2 until startByte + 22)
            val id = idBytes.toHexString()
            val txPower = bytes[startByte + 22].toInt()

            val distance = calculateDistance(txPower, rssi)

            return BeaconInfo(
                id = id,
                type = BeaconType.ALTBEACON,
                rssi = rssi,
                distance = distance,
                macAddress = macAddress
            )
        } catch (e: Exception) {
            return null
        }
    }

    private fun calculateDistance(txPower: Int, rssi: Int): Double {
        if (rssi == 0) return -1.0

        val ratio = rssi.toDouble() / txPower
        return if (ratio < 1.0) {
            Math.pow(ratio, 10.0)
        } else {
            0.89976 * Math.pow(ratio, 7.7095) + 0.111
        }
    }

    private fun formatUUID(bytes: ByteArray): String {
        val buffer = ByteBuffer.wrap(bytes)
        val high = buffer.long
        val low = buffer.long
        return UUID(high, low).toString()
    }

    private fun ByteArray.toHexString(): String {
        return joinToString("") { "%02X".format(it) }
    }

    @SuppressLint("MissingPermission")
    fun startScanning() {
        if (!isBluetoothEnabled || _isScanning.value) return

        bluetoothLeScanner = bluetoothAdapter?.bluetoothLeScanner ?: return

        val settings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        val filters = listOf<ScanFilter>()

        try {
            bluetoothLeScanner?.startScan(filters, settings, scanCallback)
            _isScanning.value = true
        } catch (e: Exception) {
            _isScanning.value = false
        }
    }

    @SuppressLint("MissingPermission")
    fun stopScanning() {
        try {
            bluetoothLeScanner?.stopScan(scanCallback)
        } catch (e: Exception) {
            // Ignore errors when stopping scan
        }
        _isScanning.value = false
    }

    fun clearBeacons() {
        discoveredBeacons.clear()
        _nearbyBeacons.value = emptyList()
    }

    companion object {
        private const val EDDYSTONE_SERVICE_UUID = "0000FEAA-0000-1000-8000-00805F9B34FB"
    }
}
