package sk.sppd.vercajch.data.api

import okhttp3.MultipartBody
import retrofit2.http.*
import sk.sppd.vercajch.data.model.*

interface ApiService {
    // Auth
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @POST("auth/refresh")
    suspend fun refreshToken(@Header("Authorization") refreshToken: String): LoginResponse

    @GET("auth/me")
    suspend fun getCurrentUser(): User

    @PUT("auth/password")
    suspend fun changePassword(@Body body: Map<String, String>): Map<String, String>

    // User profile
    @PUT("users/me")
    suspend fun updateProfile(@Body body: Map<String, String>): User

    // Equipment
    @GET("equipment")
    suspend fun getEquipment(
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 20,
        @Query("search") search: String? = null,
        @Query("category_id") categoryId: String? = null,
        @Query("status") status: String? = null
    ): PaginatedResponse<Equipment>

    @GET("equipment/{id}")
    suspend fun getEquipmentById(@Path("id") id: String): Equipment

    @GET("equipment/{id}/history")
    suspend fun getEquipmentHistory(@Path("id") id: String): Map<String, Any>

    @PUT("equipment/{id}")
    suspend fun updateEquipment(
        @Path("id") id: String,
        @Body update: EquipmentUpdate
    ): retrofit2.Response<Equipment>

    // Tags
    @GET("tags/lookup")
    suspend fun lookupTag(@Query("value") value: String): TagLookupResponse

    @POST("tags/lookup")
    suspend fun lookupTagPost(@Body body: Map<String, String>): TagLookupResponse

    // Categories
    @GET("categories")
    suspend fun getCategories(): List<Category>

    // Locations
    @GET("locations")
    suspend fun getLocations(): List<Location>

    // Manufacturers
    @GET("manufacturers")
    suspend fun getManufacturers(): List<Manufacturer>

    @GET("manufacturers/{id}/models")
    suspend fun getModels(@Path("id") manufacturerId: String): List<Map<String, Any>>

    // Accessory Types
    @GET("categories/{id}/accessory-types")
    suspend fun getAccessoryTypes(@Path("id") categoryId: String): List<AccessoryType>

    // Onboarding
    @POST("onboarding/start")
    suspend fun startOnboarding(): OnboardingSession

    @GET("onboarding/{sessionId}")
    suspend fun getOnboardingSession(@Path("sessionId") sessionId: String): OnboardingSession

    @POST("onboarding/{sessionId}/step/{step}")
    suspend fun submitOnboardingStep(
        @Path("sessionId") sessionId: String,
        @Path("step") step: Int,
        @Body data: Map<String, @JvmSuppressWildcards Any?>
    ): OnboardingSession

    @Multipart
    @POST("onboarding/{sessionId}/upload")
    suspend fun uploadOnboardingPhoto(
        @Path("sessionId") sessionId: String,
        @Part file: MultipartBody.Part
    ): Map<String, String>

    @POST("onboarding/{sessionId}/complete")
    suspend fun completeOnboarding(@Path("sessionId") sessionId: String): Equipment

    @DELETE("onboarding/{sessionId}")
    suspend fun cancelOnboarding(@Path("sessionId") sessionId: String)

    // Transfers
    @GET("transfers/requests/sent")
    suspend fun getSentTransferRequests(): List<TransferRequest>

    @GET("transfers/requests/received")
    suspend fun getReceivedTransferRequests(): List<TransferRequest>

    @POST("transfers/requests")
    suspend fun createTransferRequest(@Body body: CreateTransferRequest): TransferRequest

    @POST("transfers/requests/{id}/respond")
    suspend fun respondToTransferRequest(
        @Path("id") id: String,
        @Body body: Map<String, String>
    ): Map<String, Any>

    @POST("transfers/requests/{id}/cancel")
    suspend fun cancelTransferRequest(@Path("id") id: String): Map<String, Any>

    // Users - for finding holder by equipment
    @GET("users")
    suspend fun getUsers(
        @Query("search") search: String? = null,
        @Query("department_id") departmentId: String? = null
    ): PaginatedResponse<User>

    @GET("transfers/offers/{requestId}")
    suspend fun getTransferOffers(@Path("requestId") requestId: String): List<TransferOffer>

    @POST("transfers/offer")
    suspend fun createTransferOffer(@Body body: Map<String, String>): TransferOffer

    @POST("transfers/offer/{id}/accept")
    suspend fun acceptTransferOffer(@Path("id") id: String): Map<String, Any>

    @POST("transfers/confirm")
    suspend fun confirmTransfer(@Body body: Map<String, String>): Map<String, Any>

    // Calibrations
    @GET("calibrations/equipment/{id}")
    suspend fun getEquipmentCalibrations(@Path("id") equipmentId: String): List<Calibration>

    @POST("calibrations")
    suspend fun createCalibration(@Body body: Map<String, @JvmSuppressWildcards Any?>): Calibration
}
