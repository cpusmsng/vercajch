package sk.sppd.vercajch.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import sk.sppd.vercajch.data.model.User
import javax.inject.Inject
import javax.inject.Singleton

private val Context.authDataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

@Singleton
class AuthPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val json = Json { ignoreUnknownKeys = true }

    companion object {
        private val ACCESS_TOKEN = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
        private val USER_DATA = stringPreferencesKey("user_data")
    }

    suspend fun saveAuthData(accessToken: String, refreshToken: String, user: User) {
        context.authDataStore.edit { preferences ->
            preferences[ACCESS_TOKEN] = accessToken
            preferences[REFRESH_TOKEN] = refreshToken
            preferences[USER_DATA] = json.encodeToString(user)
        }
    }

    suspend fun getAccessToken(): String? {
        return context.authDataStore.data.first()[ACCESS_TOKEN]
    }

    suspend fun getRefreshToken(): String? {
        return context.authDataStore.data.first()[REFRESH_TOKEN]
    }

    fun getUserFlow(): Flow<User?> {
        return context.authDataStore.data.map { preferences ->
            preferences[USER_DATA]?.let {
                try {
                    json.decodeFromString<User>(it)
                } catch (e: Exception) {
                    null
                }
            }
        }
    }

    suspend fun getUser(): User? {
        return getUserFlow().first()
    }

    val isLoggedIn: Flow<Boolean> = context.authDataStore.data.map { preferences ->
        preferences[ACCESS_TOKEN] != null
    }

    suspend fun clearAuth() {
        context.authDataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
