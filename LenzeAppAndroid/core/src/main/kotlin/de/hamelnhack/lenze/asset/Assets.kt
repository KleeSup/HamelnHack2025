package de.hamelnhack.lenze.asset

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.assets.AssetManager
import com.badlogic.gdx.graphics.Color
import com.badlogic.gdx.graphics.Texture
import com.badlogic.gdx.graphics.g2d.freetype.FreeTypeFontGenerator
import com.badlogic.gdx.scenes.scene2d.ui.Label
import com.badlogic.gdx.scenes.scene2d.ui.Skin
import com.badlogic.gdx.scenes.scene2d.utils.Drawable
import com.badlogic.gdx.utils.Disposable
import ktx.assets.toInternalFile
import ktx.scene2d.Scene2DSkin

@Suppress("GDXKotlinStaticResource")
object Assets : Disposable {

    val manager = AssetManager()
    val BG_LIGHT_GRAY = Color(.9f,.9f,.9f,1f)


    lateinit var LOGO: Texture
    lateinit var ICON_SEND: Texture

    fun load(){
        manager.load("logo.png", Texture::class.java)
        manager.load("icon_send.png", Texture::class.java)

    }

    override fun dispose(){
        LOGO.dispose()
        ICON_SEND.dispose()
    }

    private fun finish(){
        LOGO = manager.get("logo.png")
        ICON_SEND = manager.get("icon_send.png")

        val skin = Skin("lgdxs/lgdxs-ui.json".toInternalFile())
        Scene2DSkin.defaultSkin.add("bg",
            skin.getDrawable("button-oval"), Drawable::class.java)

        val height = 0.020f
        //default
        var generator = FreeTypeFontGenerator("font/OpenSans-Regular.ttf".toInternalFile())
        var parameter = FreeTypeFontGenerator.FreeTypeFontParameter().apply {
            size = (Gdx.graphics.height * height).toInt()
            magFilter = Texture.TextureFilter.Linear
            minFilter = Texture.TextureFilter.Linear
        }
        var font = generator.generateFont(parameter)
        Scene2DSkin.defaultSkin.add("font", font)
        Scene2DSkin.defaultSkin.add("default", Label.LabelStyle().apply {
            fontColor = Color.DARK_GRAY
            this.font = font
            background = Scene2DSkin.defaultSkin.get(Label.LabelStyle::class.java).background
        })
        generator.dispose()

        //bold
        generator = FreeTypeFontGenerator("font/OpenSans-Bold.ttf".toInternalFile())
        parameter = FreeTypeFontGenerator.FreeTypeFontParameter().apply {
            size = (Gdx.graphics.height * height).toInt()
            magFilter = Texture.TextureFilter.Linear
            minFilter = Texture.TextureFilter.Linear
        }
        font = generator.generateFont(parameter)
        Scene2DSkin.defaultSkin.add("title", font)
        Scene2DSkin.defaultSkin.add("title", Label.LabelStyle().apply {
            fontColor = Color.BLUE
            this.font = font
            background = Scene2DSkin.defaultSkin.get(Label.LabelStyle::class.java).background
        })
        generator.dispose()

        //extra bold
        generator = FreeTypeFontGenerator("font/OpenSans-ExtraBold.ttf".toInternalFile())
        parameter = FreeTypeFontGenerator.FreeTypeFontParameter().apply {
            size = (Gdx.graphics.height * height).toInt()
            magFilter = Texture.TextureFilter.Linear
            minFilter = Texture.TextureFilter.Linear
        }
        font = generator.generateFont(parameter)
        Scene2DSkin.defaultSkin.add("extra", font)
        generator.dispose()
    }



    fun update() : Boolean{
        val done = manager.update()
        if(done){
            finish()
        }
        return done
    }

    fun isFinished() : Boolean = manager.isFinished

}
