package mobile

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/messaging"
	"google.golang.org/api/option"
)

func Send(title, body string) {
	ctx := context.Background()

	// Service Account Datei (aus Firebase Console)
	opt := option.WithCredentialsFile("service-account.json")

	// Firebase App initialisieren
	app, err := firebase.NewApp(ctx, nil, opt)
	if err != nil {
		log.Fatalf("Firebase init fehlgeschlagen: %v", err)
	}

	// FCM Client
	client, err := app.Messaging(ctx)
	if err != nil {
		log.Fatalf("Messaging Client Fehler: %v", err)
	}

	// Beispiel-Token (von onNewToken() aus der App)
	deviceToken := "YOUR_DEVICE_TOKEN"

	// Nachricht bauen
	message := &messaging.Message{
		Token: deviceToken,
		Notification: &messaging.Notification{
			Title: title,
			Body:  body,
		},
	}

	// Nachricht senden
	response, err := client.Send(ctx, message)
	if err != nil {
		log.Fatalf("Fehler beim Senden: %v", err)
	}

	fmt.Println("Erfolgreich gesendet:", response)
}
