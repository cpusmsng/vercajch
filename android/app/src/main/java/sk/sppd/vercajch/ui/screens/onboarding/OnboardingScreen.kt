package sk.sppd.vercajch.ui.screens.onboarding

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import sk.sppd.vercajch.data.model.Category
import sk.sppd.vercajch.data.model.Location

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(
    initialTagValue: String?,
    onComplete: (String) -> Unit,
    onCancel: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(initialTagValue) {
        viewModel.startOnboarding(initialTagValue)
    }

    LaunchedEffect(uiState.completedEquipmentId) {
        uiState.completedEquipmentId?.let { id ->
            onComplete(id)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Nové náradie") },
                navigationIcon = {
                    IconButton(onClick = {
                        viewModel.cancelOnboarding()
                        onCancel()
                    }) {
                        Icon(Icons.Default.Close, contentDescription = "Zrušiť")
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
            // Progress indicator
            LinearProgressIndicator(
                progress = { (uiState.currentStep.toFloat()) / 6f },
                modifier = Modifier.fillMaxWidth(),
            )

            // Step indicator
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                val steps = listOf("QR", "Foto", "Info", "Prísl.", "Kalib.", "Súhrn")
                steps.forEachIndexed { index, label ->
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(
                                    if (index + 1 <= uiState.currentStep)
                                        MaterialTheme.colorScheme.primary
                                    else
                                        MaterialTheme.colorScheme.surfaceVariant
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "${index + 1}",
                                color = if (index + 1 <= uiState.currentStep)
                                    MaterialTheme.colorScheme.onPrimary
                                else
                                    MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.labelMedium
                            )
                        }
                        Text(
                            text = label,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Content
            Box(
                modifier = Modifier
                    .weight(1f)
                    .padding(16.dp)
            ) {
                when (uiState.currentStep) {
                    1 -> Step1TagScan(
                        tagValue = uiState.tagValue,
                        onTagValueChange = { viewModel.updateTagValue(it) }
                    )
                    2 -> Step2Photos(
                        photos = uiState.photos,
                        onAddPhoto = { uri -> viewModel.addPhoto(context, uri) },
                        onRemovePhoto = { viewModel.removePhoto(it) }
                    )
                    3 -> Step3Details(
                        name = uiState.name,
                        description = uiState.description,
                        serialNumber = uiState.serialNumber,
                        categories = uiState.categories,
                        locations = uiState.locations,
                        selectedCategoryId = uiState.categoryId,
                        selectedLocationId = uiState.locationId,
                        onNameChange = { viewModel.updateName(it) },
                        onDescriptionChange = { viewModel.updateDescription(it) },
                        onSerialNumberChange = { viewModel.updateSerialNumber(it) },
                        onCategoryChange = { viewModel.updateCategory(it) },
                        onLocationChange = { viewModel.updateLocation(it) }
                    )
                    4 -> Step4Accessories(
                        accessories = uiState.accessoryTypes,
                        selectedAccessories = uiState.selectedAccessories,
                        onToggleAccessory = { viewModel.toggleAccessory(it) }
                    )
                    5 -> Step5Calibration(
                        requiresCalibration = uiState.requiresCalibration,
                        calibrationIntervalDays = uiState.calibrationIntervalDays,
                        lastCalibrationDate = uiState.lastCalibrationDate,
                        calibrationLab = uiState.calibrationLab,
                        certificateNumber = uiState.certificateNumber,
                        onRequiresCalibrationChange = { viewModel.updateRequiresCalibration(it) },
                        onIntervalChange = { viewModel.updateCalibrationInterval(it) },
                        onLastDateChange = { viewModel.updateLastCalibrationDate(it) },
                        onLabChange = { viewModel.updateCalibrationLab(it) },
                        onCertificateChange = { viewModel.updateCertificateNumber(it) }
                    )
                    6 -> Step6Summary(uiState = uiState)
                }
            }

            // Error
            if (uiState.error != null) {
                Text(
                    text = uiState.error!!,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
            }

            // Navigation buttons
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                if (uiState.currentStep > 1) {
                    OutlinedButton(
                        onClick = { viewModel.previousStep() },
                        enabled = !uiState.isLoading
                    ) {
                        Text("Späť")
                    }
                } else {
                    Spacer(modifier = Modifier.width(1.dp))
                }

                Button(
                    onClick = {
                        if (uiState.currentStep == 6) {
                            viewModel.complete()
                        } else {
                            viewModel.nextStep()
                        }
                    },
                    enabled = !uiState.isLoading && viewModel.canProceed()
                ) {
                    if (uiState.isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text(if (uiState.currentStep == 6) "Dokončiť" else "Ďalej")
                    }
                }
            }
        }
    }
}

@Composable
fun Step1TagScan(
    tagValue: String,
    onTagValueChange: (String) -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            Icons.Default.QrCode,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = "QR kód naskenovaný",
            style = MaterialTheme.typography.headlineSmall
        )
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedTextField(
            value = tagValue,
            onValueChange = onTagValueChange,
            label = { Text("Hodnota tagu") },
            modifier = Modifier.fillMaxWidth(),
            enabled = false
        )
    }
}

@Composable
fun Step2Photos(
    photos: List<Uri>,
    onAddPhoto: (Uri) -> Unit,
    onRemovePhoto: (Int) -> Unit
) {
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let { onAddPhoto(it) }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Fotografie",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "Pridajte fotografie náradia",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(photos.size) { index ->
                Box(
                    modifier = Modifier
                        .size(120.dp)
                        .clip(MaterialTheme.shapes.medium)
                ) {
                    AsyncImage(
                        model = photos[index],
                        contentDescription = "Photo ${index + 1}",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                    IconButton(
                        onClick = { onRemovePhoto(index) },
                        modifier = Modifier.align(Alignment.TopEnd)
                    ) {
                        Icon(
                            Icons.Default.Close,
                            contentDescription = "Odstrániť",
                            tint = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }

            item {
                Box(
                    modifier = Modifier
                        .size(120.dp)
                        .clip(MaterialTheme.shapes.medium)
                        .border(
                            2.dp,
                            MaterialTheme.colorScheme.outline,
                            MaterialTheme.shapes.medium
                        )
                        .clickable { launcher.launch("image/*") },
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Default.Add,
                            contentDescription = "Pridať foto",
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "Pridať",
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun Step3Details(
    name: String,
    description: String,
    serialNumber: String,
    categories: List<Category>,
    locations: List<Location>,
    selectedCategoryId: String?,
    selectedLocationId: String?,
    onNameChange: (String) -> Unit,
    onDescriptionChange: (String) -> Unit,
    onSerialNumberChange: (String) -> Unit,
    onCategoryChange: (String) -> Unit,
    onLocationChange: (String) -> Unit
) {
    var categoryExpanded by remember { mutableStateOf(false) }
    var locationExpanded by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Základné informácie",
            style = MaterialTheme.typography.headlineSmall
        )

        OutlinedTextField(
            value = name,
            onValueChange = onNameChange,
            label = { Text("Názov *") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        OutlinedTextField(
            value = description,
            onValueChange = onDescriptionChange,
            label = { Text("Popis") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 3
        )

        OutlinedTextField(
            value = serialNumber,
            onValueChange = onSerialNumberChange,
            label = { Text("Sériové číslo") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        ExposedDropdownMenuBox(
            expanded = categoryExpanded,
            onExpandedChange = { categoryExpanded = it }
        ) {
            OutlinedTextField(
                value = categories.find { it.id == selectedCategoryId }?.name ?: "",
                onValueChange = {},
                readOnly = true,
                label = { Text("Kategória *") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = categoryExpanded) },
                modifier = Modifier
                    .fillMaxWidth()
                    .menuAnchor()
            )
            ExposedDropdownMenu(
                expanded = categoryExpanded,
                onDismissRequest = { categoryExpanded = false }
            ) {
                categories.forEach { category ->
                    DropdownMenuItem(
                        text = { Text(category.name) },
                        onClick = {
                            onCategoryChange(category.id)
                            categoryExpanded = false
                        }
                    )
                }
            }
        }

        ExposedDropdownMenuBox(
            expanded = locationExpanded,
            onExpandedChange = { locationExpanded = it }
        ) {
            OutlinedTextField(
                value = locations.find { it.id == selectedLocationId }?.name ?: "",
                onValueChange = {},
                readOnly = true,
                label = { Text("Lokácia *") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = locationExpanded) },
                modifier = Modifier
                    .fillMaxWidth()
                    .menuAnchor()
            )
            ExposedDropdownMenu(
                expanded = locationExpanded,
                onDismissRequest = { locationExpanded = false }
            ) {
                locations.forEach { location ->
                    DropdownMenuItem(
                        text = { Text(location.name) },
                        onClick = {
                            onLocationChange(location.id)
                            locationExpanded = false
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun Step4Accessories(
    accessories: List<String>,
    selectedAccessories: Set<String>,
    onToggleAccessory: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "Príslušenstvo",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "Vyberte príslušenstvo, ktoré je súčasťou náradia",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(8.dp))

        if (accessories.isEmpty()) {
            Text(
                text = "Pre túto kategóriu nie je definované príslušenstvo",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        } else {
            accessories.forEach { accessory ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onToggleAccessory(accessory) }
                        .padding(vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = selectedAccessories.contains(accessory),
                        onCheckedChange = { onToggleAccessory(accessory) }
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = accessory)
                }
            }
        }
    }
}

@Composable
fun Step5Calibration(
    requiresCalibration: Boolean,
    calibrationIntervalDays: String,
    lastCalibrationDate: String,
    calibrationLab: String,
    certificateNumber: String,
    onRequiresCalibrationChange: (Boolean) -> Unit,
    onIntervalChange: (String) -> Unit,
    onLastDateChange: (String) -> Unit,
    onLabChange: (String) -> Unit,
    onCertificateChange: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Kalibrácia",
            style = MaterialTheme.typography.headlineSmall
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Switch(
                checked = requiresCalibration,
                onCheckedChange = onRequiresCalibrationChange
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text("Vyžaduje kalibráciu")
        }

        if (requiresCalibration) {
            OutlinedTextField(
                value = calibrationIntervalDays,
                onValueChange = onIntervalChange,
                label = { Text("Interval kalibrácie (dní)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = lastCalibrationDate,
                onValueChange = onLastDateChange,
                label = { Text("Dátum poslednej kalibrácie") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                placeholder = { Text("YYYY-MM-DD") }
            )

            OutlinedTextField(
                value = calibrationLab,
                onValueChange = onLabChange,
                label = { Text("Kalibračné laboratórium") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = certificateNumber,
                onValueChange = onCertificateChange,
                label = { Text("Číslo certifikátu") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
        }
    }
}

@Composable
fun Step6Summary(uiState: OnboardingUiState) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Súhrn",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "Skontrolujte údaje pred uložením",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                SummaryRow("Názov", uiState.name)
                SummaryRow("QR kód", uiState.tagValue)
                SummaryRow("Kategória", uiState.categories.find { it.id == uiState.categoryId }?.name ?: "-")
                SummaryRow("Lokácia", uiState.locations.find { it.id == uiState.locationId }?.name ?: "-")
                if (uiState.serialNumber.isNotBlank()) {
                    SummaryRow("Sériové číslo", uiState.serialNumber)
                }
                SummaryRow("Počet fotiek", "${uiState.photos.size}")
                SummaryRow("Príslušenstvo", "${uiState.selectedAccessories.size} položiek")
                SummaryRow("Kalibrácia", if (uiState.requiresCalibration) "Áno" else "Nie")
            }
        }
    }
}

@Composable
fun SummaryRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}
