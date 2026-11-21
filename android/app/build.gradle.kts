plugins { id("com.android.application") }
android {
    namespace = "io.github.ilshang2.tvcountdown"
    compileSdk = 35
    defaultConfig {
        applicationId = "io.github.ilshang2.tvcountdown"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    buildTypes { release { isMinifyEnabled = false; signingConfig = signingConfigs.getByName("debug") } }
}
