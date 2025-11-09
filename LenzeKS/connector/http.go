package connector

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/google/uuid"
)

type LoadChatPacket struct {
	Id          uuid.UUID `json:"id"`
	MachineName string    `json:"machine_name"`
	Code        uint16    `json:"code"`
	Date        time.Time `json:"date"`
}

type ChatMessagePacket struct {
	Id      uuid.UUID `json:"id"`
	Content string    `json:"content"`
	AI      string    `json:"ai"`
}

type HttpService struct{}

func (s *HttpService) Start(wg *sync.WaitGroup, allChats func() ([]LoadChatPacket, error),
	allMessages func(uuid.UUID, bool) ([]ChatMessagePacket, error), readMsg func(ChatMessagePacket)) error {
	log.Println("Starting HttpService...")
	http.HandleFunc("/api/chats", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		idStr := r.URL.Query().Get("id")
		if idStr == "" { //send all chats
			packets, err := allChats()
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				log.Println(err)
				return
			}
			err = json.NewEncoder(w).Encode(packets)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				log.Println(err)
				return
			}
			return
		}

		// Parse string to UUID
		id, err := uuid.Parse(idStr)
		if err != nil {
			http.Error(w, "Invalid UUID format", http.StatusBadRequest)
			return
		}

		//request single id

		onlyLast := r.URL.Query().Get("last") == "true"
		messages, err := allMessages(id, onlyLast)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			log.Println(err)
			return
		}
		err = json.NewEncoder(w).Encode(messages)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			log.Println(err)
			return
		}

	})

	http.HandleFunc("/api/send", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var packet ChatMessagePacket
		err := json.NewDecoder(r.Body).Decode(&packet)
		if err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}

		log.Printf("Received: %+v", packet)
		readMsg(packet)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		err = json.NewEncoder(w).Encode(map[string]string{"status": "success"})
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			log.Println(err)
			return
		}
	})

	go func() {
		defer wg.Done()
		err := http.ListenAndServe(":8080", nil)
		if err != nil {
			log.Fatal(err)
		}
	}()
	fmt.Println("HttpService started!")
	return nil
}
