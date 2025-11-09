package sqldb

import (
	"LenzeKS/connector"
	"database/sql"
	"log"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
)

const conn = "postgres://HamelnHackRobert:Robert2025@hamelnhack.postgres.database.azure.com:5432/Hamelnhack?sslmode=require"

type ChatDatabase struct {
	db *sql.DB
}

func (cdb *ChatDatabase) CreateChat(machineName string, code int) (uuid.UUID, error) {
	id := uuid.New()
	log.Println("Creating Chat:", machineName, "(", code, ")")
	_, err := cdb.db.Exec("INSERT INTO chats(id, maschine, fehlercode) VALUES ($1,$2,$3)",
		id.String(), machineName, code)
	if err != nil {
		return uuid.Nil, err
	}
	return id, nil
}

func (cdb *ChatDatabase) GetAllChats() ([]connector.LoadChatPacket, error) {
	result, err := cdb.db.Query("SELECT id, maschine, fehlercode, erstellungsdatum FROM chats ORDER BY erstellungsdatum DESC")
	if err != nil {
		return nil, err
	}
	defer func(result *sql.Rows) {
		err := result.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(result)
	var chats []connector.LoadChatPacket
	for result.Next() {
		var chat connector.LoadChatPacket
		err := result.Scan(&chat.Id, &chat.MachineName, &chat.Code, &chat.Date)
		if err != nil {
			log.Fatal(err)
		}
		chats = append(chats, chat)
	}
	return chats, nil
}

func (cdb *ChatDatabase) AddChatMessage(id uuid.UUID, ai bool, content string) error {
	var name string
	if ai {
		name = "AI"
	} else {
		name = "User"
	}
	log.Println("Adding message:", id.String(), "AI=", ai)
	_, err := cdb.db.Exec("INSERT INTO chat_messages(chat_id, rolle, content) VALUES ($1,$2,$3)",
		id.String(), name, content)
	if err != nil {
		return err
	}
	return nil
}

func (cdb *ChatDatabase) GetAllMessages(id uuid.UUID) ([]connector.ChatMessagePacket, error) {
	result, err := cdb.db.Query("SELECT rolle, content FROM chat_messages WHERE chat_id=$1 ORDER BY zeitstempel ASC", id)
	if err != nil {
		return nil, err
	}
	defer func(result *sql.Rows) {
		err := result.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(result)
	var chats []connector.ChatMessagePacket
	for result.Next() {
		var chat connector.ChatMessagePacket
		chat.Id = id
		err := result.Scan(&chat.AI, &chat.Content)
		if err != nil {
			log.Fatal(err)
		}
		chats = append(chats, chat)
	}
	return chats, nil
}

func (cdb *ChatDatabase) GetLastMessage(id uuid.UUID) (connector.ChatMessagePacket, error) {
	result, err := cdb.db.Query(
		"SELECT rolle, content FROM chat_messages WHERE chat_id=$1 ORDER BY zeitstempel DESC LIMIT 1", id)
	if err != nil {
		return connector.ChatMessagePacket{}, err
	}
	defer func(result *sql.Rows) {
		err := result.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(result)
	for result.Next() {
		var chat connector.ChatMessagePacket
		chat.Id = id
		err := result.Scan(&chat.AI, &chat.Content)
		if err != nil {
			log.Fatal(err)
		}
		return chat, nil
	}
	return connector.ChatMessagePacket{}, nil
}

func (cdb *ChatDatabase) GetErrorCodeFromChatId(id uuid.UUID) (int, error) {
	result, err := cdb.db.Query(
		"SELECT fehlercode FROM chats WHERE id=$1", id)
	if err != nil {
		return 0, err
	}
	for result.Next() {
		var code int
		err = result.Scan(&code)
		if err != nil {
			return 0, err
		}
		return code, nil
	}
	return 0, nil
}

func (cdb *ChatDatabase) Connect() error {
	db, err := sql.Open("postgres", conn)
	if err != nil {
		return err
	}

	if err := db.Ping(); err != nil {
		return err
	}
	log.Println("Connected to chat database!")
	cdb.db = db
	return nil
}

func (cdb *ChatDatabase) Close() error {
	log.Println("Closing chat database...")
	return cdb.db.Close()
}
