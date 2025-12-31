package sk.sppd.vercajch

import android.content.Intent
import android.nfc.NfcAdapter
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.content.getSystemService
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import sk.sppd.vercajch.ui.navigation.VercajchNavHost
import sk.sppd.vercajch.ui.theme.VercajchTheme
import sk.sppd.vercajch.util.NfcManager
import sk.sppd.vercajch.util.NfcTagInfo

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private lateinit var nfcManager: NfcManager

    companion object {
        private val _nfcTagScanned = MutableStateFlow<NfcTagInfo?>(null)
        val nfcTagScanned = _nfcTagScanned.asStateFlow()

        fun clearNfcTag() {
            _nfcTagScanned.value = null
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        nfcManager = NfcManager(this)

        // Check initial intent for NFC
        handleIntent(intent)

        enableEdgeToEdge()
        setContent {
            VercajchTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    VercajchNavHost()
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        if (nfcManager.isNfcSupported) {
            nfcManager.enableForegroundDispatch()
        }
    }

    override fun onPause() {
        super.onPause()
        if (nfcManager.isNfcSupported) {
            nfcManager.disableForegroundDispatch()
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        if (intent.action in listOf(
                NfcAdapter.ACTION_NDEF_DISCOVERED,
                NfcAdapter.ACTION_TAG_DISCOVERED,
                NfcAdapter.ACTION_TECH_DISCOVERED
            )) {
            val tagInfo = nfcManager.processIntent(intent)
            if (tagInfo != null) {
                // Vibrate to indicate successful scan
                vibrateOnScan()

                // Emit the tag info for the scanner to pick up
                _nfcTagScanned.value = tagInfo

                Toast.makeText(
                    this,
                    "NFC tag: ${tagInfo.type}\nID: ${tagInfo.id}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun vibrateOnScan() {
        try {
            val vibrator = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.S) {
                getSystemService<VibratorManager>()?.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService<Vibrator>()
            }

            vibrator?.let {
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    it.vibrate(VibrationEffect.createOneShot(100, VibrationEffect.DEFAULT_AMPLITUDE))
                } else {
                    @Suppress("DEPRECATION")
                    it.vibrate(100)
                }
            }
        } catch (e: Exception) {
            // Ignore vibration errors
        }
    }
}
