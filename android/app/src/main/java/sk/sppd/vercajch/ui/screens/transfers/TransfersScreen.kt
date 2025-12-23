package sk.sppd.vercajch.ui.screens.transfers

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
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import sk.sppd.vercajch.data.model.TransferRequest

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TransfersScreen(
    onBack: () -> Unit,
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
                Column {
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

            if (isReceived) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Od: ${request.requester?.fullName ?: "Neznámy"}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Komu: ${request.holder?.fullName ?: "Neznámy"}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
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
