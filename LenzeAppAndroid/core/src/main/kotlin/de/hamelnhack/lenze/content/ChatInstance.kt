package de.hamelnhack.lenze.content

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.Input
import com.badlogic.gdx.graphics.Color
import com.badlogic.gdx.scenes.scene2d.actions.Actions
import com.badlogic.gdx.scenes.scene2d.ui.ScrollPane
import com.badlogic.gdx.scenes.scene2d.ui.Table
import com.badlogic.gdx.scenes.scene2d.ui.Value
import com.badlogic.gdx.scenes.scene2d.utils.TextureRegionDrawable
import de.hamelnhack.lenze.LenzeApp
import de.hamelnhack.lenze.asset.Assets
import de.hamelnhack.lenze.http.ChatMessagePacket
import de.hamelnhack.lenze.http.HttpClient
import de.hamelnhack.lenze.screen.MainMenu
import de.hamelnhack.lenze.screen.RenderScreen
import de.hamelnhack.lenze.screen.animationSpeed
import ktx.actors.onClick
import ktx.scene2d.Scene2DSkin
import ktx.scene2d.imageButton
import ktx.scene2d.label
import ktx.scene2d.scene2d
import ktx.scene2d.scrollPane
import ktx.scene2d.table
import ktx.scene2d.textButton
import ktx.scene2d.textField
import java.util.LinkedList
import kotlin.math.exp

val chats: ArrayList<Chat> = ArrayList()

data class Chat(val id: String, val machineName: String, val errorCode: Int,
                val date: String, val solved: Boolean)

class ChatInstance(val chat: Chat) : RenderScreen() {

    var lastPacket: ChatMessagePacket? = null
    val messages = Table()
    lateinit var scroll: ScrollPane
    init {
        Gdx.input.setCatchKey(Input.Keys.BACK, true)
        HttpClient.requestAllMessages(chat.id){
            addMessage(it)
        }
    }

    override fun hide() {
        Gdx.input.setCatchKey(Input.Keys.BACK, false)
        root.addAction(Actions.sequence(Actions.moveTo(Gdx.graphics.width.toFloat(), 0f, animationSpeed),
            Actions.removeActor()))
    }

    private var requestTimer = 0f
    private val MAX_TIMER = 3f; //3 seconds
    override fun render(delta: Float) {
        super.render(delta)
        if(Gdx.input.isKeyJustPressed(Input.Keys.BACK)){
            LenzeApp.instance.current = MainMenu()
        }
        if(sendLock){
            requestTimer += delta
            if(requestTimer >= MAX_TIMER){
                requestTimer = 0f
                HttpClient.requestLatestMessage(chat.id){
                    if(lastPacket == null || it.ai == "AI"){
                        addMessage(it)
                        sendLock = false
                        requestTimer = 0f
                    }
                }
            }
        }
    }

    fun addMessage(msg: ChatMessagePacket){
        val ai = msg.ai == "AI"
        messages.add(scene2d.table {
            background = skin.getDrawable("button")
            if(ai) color = Color.ROYAL else color = Color.LIGHT_GRAY
            label(msg.content){
                it.growX()
                it.pad(16f)
                style.font = Scene2DSkin.defaultSkin.getFont("title")
                style.fontColor = Color.WHITE
                wrap = true
            }
        }).apply {
            growX()
            width(Value.percentWidth(0.9f, root))
            row()
            spaceTop(16f)
            spaceBottom(16f)
        }
        messages.invalidate()
        scroll.layout()
        scroll.scrollY = scroll.maxY
        lastPacket = msg
    }

    var sendLock = false

    override fun build(): Table = scene2d.table {
        val rootTab = this

        //top
        table{
            background = skin.getDrawable("bg")
            color = Color.LIGHT_GRAY
            padTop(64f)
            padBottom(64f)
            label("Chat", "title")
        }.cell(growX = true)
        row()
        //middle
        scroll = scrollPane {
            actor = messages
            setScrollingDisabled(true,false)
            setScrollbarsVisible(false)
            it.expand()
        }
        row()
        //bottom
        table {
            it.height(Value.percentHeight(0.075f, rootTab))
            val field = textField {
                style.font = Scene2DSkin.defaultSkin.getFont("title")
                style.fontColor = Color.WHITE

            }.cell(grow = true)
            textButton("Senden"){
                it.width(Value.percentWidth(.25f,this@table))
                style.font = Scene2DSkin.defaultSkin.getFont("title")
                style.fontColor = Color.BLUE

                onClick {
                    if(field.text.isEmpty() || sendLock)return@onClick
                    sendLock = true
                    val packet = ChatMessagePacket().apply {
                        id = chat.id
                        content = field.text
                        ai = "User"
                    }
                    HttpClient.sendMessage(packet)
                    addMessage(packet)
                    field.text = ""
                }

            }.cell(fill = true)
            background = skin.getDrawable("button")
            color = Color.DARK_GRAY

        }.cell(growX = true, pad = 16f)

        setX(Gdx.graphics.width.toFloat())
        addAction(Actions.sequence(Actions.moveTo(0f,0f, animationSpeed), Actions.run {
            invalidate()
        }))
    }



}
