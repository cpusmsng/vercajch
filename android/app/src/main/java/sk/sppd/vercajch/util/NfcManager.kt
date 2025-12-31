package sk.sppd.vercajch.util

import android.app.Activity
import android.app.PendingIntent
import android.content.Intent
import android.content.IntentFilter
import android.nfc.NdefMessage
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.nfc.tech.MifareUltralight
import android.nfc.tech.Ndef
import android.nfc.tech.NfcA
import android.os.Build
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class NfcTagInfo(
    val id: String,
    val type: String,
    val techList: List<String>,
    val content: String? = null
)

class NfcManager(private val activity: Activity) {

    private val nfcAdapter: NfcAdapter? = NfcAdapter.getDefaultAdapter(activity)

    private val _tagInfo = MutableStateFlow<NfcTagInfo?>(null)
    val tagInfo: StateFlow<NfcTagInfo?> = _tagInfo.asStateFlow()

    val isNfcSupported: Boolean
        get() = nfcAdapter != null

    val isNfcEnabled: Boolean
        get() = nfcAdapter?.isEnabled == true

    private val pendingIntent: PendingIntent by lazy {
        PendingIntent.getActivity(
            activity,
            0,
            Intent(activity, activity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                PendingIntent.FLAG_MUTABLE
            } else {
                0
            }
        )
    }

    private val intentFilters: Array<IntentFilter> by lazy {
        arrayOf(
            IntentFilter(NfcAdapter.ACTION_NDEF_DISCOVERED).apply {
                try {
                    addDataType("*/*")
                } catch (e: IntentFilter.MalformedMimeTypeException) {
                    throw RuntimeException("Failed to add data type", e)
                }
            },
            IntentFilter(NfcAdapter.ACTION_TAG_DISCOVERED),
            IntentFilter(NfcAdapter.ACTION_TECH_DISCOVERED)
        )
    }

    private val techLists: Array<Array<String>> by lazy {
        arrayOf(
            arrayOf(Ndef::class.java.name),
            arrayOf(NfcA::class.java.name),
            arrayOf(MifareClassic::class.java.name),
            arrayOf(MifareUltralight::class.java.name)
        )
    }

    fun enableForegroundDispatch() {
        nfcAdapter?.enableForegroundDispatch(activity, pendingIntent, intentFilters, techLists)
    }

    fun disableForegroundDispatch() {
        nfcAdapter?.disableForegroundDispatch(activity)
    }

    fun processIntent(intent: Intent): NfcTagInfo? {
        if (intent.action !in listOf(
                NfcAdapter.ACTION_NDEF_DISCOVERED,
                NfcAdapter.ACTION_TAG_DISCOVERED,
                NfcAdapter.ACTION_TECH_DISCOVERED
            )) {
            return null
        }

        val tag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(NfcAdapter.EXTRA_TAG, Tag::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(NfcAdapter.EXTRA_TAG)
        } ?: return null

        val tagInfo = parseTag(tag)
        _tagInfo.value = tagInfo
        return tagInfo
    }

    private fun parseTag(tag: Tag): NfcTagInfo {
        val id = bytesToHex(tag.id)
        val techList = tag.techList.map { it.substringAfterLast('.') }
        val type = detectTagType(tag)
        val content = readTagContent(tag)

        return NfcTagInfo(
            id = id,
            type = type,
            techList = techList,
            content = content
        )
    }

    private fun detectTagType(tag: Tag): String {
        return when {
            tag.techList.contains(MifareClassic::class.java.name) -> {
                val mfc = MifareClassic.get(tag)
                when (mfc?.type) {
                    MifareClassic.TYPE_CLASSIC -> "MIFARE Classic"
                    MifareClassic.TYPE_PLUS -> "MIFARE Plus"
                    MifareClassic.TYPE_PRO -> "MIFARE Pro"
                    else -> "MIFARE Classic"
                }
            }
            tag.techList.contains(MifareUltralight::class.java.name) -> {
                val mfu = MifareUltralight.get(tag)
                when (mfu?.type) {
                    MifareUltralight.TYPE_ULTRALIGHT -> "MIFARE Ultralight"
                    MifareUltralight.TYPE_ULTRALIGHT_C -> "MIFARE Ultralight C"
                    else -> "MIFARE Ultralight"
                }
            }
            tag.techList.contains(Ndef::class.java.name) -> {
                val ndef = Ndef.get(tag)
                ndef?.type?.let { type ->
                    when {
                        type.contains("1") -> "NFC Forum Type 1 (NTAG)"
                        type.contains("2") -> "NFC Forum Type 2 (NTAG)"
                        type.contains("3") -> "NFC Forum Type 3 (FeliCa)"
                        type.contains("4") -> "NFC Forum Type 4 (ISO-DEP)"
                        else -> "NDEF ($type)"
                    }
                } ?: "NDEF"
            }
            tag.techList.contains(NfcA::class.java.name) -> "NFC-A (ISO 14443-3A)"
            else -> "Unknown NFC"
        }
    }

    private fun readTagContent(tag: Tag): String? {
        try {
            // Try to read NDEF content
            Ndef.get(tag)?.let { ndef ->
                ndef.connect()
                val ndefMessage = ndef.ndefMessage
                ndef.close()

                if (ndefMessage != null) {
                    return parseNdefMessage(ndefMessage)
                }
            }

            // For non-NDEF tags, just return the ID
            return null
        } catch (e: Exception) {
            return null
        }
    }

    private fun parseNdefMessage(message: NdefMessage): String? {
        for (record in message.records) {
            // Text record
            if (record.tnf == android.nfc.NdefRecord.TNF_WELL_KNOWN &&
                record.type.contentEquals("T".toByteArray())) {
                val payload = record.payload
                val languageCodeLength = payload[0].toInt() and 0x3F
                return String(payload, languageCodeLength + 1, payload.size - languageCodeLength - 1, Charsets.UTF_8)
            }

            // URI record
            if (record.tnf == android.nfc.NdefRecord.TNF_WELL_KNOWN &&
                record.type.contentEquals("U".toByteArray())) {
                val prefixes = arrayOf(
                    "", "http://www.", "https://www.", "http://", "https://",
                    "tel:", "mailto:", "ftp://anonymous:anonymous@", "ftp://ftp.",
                    "ftps://", "sftp://", "smb://", "nfs://", "ftp://", "dav://",
                    "news:", "telnet://", "imap:", "rtsp://", "urn:", "pop:",
                    "sip:", "sips:", "tftp:", "btspp://", "btl2cap://", "btgoep://",
                    "tcpobex://", "irdaobex://", "file://", "urn:epc:id:", "urn:epc:tag:",
                    "urn:epc:pat:", "urn:epc:raw:", "urn:epc:", "urn:nfc:"
                )
                val payload = record.payload
                val prefix = prefixes.getOrElse(payload[0].toInt()) { "" }
                val uri = String(payload, 1, payload.size - 1, Charsets.UTF_8)
                return prefix + uri
            }
        }

        return null
    }

    fun clearTagInfo() {
        _tagInfo.value = null
    }

    companion object {
        private fun bytesToHex(bytes: ByteArray): String {
            return bytes.joinToString("") { "%02X".format(it) }
        }
    }
}
