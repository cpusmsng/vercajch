package sk.sppd.vercajch.data.repository

import sk.sppd.vercajch.data.api.ApiService
import sk.sppd.vercajch.data.model.CreateTransferRequest
import sk.sppd.vercajch.data.model.TransferOffer
import sk.sppd.vercajch.data.model.TransferRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TransferRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getSentRequests(): Result<List<TransferRequest>> {
        return try {
            val response = apiService.getSentTransferRequests()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getReceivedRequests(): Result<List<TransferRequest>> {
        return try {
            val response = apiService.getReceivedTransferRequests()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createRequest(
        requestType: String,
        equipmentId: String? = null,
        categoryId: String? = null,
        holderId: String? = null,
        neededFrom: String? = null,
        neededUntil: String? = null,
        message: String? = null
    ): Result<TransferRequest> {
        return try {
            val request = CreateTransferRequest(
                requestType = requestType,
                equipmentId = equipmentId,
                categoryId = categoryId,
                holderId = holderId,
                neededFrom = neededFrom,
                neededUntil = neededUntil,
                message = message
            )
            val response = apiService.createTransferRequest(request)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun acceptRequest(requestId: String): Result<Unit> {
        return try {
            apiService.respondToTransferRequest(requestId, mapOf("action" to "accept"))
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun rejectRequest(requestId: String, reason: String? = null): Result<Unit> {
        return try {
            val body = mutableMapOf("action" to "reject")
            reason?.let { body["rejection_reason"] = it }
            apiService.respondToTransferRequest(requestId, body)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun cancelRequest(requestId: String): Result<Unit> {
        return try {
            apiService.cancelTransferRequest(requestId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getOffers(requestId: String): Result<List<TransferOffer>> {
        return try {
            val response = apiService.getTransferOffers(requestId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createOffer(
        requestId: String,
        equipmentId: String
    ): Result<TransferOffer> {
        return try {
            val response = apiService.createTransferOffer(
                mapOf(
                    "request_id" to requestId,
                    "equipment_id" to equipmentId
                )
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun acceptOffer(offerId: String): Result<Unit> {
        return try {
            apiService.acceptTransferOffer(offerId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun confirmTransfer(
        requestId: String,
        confirmationType: String
    ): Result<Unit> {
        return try {
            apiService.confirmTransfer(
                mapOf(
                    "request_id" to requestId,
                    "confirmation_type" to confirmationType
                )
            )
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
