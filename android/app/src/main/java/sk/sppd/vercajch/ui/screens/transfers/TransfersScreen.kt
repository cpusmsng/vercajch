package sk.sppd.vercajch.ui.screens.transfers

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import sk.sppd.vercajch.data.model.TransferRequest
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TransfersScreen(
    onBack: () -> Unit,
    onCreateTransfer: () -> Unit = {},
    viewModel: TransfersViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedTab by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        viewModel.loadTransfers()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Transfery") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Späť")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = onCreateTransfer,
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Nový transfer")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("Prijaté")
                            if (uiState.receivedRequests.isNotEmpty()) {
                                Spacer(modifier = Modifier.width(4.dp))
                                Badge { Text("${uiState.receivedRequests.size}") }
                            }
                        }
                    }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Odoslané") }
                )
            }

            when {
                uiState.isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }

                uiState.error != null -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = uiState.error!!,
                                color = MaterialTheme.colorScheme.error
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(onClick = { viewModel.loadTransfers() }) {
                                Text("Skúsiť znova")
                            }
                        }
                    }
                }

                else -> {
                    val requests = if (selectedTab == 0) {
                        uiState.receivedRequests
                    } else {
                        uiState.sentRequests
                    }

                    if (requests.isEmpty()) {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(
                                    Icons.Default.SwapHoriz,
                                    contentDescription = null,
                                    modifier = Modifier.size(48.dp),
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    text = if (selectedTab == 0) {
                                        "Žiadne prijaté požiadavky"
                                    } else {
                                        "Žiadne odoslané požiadavky"
                                    },
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            items(requests) { request ->
                                TransferRequestCard(
                                    request = request,
                                    isReceived = selectedTab == 0,
                                    onAccept = { viewModel.acceptRequest(request.id) },
                                    onReject = { viewModel.rejectRequest(request.id) },
                                    onCancel = { viewModel.cancelRequest(request.id) }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TransferRequestCard(
    request: TransferRequest,
    isReceived: Boolean,
    onAccept: () -> Unit,
    onReject: () -> Unit,
    onCancel: () -> Unit
) {
    val context = LocalContext.current

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = request.equipment?.name ?: "Neznáme náradie",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = request.equipment?.internalCode ?: "",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                TransferStatusChip(status = request.status)
            }

            // Person info with contact options
            val person = if (isReceived) request.requester else request.holder
            val personLabel = if (isReceived) "Od" else "Komu"

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "$personLabel: ${person?.fullName ?: "Neznámy"}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                // Contact buttons
                Row {
                    person?.phone?.let { phone ->
                        IconButton(
                            onClick = {
                                val intent = Intent(Intent.ACTION_DIAL).apply {
                                    data = Uri.parse("tel:$phone")
                                }
                                context.startActivity(intent)
                            },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                Icons.Default.Phone,
                                contentDescription = "Zavolať",
                                modifier = Modifier.size(18.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                    person?.email?.let { email ->
                        IconButton(
                            onClick = {
                                val intent = Intent(Intent.ACTION_SENDTO).apply {
                                    data = Uri.parse("mailto:$email")
                                }
                                context.startActivity(intent)
                            },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                Icons.Default.Email,
                                contentDescription = "Napísať email",
                                modifier = Modifier.size(18.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
            }

            // Borrow duration info
            request.neededUntil?.let { neededUntil ->
                BorrowDurationInfo(neededUntil = neededUntil)
            }

            if (!request.message.isNullOrBlank()) {
                Text(
                    text = request.message,
                    style = MaterialTheme.typography.bodyMedium
                )
            }

            if (request.status == "pending") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    if (isReceived) {
                        OutlinedButton(
                            onClick = onReject,
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = MaterialTheme.colorScheme.error
                            )
                        ) {
                            Text("Odmietnuť")
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(onClick = onAccept) {
                            Text("Prijať")
                        }
                    } else {
                        OutlinedButton(
                            onClick = onCancel,
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = MaterialTheme.colorScheme.error
                            )
                        ) {
                            Text("Zrušiť")
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BorrowDurationInfo(neededUntil: String) {
    val formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME
    val displayFormatter = DateTimeFormatter.ofPattern("d.M.yyyy")

    val deadline = try {
        LocalDateTime.parse(neededUntil, formatter)
    } catch (e: Exception) {
        try {
            LocalDateTime.parse(neededUntil.replace("Z", ""), formatter)
        } catch (e2: Exception) {
            null
        }
    }

    if (deadline != null) {
        val now = LocalDateTime.now()
        val daysRemaining = ChronoUnit.DAYS.between(now, deadline)
        val hoursRemaining = ChronoUnit.HOURS.between(now, deadline)

        val (text, isWarning) = when {
            daysRemaining < 0 -> "Po termíne!" to true
            daysRemaining == 0L && hoursRemaining > 0 -> "Zostáva $hoursRemaining hodín" to true
            daysRemaining == 0L -> "Dnes je posledný deň!" to true
            daysRemaining == 1L -> "Zostáva 1 deň" to false
            daysRemaining <= 3 -> "Zostávajú $daysRemaining dni" to false
            else -> "Potrebné do: ${deadline.format(displayFormatter)}" to false
        }

        val backgroundColor = if (isWarning) {
            MaterialTheme.colorScheme.errorContainer
        } else {
            MaterialTheme.colorScheme.tertiaryContainer
        }

        val contentColor = if (isWarning) {
            MaterialTheme.colorScheme.error
        } else {
            MaterialTheme.colorScheme.tertiary
        }

        Surface(
            color = backgroundColor,
            shape = MaterialTheme.shapes.small,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    if (isWarning) Icons.Default.Warning else Icons.Default.Schedule,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                    tint = contentColor
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = text,
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = if (isWarning) FontWeight.Bold else FontWeight.Normal,
                    color = contentColor
                )
            }
        }
    }
}

@Composable
fun TransferStatusChip(status: String) {
    val (label, color) = when (status) {
        "pending" -> "Čaká" to MaterialTheme.colorScheme.tertiary
        "accepted" -> "Prijaté" to MaterialTheme.colorScheme.primary
        "rejected" -> "Odmietnuté" to MaterialTheme.colorScheme.error
        "cancelled" -> "Zrušené" to MaterialTheme.colorScheme.outline
        "completed" -> "Dokončené" to MaterialTheme.colorScheme.primary
        "requires_approval" -> "Čaká na schválenie" to MaterialTheme.colorScheme.tertiary
        else -> status to MaterialTheme.colorScheme.outline
    }

    Surface(
        color = color.copy(alpha = 0.1f),
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = label,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}
