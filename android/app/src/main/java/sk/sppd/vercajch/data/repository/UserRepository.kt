package sk.sppd.vercajch.data.repository

import sk.sppd.vercajch.data.api.ApiService
import sk.sppd.vercajch.data.model.User
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun updateProfile(fullName: String, phone: String): Result<User> {
        return try {
            val response = apiService.updateProfile(
                mapOf(
                    "full_name" to fullName,
                    "phone" to phone
                )
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun changePassword(currentPassword: String, newPassword: String): Result<Unit> {
        return try {
            apiService.changePassword(
                mapOf(
                    "current_password" to currentPassword,
                    "new_password" to newPassword
                )
            )
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
