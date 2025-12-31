package sk.sppd.vercajch.ui.screens.about

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import sk.sppd.vercajch.BuildConfig

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AboutScreen(
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val scrollState = rememberScrollState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("O aplikácii") },
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
            // App info card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Default.Build,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Vercajch",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Správa náradia a vybavenia",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Verzia ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                }
            }

            // Features
            SectionTitle("Funkcie aplikácie")
            FeatureItem(
                icon = Icons.Default.QrCodeScanner,
                title = "Skenovanie QR kódov",
                description = "Rýchla identifikácia náradia pomocou QR kódov"
            )
            FeatureItem(
                icon = Icons.Default.Nfc,
                title = "NFC / RFID",
                description = "Bezkontaktná identifikácia pomocou NFC tagov"
            )
            FeatureItem(
                icon = Icons.Default.SwapHoriz,
                title = "Transfery",
                description = "Zapožičiavanie a presun náradia medzi zamestnancami"
            )
            FeatureItem(
                icon = Icons.Default.Inventory,
                title = "Inventarizácia",
                description = "Správa a evidencia firemného vybavenia"
            )

            HorizontalDivider()

            // RFID Info
            SectionTitle("Podporované RFID čipy")

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    RfidChipInfo(
                        name = "MIFARE Classic 1K/4K",
                        frequency = "13.56 MHz",
                        compatible = true,
                        note = "Najrozšírenejší typ, vhodný pre väčšinu aplikácií"
                    )
                    RfidChipInfo(
                        name = "MIFARE Ultralight",
                        frequency = "13.56 MHz",
                        compatible = true,
                        note = "Menšia pamäť, nižšia cena"
                    )
                    RfidChipInfo(
                        name = "NTAG213/215/216",
                        frequency = "13.56 MHz",
                        compatible = true,
                        note = "NFC Forum Type 2, ideálny pre NFC štítky"
                    )
                    RfidChipInfo(
                        name = "MIFARE DESFire",
                        frequency = "13.56 MHz",
                        compatible = true,
                        note = "Vysoká bezpečnosť, AES šifrovanie"
                    )
                    RfidChipInfo(
                        name = "ISO 14443-A/B",
                        frequency = "13.56 MHz",
                        compatible = true,
                        note = "Štandardné NFC karty"
                    )
                    RfidChipInfo(
                        name = "ISO 15693",
                        frequency = "13.56 MHz",
                        compatible = false,
                        note = "Väčší dosah, nie všetky telefóny podporujú"
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Pre správnu funkčnosť NFC musí byť v telefóne zapnuté NFC a telefón musí byť priložený k tagu.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            HorizontalDivider()

            // Bluetooth beacons info
            SectionTitle("Bluetooth Beacons")

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.Bluetooth,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Podporované beacony",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Text("• iBeacon (Apple)")
                    Text("• Eddystone (Google)")
                    Text("• AltBeacon")
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Bluetooth beacony umožňujú automatickú lokalizáciu náradia v priestoroch firmy.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            HorizontalDivider()

            // Contact info
            SectionTitle("Kontakt a podpora")

            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Email, contentDescription = null)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("podpora@spp-d.sk")
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Language, contentDescription = null)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("www.spp-d.sk")
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "© ${java.time.Year.now().value} SPP-D. Všetky práva vyhradené.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }
    }
}

@Composable
private fun SectionTitle(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleMedium,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.primary
    )
}

@Composable
private fun FeatureItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    description: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(32.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun RfidChipInfo(
    name: String,
    frequency: String,
    compatible: Boolean,
    note: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = if (compatible) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = if (compatible) "Podporované" else "Nepodporované",
            tint = if (compatible) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Row {
                Text(
                    text = name,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "($frequency)",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Text(
                text = note,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
