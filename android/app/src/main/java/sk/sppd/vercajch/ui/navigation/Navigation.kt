package sk.sppd.vercajch.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import sk.sppd.vercajch.ui.screens.about.AboutScreen
import sk.sppd.vercajch.ui.screens.auth.LoginScreen
import sk.sppd.vercajch.ui.screens.auth.LoginViewModel
import sk.sppd.vercajch.ui.screens.equipment.EquipmentDetailScreen
import sk.sppd.vercajch.ui.screens.equipment.EquipmentListScreen
import sk.sppd.vercajch.ui.screens.home.HomeScreen
import sk.sppd.vercajch.ui.screens.location.LocationScreen
import sk.sppd.vercajch.ui.screens.onboarding.OnboardingScreen
import sk.sppd.vercajch.ui.screens.profile.ProfileScreen
import sk.sppd.vercajch.ui.screens.scanner.ScannerScreen
import sk.sppd.vercajch.ui.screens.transfers.CreateTransferRequestScreen
import sk.sppd.vercajch.ui.screens.transfers.TransfersScreen
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Home : Screen("home")
    object Scanner : Screen("scanner")
    object EquipmentList : Screen("equipment")
    object EquipmentDetail : Screen("equipment/{id}") {
        fun createRoute(id: String) = "equipment/$id"
    }
    object Onboarding : Screen("onboarding?tagValue={tagValue}") {
        fun createRoute(tagValue: String? = null) =
            if (tagValue != null) "onboarding?tagValue=$tagValue" else "onboarding"
    }
    object Transfers : Screen("transfers")
    object CreateTransferRequest : Screen("transfers/create?equipmentId={equipmentId}&equipmentName={equipmentName}&holderId={holderId}&holderName={holderName}") {
        fun createRoute(
            equipmentId: String,
            equipmentName: String,
            holderId: String?,
            holderName: String?
        ): String {
            val encodedName = URLEncoder.encode(equipmentName, StandardCharsets.UTF_8.toString())
            val encodedHolderName = holderName?.let { URLEncoder.encode(it, StandardCharsets.UTF_8.toString()) } ?: ""
            return "transfers/create?equipmentId=$equipmentId&equipmentName=$encodedName&holderId=${holderId ?: ""}&holderName=$encodedHolderName"
        }
    }
    object Profile : Screen("profile")
    object About : Screen("about")
    object Location : Screen("location")
}

@Composable
fun VercajchNavHost() {
    val navController = rememberNavController()
    val loginViewModel: LoginViewModel = hiltViewModel()
    val isLoggedIn by loginViewModel.isLoggedIn.collectAsState(initial = false)

    NavHost(
        navController = navController,
        startDestination = if (isLoggedIn) Screen.Home.route else Screen.Login.route
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToScanner = {
                    navController.navigate(Screen.Scanner.route)
                },
                onNavigateToEquipment = {
                    navController.navigate(Screen.EquipmentList.route)
                },
                onNavigateToTransfers = {
                    navController.navigate(Screen.Transfers.route)
                },
                onNavigateToLocation = {
                    navController.navigate(Screen.Location.route)
                },
                onNavigateToProfile = {
                    navController.navigate(Screen.Profile.route)
                },
                onNavigateToAbout = {
                    navController.navigate(Screen.About.route)
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Scanner.route) {
            ScannerScreen(
                onEquipmentFound = { id ->
                    navController.navigate(Screen.EquipmentDetail.createRoute(id)) {
                        popUpTo(Screen.Scanner.route) { inclusive = true }
                    }
                },
                onNewEquipment = { tagValue ->
                    navController.navigate(Screen.Onboarding.createRoute(tagValue)) {
                        popUpTo(Screen.Scanner.route) { inclusive = true }
                    }
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.EquipmentList.route) {
            EquipmentListScreen(
                onEquipmentClick = { id ->
                    navController.navigate(Screen.EquipmentDetail.createRoute(id))
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.EquipmentDetail.route,
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id") ?: return@composable
            EquipmentDetailScreen(
                equipmentId = id,
                onBack = { navController.popBackStack() },
                onRequestTransfer = { equipmentId, equipmentName, holderId, holderName ->
                    navController.navigate(
                        Screen.CreateTransferRequest.createRoute(
                            equipmentId = equipmentId,
                            equipmentName = equipmentName,
                            holderId = holderId,
                            holderName = holderName
                        )
                    )
                }
            )
        }

        composable(
            route = Screen.Onboarding.route,
            arguments = listOf(
                navArgument("tagValue") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val tagValue = backStackEntry.arguments?.getString("tagValue")
            OnboardingScreen(
                initialTagValue = tagValue,
                onComplete = { equipmentId ->
                    navController.navigate(Screen.EquipmentDetail.createRoute(equipmentId)) {
                        popUpTo(Screen.Home.route)
                    }
                },
                onCancel = { navController.popBackStack() }
            )
        }

        composable(Screen.Transfers.route) {
            TransfersScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.CreateTransferRequest.route,
            arguments = listOf(
                navArgument("equipmentId") { type = NavType.StringType },
                navArgument("equipmentName") { type = NavType.StringType },
                navArgument("holderId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                },
                navArgument("holderName") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val equipmentId = backStackEntry.arguments?.getString("equipmentId")
            val equipmentName = backStackEntry.arguments?.getString("equipmentName")?.let {
                URLDecoder.decode(it, StandardCharsets.UTF_8.toString())
            }
            val holderId = backStackEntry.arguments?.getString("holderId")?.ifBlank { null }
            val holderName = backStackEntry.arguments?.getString("holderName")?.let {
                if (it.isNotBlank()) URLDecoder.decode(it, StandardCharsets.UTF_8.toString()) else null
            }

            CreateTransferRequestScreen(
                equipmentId = equipmentId,
                equipmentName = equipmentName,
                holderId = holderId,
                holderName = holderName,
                onBack = { navController.popBackStack() },
                onSuccess = {
                    navController.navigate(Screen.Transfers.route) {
                        popUpTo(Screen.Home.route)
                    }
                }
            )
        }

        composable(Screen.Profile.route) {
            ProfileScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.About.route) {
            AboutScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Location.route) {
            LocationScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}
