# Retrofit
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class sk.sppd.vercajch.**$$serializer { *; }
-keepclassmembers class sk.sppd.vercajch.** {
    *** Companion;
}
-keepclasseswithmembers class sk.sppd.vercajch.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# ML Kit
-keep class com.google.mlkit.** { *; }
