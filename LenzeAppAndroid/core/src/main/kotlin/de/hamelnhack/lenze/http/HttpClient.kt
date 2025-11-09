package de.hamelnhack.lenze.http

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.Net
import com.badlogic.gdx.net.HttpRequestHeader
import com.badlogic.gdx.utils.Json
import com.badlogic.gdx.utils.JsonValue
import com.badlogic.gdx.utils.JsonWriter
import ktx.collections.GdxArray
import java.util.concurrent.Future

class LoadChatPacket{
    var id: String = ""
    var machine_name: String = ""
    var code: Int = 0
    var date: String = ""
}

class ChatMessagePacket{
    var id: String = ""
    var content: String = ""
    var ai: String = ""
}

val json = Json().apply {
    setOutputType(JsonWriter.OutputType.json)
}

val address = "http://localhost"

object HttpClient {

    fun requestAllChats(receiver: (LoadChatPacket)->Unit){
        Gdx.net.sendHttpRequest(Net.HttpRequest(Net.HttpMethods.GET).apply {
            url = "$address/api/chats"
            setHeader(HttpRequestHeader.ContentType, "application/json")
        },
            object : Net.HttpResponseListener{
                override fun handleHttpResponse(response: Net.HttpResponse?) {
                    if(response == null)return
                    val packets = json.fromJson(Array<LoadChatPacket>::class.java,
                        String(response.result))

                    Gdx.app.postRunnable {
                        for(packet in packets){ receiver(packet) }
                    }
                }

                override fun failed(t: Throwable?) {
                    Gdx.app.log("HTTP", "Failed!", t)
                }

                override fun cancelled() {
                    Gdx.app.log("HTTP", "Cancelled!")
                }
            })
    }

    fun requestAllMessages(id: String, receiver: (ChatMessagePacket) -> Unit){
        Gdx.net.sendHttpRequest(Net.HttpRequest(Net.HttpMethods.GET).apply {
            url = "$address/api/chats?id=$id"
            setHeader(HttpRequestHeader.ContentType, "application/json")
        },
            object : Net.HttpResponseListener{
                override fun handleHttpResponse(response: Net.HttpResponse?) {
                    if(response == null)return
                    val packets = json.fromJson(Array<ChatMessagePacket>::class.java,
                        String(response.result))
                    if(packets == null)return
                    Gdx.app.postRunnable {
                        for(packet in packets)receiver(packet)
                    }
                }
                override fun failed(t: Throwable?) {
                    Gdx.app.log("HTTP", "Failed!", t)
                }
                override fun cancelled() {
                    Gdx.app.log("HTTP", "Cancelled!")
                }
            })
    }

    fun requestLatestMessage(id: String, receiver: (ChatMessagePacket) -> Unit){
        Gdx.net.sendHttpRequest(Net.HttpRequest(Net.HttpMethods.GET).apply {
            url = "$address/api/chats?id=$id&last=true"
            setHeader(HttpRequestHeader.ContentType, "application/json")
        },
            object : Net.HttpResponseListener{
                override fun handleHttpResponse(response: Net.HttpResponse?) {
                    if(response == null)return
                    val packets = json.fromJson(Array<ChatMessagePacket>::class.java,
                        String(response.result))
                    if(packets == null)return
                    Gdx.app.postRunnable {
                        for(packet in packets)receiver(packet)
                    }
                }

                override fun failed(t: Throwable?) {
                    Gdx.app.log("HTTP", "Failed!", t)
                }

                override fun cancelled() {
                    Gdx.app.log("HTTP", "Cancelled!")
                }
            })
    }
    //"[{\"id\":\"$id\",\"content\":\"$msg\",\"id\":\"$id\"}]"
    fun sendMessage(packet: ChatMessagePacket){
        val httpRequest = Net.HttpRequest(Net.HttpMethods.POST)
        httpRequest.url = "$address/api/send"
        httpRequest.setHeader(HttpRequestHeader.ContentType, "application/json")

        val jsonString = json.toJson(packet)
        httpRequest.content = jsonString
        Gdx.app.log("HTTP", "JSON $jsonString")

        Gdx.net.sendHttpRequest(httpRequest, object : Net.HttpResponseListener {
            override fun handleHttpResponse(httpResponse: Net.HttpResponse) {
                val response = httpResponse.resultAsString
                Gdx.app.log("HTTP", "Response $response")
            }

            override fun failed(t: Throwable) {
                Gdx.app.error("HTTP Error", t.message)
            }

            override fun cancelled() {
                Gdx.app.log("HTTP", "Request cancelled")
            }
        })
    }

}
