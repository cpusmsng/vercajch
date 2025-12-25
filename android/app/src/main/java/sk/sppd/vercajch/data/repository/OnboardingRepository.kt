package sk.sppd.vercajch.data.repository

import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import sk.sppd.vercajch.data.api.ApiService
import sk.sppd.vercajch.data.model.*
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OnboardingRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun startOnboarding(): Result<OnboardingSession> {
        return try {
            val response = apiService.startOnboarding()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getSession(sessionId: String): Result<OnboardingSession> {
        return try {
            val response = apiService.getOnboardingSession(sessionId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun submitStep(
        sessionId: String,
        step: Int,
        data: Map<String, Any?>
    ): Result<OnboardingSession> {
        return try {
            val response = apiService.submitOnboardingStep(sessionId, step, data)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun uploadPhoto(sessionId: String, file: File): Result<String> {
        return try {
            val requestBody = file.asRequestBody("image/*".toMediaTypeOrNull())
            val part = MultipartBody.Part.createFormData("file", file.name, requestBody)
            val response = apiService.uploadOnboardingPhoto(sessionId, part)
            Result.success(response["file_id"] ?: response["url"] ?: "")
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun complete(sessionId: String): Result<Equipment> {
        return try {
            val response = apiService.completeOnboarding(sessionId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun cancel(sessionId: String): Result<Unit> {
        return try {
            apiService.cancelOnboarding(sessionId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
