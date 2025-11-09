package de.hamelnhack.lenze.android

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class FirebaseMS : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        // Hier könntest du den Token an deinen Server schicken
        Log.d("FCM", "New token: $token")
    }



    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // Wird aufgerufen bei:
        // - data-only Messages (immer)
        // - notification + data Messages, wenn App im Vordergrund ist

        val title = remoteMessage.notification?.title ?: "Meine App"
        val body = remoteMessage.notification?.body ?: "Neue Nachricht"

        showNotification(title, body)
    }

    private fun showNotification(title: String, body: String) {
        val channelId = "default_channel"

        // Intent, das gestartet wird, wenn der User auf die Notification tippt
        val intent = Intent(this, AndroidLauncher::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
        )

        val notificationManager =
            getSystemService(NOTIFICATION_SERVICE) as NotificationManager

        // Ab Android 8: Notification-Channel erforderlich
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Standard Kanal",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }



}
