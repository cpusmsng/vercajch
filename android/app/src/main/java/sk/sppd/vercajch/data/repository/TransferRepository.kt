package sk.sppd.vercajch.data.repository

import sk.sppd.vercajch.data.api.ApiService
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

    suspend fun createDirectRequest(
        equipmentId: String,
        holderId: String,
        message: String?
    ): Result<TransferRequest> {
        return try {
            val body = mutableMapOf(
                "equipment_id" to equipmentId,
                "holder_id" to holderId
            )
            message?.let { body["message"] = it }
            val response = apiService.createDirectTransferRequest(body)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createBroadcastRequest(
        categoryId: String,
        message: String
    ): Result<TransferRequest> {
        return try {
            val response = apiService.createBroadcastTransferRequest(
                mapOf(
                    "category_id" to categoryId,
                    "message" to message
                )
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun acceptRequest(requestId: String): Result<Unit> {
        return try {
            apiService.acceptTransferRequest(requestId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun rejectRequest(requestId: String): Result<Unit> {
        return try {
            apiService.rejectTransferRequest(requestId)
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
