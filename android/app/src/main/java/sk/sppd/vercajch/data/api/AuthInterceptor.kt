package sk.sppd.vercajch.data.api

import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import sk.sppd.vercajch.data.preferences.AuthPreferences
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthInterceptor @Inject constructor(
    private val authPreferences: AuthPreferences
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Skip auth header for login and refresh endpoints
        if (request.url.encodedPath.contains("auth/login") ||
            request.url.encodedPath.contains("auth/refresh")) {
            return chain.proceed(request)
        }

        val token = runBlocking { authPreferences.getAccessToken() }

        return if (token != null) {
            val authenticatedRequest = request.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
            chain.proceed(authenticatedRequest)
        } else {
            chain.proceed(request)
        }
    }
}
