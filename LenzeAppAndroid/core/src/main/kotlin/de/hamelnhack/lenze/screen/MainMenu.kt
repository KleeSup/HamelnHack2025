package de.hamelnhack.lenze.screen

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.graphics.Color
import com.badlogic.gdx.scenes.scene2d.actions.Actions
import com.badlogic.gdx.scenes.scene2d.ui.Label
import com.badlogic.gdx.scenes.scene2d.ui.Skin
import com.badlogic.gdx.scenes.scene2d.ui.Table
import com.badlogic.gdx.scenes.scene2d.ui.Value
import com.badlogic.gdx.scenes.scene2d.utils.NinePatchDrawable
import de.hamelnhack.lenze.LenzeApp
import de.hamelnhack.lenze.asset.Assets
import de.hamelnhack.lenze.content.Chat
import de.hamelnhack.lenze.content.ChatInstance
import de.hamelnhack.lenze.content.chats
import ktx.actors.onClick
import ktx.scene2d.Scene2DSkin
import ktx.scene2d.image
import ktx.scene2d.label
import ktx.scene2d.scene2d
import ktx.scene2d.scrollPane
import ktx.scene2d.table

class MainMenu(val slideIn: Boolean = true) : RenderScreen() {


    override fun hide() {
        root.addAction(Actions.sequence(Actions.moveTo(-Gdx.graphics.width.toFloat(), 0f, animationSpeed),
            Actions.removeActor()))
    }

    lateinit var scrollable: Table
    fun notifyNew(chat: Chat){
        scrollable.add(scene2d.table {
            val sColor = Color(.9f,.9f,.9f,1f)
            val openSans = Scene2DSkin.defaultSkin.getFont("font")
            val titleUnsolvedStyle = Label.LabelStyle(Scene2DSkin.defaultSkin.getFont("extra"), Color.RED)
            val codeStyle  = Label.LabelStyle(openSans, Color.BLACK)
            val codeUnresolvedStyle  = Label.LabelStyle(openSans, Color.BLACK)
            val titleStyle = Label.LabelStyle(Scene2DSkin.defaultSkin.getFont("title"), Color.BLUE)
            table {
                background = skin.getDrawable("bg")
                color = sColor

                // Maschinenname + Datum
                label(chat.machineName){
                    style = if(chat.solved) titleStyle else titleUnsolvedStyle
                    it.left().padLeft(16f).padTop(16f)
                    onClick {
                        LenzeApp.instance.current = ChatInstance(chat)
                    }
                }
                row()

                // Fehlercode
                label("Fehlercode: ${chat.errorCode}"){
                    style = if(chat.solved) codeStyle else codeUnresolvedStyle
                    it.left().padLeft(16f)
                }
                row()
                label("Datum: ${chat.date}"){
                    style = if(chat.solved) codeStyle else codeUnresolvedStyle
                    it.left().padLeft(16f).padBottom(16f)
                }

                left()
            }.cell(growX = true)
        }).row()
        scrollable.invalidate()
    }

    override fun build(): Table = scene2d.table {
        // Root-Table füllt die Stage
        setFillParent(true)
        top()

        // --- Font-Styles auf Basis von OpenSans -----------------------------


        // Scale noch einmal leicht anpassen (falls nötig)
        // Hier z.B. relativ zu einer Referenzhöhe von 800 px
        //val scale = Gdx.graphics.height / 800f * 1.2f
        //openSans.data.setScale(scale)

        val titleStyle = Label.LabelStyle(Scene2DSkin.defaultSkin.getFont("title"), Color.BLUE)


        // --- Logo oben ------------------------------------------------------
        image(Assets.LOGO) {
            it.expandX()
                .center()
                .padTop(16f)
                .padBottom(64f)
        }
        row()

        label("Letzte Nachrichten") {
            style = Label.LabelStyle(titleStyle.font, Color.GRAY)
            it.padBottom(32f)
        }
        row()

        // --- Content-Tabelle für Chats (NICHT Kind des Root-Tables) --------
        scrollable = scene2d.table {
            top()
            defaults().growX().pad(8f)
        }
        for (chat in chats) {
            notifyNew(chat)
        }

        // --- ScrollPane: 90 % der Bildschirmbreite, zentriert --------------
        scrollPane {
            actor = scrollable
            setScrollingDisabled(true, false) // nur vertikal scrollen
            setScrollbarsVisible(true)

            it.width(Value.percentWidth(0.9f, this@table)) // 90 % der Root-Table-Breite
                .expandY()     // nimmt den restlichen vertikalen Platz ein
                .fillY()
                .center()
                .padBottom(64f)
        }

        // optional zum Debuggen
        // debugAll()
        if(slideIn){
            setX(-(Gdx.graphics.width.toFloat()))
            addAction(Actions.sequence(Actions.moveTo(0f,0f,animationSpeed), Actions.run {
                invalidate()
            }))
        }
    }
}
