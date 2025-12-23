package sk.sppd.vercajch.ui.screens.equipment

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import sk.sppd.vercajch.data.model.Equipment

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EquipmentDetailScreen(
    equipmentId: String,
    onBack: () -> Unit,
    onRequestTransfer: (String) -> Unit,
    viewModel: EquipmentDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(equipmentId) {
        viewModel.loadEquipment(equipmentId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Detail náradia") },
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
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            uiState.error != null -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = uiState.error!!,
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }

            uiState.equipment != null -> {
                EquipmentDetailContent(
                    equipment = uiState.equipment!!,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    onRequestTransfer = { onRequestTransfer(equipmentId) }
                )
            }
        }
    }
}

@Composable
fun EquipmentDetailContent(
    equipment: Equipment,
    modifier: Modifier = Modifier,
    onRequestTransfer: () -> Unit
) {
    Column(
        modifier = modifier
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Photo
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
        ) {
            if (equipment.photoUrl != null) {
                AsyncImage(
                    model = equipment.photoUrl,
                    contentDescription = equipment.name,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            } else {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.Image,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        // Basic Info
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = equipment.name,
                        style = MaterialTheme.typography.headlineSmall
                    )
                    StatusChip(status = equipment.status)
                }

                Text(
                    text = equipment.internalCode,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                if (equipment.description != null) {
                    Text(
                        text = equipment.description,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        // Details
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Detaily",
                    style = MaterialTheme.typography.titleMedium
                )

                DetailRow(
                    icon = Icons.Default.Category,
                    label = "Kategória",
                    value = equipment.category?.name ?: "-"
                )

                if (equipment.serialNumber != null) {
                    DetailRow(
                        icon = Icons.Default.Tag,
                        label = "Sériové číslo",
                        value = equipment.serialNumber
                    )
                }

                if (equipment.manufacturer != null) {
                    DetailRow(
                        icon = Icons.Default.Business,
                        label = "Výrobca",
                        value = equipment.manufacturer
                    )
                }

                if (equipment.modelName != null) {
                    DetailRow(
                        icon = Icons.Default.Devices,
                        label = "Model",
                        value = equipment.modelName
                    )
                }

                DetailRow(
                    icon = Icons.Default.Build,
                    label = "Stav",
                    value = when (equipment.condition) {
                        "new" -> "Nové"
                        "good" -> "Dobré"
                        "fair" -> "Opotrebované"
                        "poor" -> "Zlé"
                        "broken" -> "Poškodené"
                        else -> equipment.condition
                    }
                )
            }
        }

        // Location & Holder
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Umiestnenie",
                    style = MaterialTheme.typography.titleMedium
                )

                DetailRow(
                    icon = Icons.Default.LocationOn,
                    label = "Lokácia",
                    value = equipment.currentLocation?.name ?: "Neurčená"
                )

                DetailRow(
                    icon = Icons.Default.Person,
                    label = "Držiteľ",
                    value = equipment.currentHolder?.fullName ?: "Nikto"
                )
            }
        }

        // Calibration
        if (equipment.requiresCalibration) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Kalibrácia",
                        style = MaterialTheme.typography.titleMedium
                    )

                    DetailRow(
                        icon = Icons.Default.Speed,
                        label = "Interval",
                        value = "${equipment.calibrationIntervalDays ?: 0} dní"
                    )

                    if (equipment.lastCalibrationDate != null) {
                        DetailRow(
                            icon = Icons.Default.History,
                            label = "Posledná",
                            value = equipment.lastCalibrationDate
                        )
                    }

                    if (equipment.nextCalibrationDate != null) {
                        DetailRow(
                            icon = Icons.Default.Event,
                            label = "Nasledujúca",
                            value = equipment.nextCalibrationDate
                        )
                    }

                    if (equipment.calibrationStatus != null) {
                        val (statusLabel, statusColor) = when (equipment.calibrationStatus) {
                            "valid" -> "Platná" to MaterialTheme.colorScheme.primary
                            "expiring" -> "Končí" to MaterialTheme.colorScheme.error.copy(alpha = 0.7f)
                            "expired" -> "Expirovaná" to MaterialTheme.colorScheme.error
                            else -> equipment.calibrationStatus to MaterialTheme.colorScheme.outline
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Stav",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Surface(
                                color = statusColor.copy(alpha = 0.1f),
                                shape = MaterialTheme.shapes.small
                            ) {
                                Text(
                                    text = statusLabel,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                    style = MaterialTheme.typography.labelMedium,
                                    color = statusColor
                                )
                            }
                        }
                    }
                }
            }
        }

        // Actions
        if (equipment.status == "available" && equipment.currentHolder == null) {
            Button(
                onClick = onRequestTransfer,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.SwapHoriz, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Požiadať o transfer")
            }
        }
    }
}

@Composable
fun DetailRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    value: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            icon,
            contentDescription = null,
            modifier = Modifier.size(20.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
