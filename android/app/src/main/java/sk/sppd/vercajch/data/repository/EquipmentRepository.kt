package sk.sppd.vercajch.data.repository

import sk.sppd.vercajch.data.api.ApiService
import sk.sppd.vercajch.data.model.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class EquipmentRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getEquipment(
        page: Int = 1,
        search: String? = null,
        categoryId: String? = null,
        status: String? = null
    ): Result<PaginatedResponse<Equipment>> {
        return try {
            val response = apiService.getEquipment(page, 20, search, categoryId, status)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getEquipmentById(id: String): Result<Equipment> {
        return try {
            val response = apiService.getEquipmentById(id)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun lookupTag(value: String): Result<TagLookupResponse> {
        return try {
            val response = apiService.lookupTag(value)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getCategories()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getLocations(): Result<List<Location>> {
        return try {
            val response = apiService.getLocations()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getManufacturers(): Result<List<Manufacturer>> {
        return try {
            val response = apiService.getManufacturers()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getAccessoryTypes(categoryId: String): Result<List<AccessoryType>> {
        return try {
            val response = apiService.getAccessoryTypes(categoryId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
