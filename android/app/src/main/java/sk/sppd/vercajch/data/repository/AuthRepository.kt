package sk.sppd.vercajch.data.repository

import kotlinx.coroutines.flow.Flow
import sk.sppd.vercajch.data.api.ApiService
import sk.sppd.vercajch.data.model.LoginRequest
import sk.sppd.vercajch.data.model.User
import sk.sppd.vercajch.data.preferences.AuthPreferences
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val authPreferences: AuthPreferences
) {
    val isLoggedIn: Flow<Boolean> = authPreferences.isLoggedIn
    val currentUser: Flow<User?> = authPreferences.getUserFlow()

    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = apiService.login(LoginRequest(email, password))
            authPreferences.saveAuthData(
                response.accessToken,
                response.refreshToken,
                response.user
            )
            Result.success(response.user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        authPreferences.clearAuth()
    }

    suspend fun getCurrentUser(): User? {
        return try {
            val user = apiService.getCurrentUser()
            authPreferences.getAccessToken()?.let { token ->
                authPreferences.getRefreshToken()?.let { refresh ->
                    authPreferences.saveAuthData(token, refresh, user)
                }
            }
            user
        } catch (e: Exception) {
            null
        }
    }
}
