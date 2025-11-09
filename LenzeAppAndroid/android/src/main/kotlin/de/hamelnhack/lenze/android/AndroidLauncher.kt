package de.hamelnhack.lenze.android

import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.WindowManager

import com.badlogic.gdx.backends.android.AndroidApplication
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration
import de.hamelnhack.lenze.LenzeApp

/** Launches the Android application. */
class AndroidLauncher : AndroidApplication() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val config = AndroidApplicationConfiguration().apply {
            useImmersiveMode = false
        }

        val view = initializeForView(LenzeApp(), config)
        setContentView(view)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            view.setOnApplyWindowInsetsListener { v, insets ->
                val cutout = insets.displayCutout
                if (cutout != null) {
                    safeInsetTopPx = cutout.safeInsetTop
                    safeInsetBottomPx = cutout.safeInsetBottom
                }
                insets
            }
        }
    }
}
