package sk.sppd.vercajch.ui.screens.transfers

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
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateTransferRequestScreen(
    equipmentId: String?,
    equipmentName: String?,
    holderId: String?,
    holderName: String?,
    onBack: () -> Unit,
    onSuccess: () -> Unit,
    viewModel: CreateTransferRequestViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    var message by remember { mutableStateOf("") }
    var selectedDuration by remember { mutableStateOf<Int?>(null) }
    var showDatePicker by remember { mutableStateOf(false) }
    var neededUntil by remember { mutableStateOf<LocalDate?>(null) }

    val durationOptions = listOf(
        1 to "1 deň",
        3 to "3 dni",
        7 to "1 týždeň",
        14 to "2 týždne",
        30 to "1 mesiac",
        0 to "Vlastný dátum"
    )

    LaunchedEffect(uiState.success) {
        if (uiState.success) {
            onSuccess()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Požiadať o náradie") },
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
                .verticalScroll(scrollState)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Equipment info card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.Build,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = equipmentName ?: "Náradie",
                                style = MaterialTheme.typography.titleMedium
                            )
                            if (holderName != null) {
                                Text(
                                    text = "Aktuálny držiteľ: $holderName",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer
                                )
                            }
                        }
                    }
                }
            }

            // Duration selection
            Text(
                text = "Ako dlho potrebujete náradie?",
                style = MaterialTheme.typography.titleSmall
            )

            Column(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                durationOptions.forEach { (days, label) ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedDuration == days,
                            onClick = {
                                selectedDuration = days
                                if (days > 0) {
                                    neededUntil = LocalDate.now().plusDays(days.toLong())
                                } else if (days == 0) {
                                    showDatePicker = true
                                }
                            }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = label)

                        if (days == 0 && selectedDuration == 0 && neededUntil != null) {
                            Spacer(modifier = Modifier.width(8.dp))
                            AssistChip(
                                onClick = { showDatePicker = true },
                                label = {
                                    Text(neededUntil!!.format(DateTimeFormatter.ofPattern("d.M.yyyy")))
                                },
                                leadingIcon = {
                                    Icon(
                                        Icons.Default.CalendarMonth,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            )
                        }
                    }
                }
            }

            // Needed until display
            if (neededUntil != null && selectedDuration != 0) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.tertiaryContainer
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.CalendarMonth,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.tertiary
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Potrebujem do: ${neededUntil!!.format(DateTimeFormatter.ofPattern("d.M.yyyy"))}",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            HorizontalDivider()

            // Message
            OutlinedTextField(
                value = message,
                onValueChange = { message = it },
                label = { Text("Správa (voliteľná)") },
                placeholder = { Text("Napíšte dôvod požiadavky...") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3,
                maxLines = 5
            )

            // Error message
            if (uiState.error != null) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Error,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = uiState.error!!,
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // Submit button
            Button(
                onClick = {
                    viewModel.createRequest(
                        equipmentId = equipmentId!!,
                        holderId = holderId,
                        neededUntil = neededUntil?.format(DateTimeFormatter.ISO_LOCAL_DATE),
                        message = message.ifBlank { null }
                    )
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isLoading && equipmentId != null
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Icon(Icons.Default.Send, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Odoslať požiadavku")
                }
            }
        }
    }

    // Date picker dialog
    if (showDatePicker) {
        val datePickerState = rememberDatePickerState(
            initialSelectedDateMillis = (neededUntil ?: LocalDate.now().plusDays(1))
                .toEpochDay() * 24 * 60 * 60 * 1000
        )

        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(
                    onClick = {
                        datePickerState.selectedDateMillis?.let { millis ->
                            neededUntil = LocalDate.ofEpochDay(millis / (24 * 60 * 60 * 1000))
                            selectedDuration = 0
                        }
                        showDatePicker = false
                    }
                ) {
                    Text("OK")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDatePicker = false }) {
                    Text("Zrušiť")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }
}
