package sk.sppd.vercajch.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

val Primary = Color(0xFF6366F1)
val PrimaryDark = Color(0xFF4F46E5)
val PrimaryLight = Color(0xFF818CF8)
val Secondary = Color(0xFF10B981)
val Background = Color(0xFFF9FAFB)
val Surface = Color(0xFFFFFFFF)
val Error = Color(0xFFEF4444)
val OnPrimary = Color.White
val OnSecondary = Color.White
val OnBackground = Color(0xFF111827)
val OnSurface = Color(0xFF111827)
val OnError = Color.White

private val LightColorScheme = lightColorScheme(
    primary = Primary,
    onPrimary = OnPrimary,
    primaryContainer = PrimaryLight,
    onPrimaryContainer = PrimaryDark,
    secondary = Secondary,
    onSecondary = OnSecondary,
    background = Background,
    onBackground = OnBackground,
    surface = Surface,
    onSurface = OnSurface,
    error = Error,
    onError = OnError,
)

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryLight,
    onPrimary = Color.Black,
    primaryContainer = PrimaryDark,
    onPrimaryContainer = PrimaryLight,
    secondary = Secondary,
    onSecondary = Color.Black,
    background = Color(0xFF111827),
    onBackground = Color.White,
    surface = Color(0xFF1F2937),
    onSurface = Color.White,
    error = Color(0xFFF87171),
    onError = Color.Black,
)

@Composable
fun VercajchTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
