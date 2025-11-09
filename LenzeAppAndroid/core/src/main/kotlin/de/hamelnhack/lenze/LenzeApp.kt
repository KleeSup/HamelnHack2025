package de.hamelnhack.lenze

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.graphics.Color
import com.badlogic.gdx.graphics.Pixmap
import com.badlogic.gdx.graphics.Pixmap.Format
import com.badlogic.gdx.graphics.Texture
import com.badlogic.gdx.graphics.g2d.BitmapFont
import com.badlogic.gdx.graphics.g2d.SpriteBatch
import com.badlogic.gdx.graphics.g2d.TextureRegion
import com.badlogic.gdx.graphics.g2d.freetype.FreeTypeFontGenerator
import com.badlogic.gdx.scenes.scene2d.Stage
import com.badlogic.gdx.scenes.scene2d.ui.Skin
import com.badlogic.gdx.utils.Logger
import com.badlogic.gdx.utils.ScreenUtils
import de.hamelnhack.lenze.asset.Assets
import de.hamelnhack.lenze.content.Chat
import de.hamelnhack.lenze.content.chats
import de.hamelnhack.lenze.http.HttpClient
import de.hamelnhack.lenze.screen.MainMenu
import de.hamelnhack.lenze.screen.RenderScreen
import ktx.app.KtxApplicationAdapter
import ktx.assets.toInternalFile
import ktx.scene2d.Scene2DSkin
import space.earlygrey.shapedrawer.ShapeDrawer

class LenzeApp : KtxApplicationAdapter{

    @Suppress("GDXKotlinStaticResource")
    companion object{
        lateinit var instance: LenzeApp
    }

    lateinit var drawer: ShapeDrawer
    lateinit var stage: Stage
    var current: RenderScreen? = null
        set(value){
            field?.hide()
            field = value
            field?.show()
        }

    override fun create() {
        instance = this
        stage = Stage()
        Gdx.app.logLevel = Logger.DEBUG

        val pixmap = Pixmap(1, 1, Format.RGBA8888)
        pixmap.setColor(Color.WHITE);
        pixmap.drawPixel(0,0)
        val texture = Texture(pixmap)
        drawer = ShapeDrawer(SpriteBatch(), TextureRegion(texture))

        Scene2DSkin.defaultSkin = Skin("skin/level-plane-ui.json".toInternalFile())
        Assets.load()
        Gdx.input.inputProcessor = stage
        HttpClient.requestAllChats {
            val chat = Chat(it.id, it.machine_name, it.code, it.date, true)
            chats.add(chat)
            if(current is MainMenu)(current as MainMenu).notifyNew(chat)
        }
    }

    override fun render() {
        ScreenUtils.clear(Color.WHITE)
        if(Assets.isFinished()){
            current?.render(Gdx.graphics.deltaTime)
        }else{
            if(Assets.update()){
                Gdx.app.log("LenzeApp", "Loading finished!")
                current = MainMenu(false)
            }
        }
    }

    override fun resize(width: Int, height: Int) {
        stage.viewport.update(width,height,true)
    }

    override fun dispose() {
        Assets.dispose()
        stage.dispose()
        Scene2DSkin.defaultSkin.dispose()
    }
}
