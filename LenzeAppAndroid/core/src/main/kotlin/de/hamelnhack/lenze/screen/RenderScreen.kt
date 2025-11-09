package de.hamelnhack.lenze.screen

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.scenes.scene2d.ui.Table
import de.hamelnhack.lenze.LenzeApp
import de.hamelnhack.lenze.android.safeInsetBottomPx
import de.hamelnhack.lenze.android.safeInsetTopPx
import ktx.app.KtxScreen
import ktx.scene2d.Scene2DSkin

const val animationSpeed: Float = 0.25f
abstract class RenderScreen : KtxScreen {

    protected val stage = LenzeApp.instance.stage
    protected val skin = Scene2DSkin.defaultSkin
    protected lateinit var root: Table

    protected abstract fun build() : Table

    override fun show() {
        root = build()
        val vh = stage.viewport.worldHeight
        val screenH = Gdx.graphics.height.toFloat()
        val safeTopWorld = safeInsetTopPx / screenH * vh
        val safeBottomWorld = safeInsetBottomPx / screenH * vh
        root.padTop(safeTopWorld).padBottom(safeBottomWorld)

        root.setFillParent(true)
        stage.addActor(root)
        Gdx.app.debug("RenderScreen", "Showing "+this::javaClass.name)
    }

    override fun render(delta: Float) {
        stage.act()
        stage.draw()
    }

    override fun hide() {
        stage.actors.removeValue(root, true)
        Gdx.app.debug("RenderScreen", "Hiding "+this::javaClass.name)
    }
}
