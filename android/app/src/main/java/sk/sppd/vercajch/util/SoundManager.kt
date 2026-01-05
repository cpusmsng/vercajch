package sk.sppd.vercajch.util

import android.content.Context
import android.media.AudioAttributes
import android.media.SoundPool
import android.media.ToneGenerator
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages sound and haptic feedback for scanning operations
 */
@Singleton
class SoundManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val toneGenerator: ToneGenerator by lazy {
        ToneGenerator(android.media.AudioManager.STREAM_NOTIFICATION, 100)
    }

    private val vibrator: Vibrator by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
    }

    /**
     * Play success sound and vibration for successful scan
     */
    fun playSuccessSound() {
        try {
            // Play a pleasant confirmation tone
            toneGenerator.startTone(ToneGenerator.TONE_PROP_ACK, 150)

            // Short vibration
            vibrateShort()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Play error sound for failed scan
     */
    fun playErrorSound() {
        try {
            // Play error tone
            toneGenerator.startTone(ToneGenerator.TONE_PROP_NACK, 200)

            // Double vibration for error
            vibrateError()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Play NFC detection sound
     */
    fun playNfcSound() {
        try {
            // Different tone for NFC
            toneGenerator.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 100)
            vibrateShort()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Short vibration for success
     */
    private fun vibrateShort() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(50)
        }
    }

    /**
     * Double vibration pattern for errors
     */
    private fun vibrateError() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val pattern = longArrayOf(0, 100, 100, 100)
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(longArrayOf(0, 100, 100, 100), -1)
        }
    }

    fun release() {
        try {
            toneGenerator.release()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
