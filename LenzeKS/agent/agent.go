package agent

import (
	"LenzeKS/connector"
	"LenzeKS/connector/mobile"
	"LenzeKS/connector/opcua"
	"LenzeKS/connector/sqldb"
	"bytes"
	"fmt"
	"log"
	"os/exec"
	"sync"

	"github.com/google/uuid"
)

var conn opcua.Connector
var ChatDB sqldb.ChatDatabase
var wg sync.WaitGroup

func Start() {

	wg.Add(1)
	err := conn.Start(&wg, func(errorID interface{}, machineName interface{}, err error) {
		if err == nil && errorID.(uint16) > 0 {
			log.Println("New error ID:", errorID, "on machine:", machineName)
			NotifyNewErrorCode(machineName.(string),
				int(errorID.(uint16)))
		}
	})
	if err != nil {
		log.Fatal(err)
	}
	defer func(connector *opcua.Connector) {
		err := connector.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(&conn)

	err = ChatDB.Connect()
	if err != nil {
		log.Fatal(err)
	}
	defer func(chatDB *sqldb.ChatDatabase) {
		err := chatDB.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(&ChatDB)

	wg.Add(1)
	http := connector.HttpService{}
	err = http.Start(&wg, func() ([]connector.LoadChatPacket, error) {
		return ChatDB.GetAllChats()
	},
		func(u uuid.UUID, onlyLast bool) ([]connector.ChatMessagePacket, error) {
			if onlyLast {
				single := make([]connector.ChatMessagePacket, 1)
				single[0], err = ChatDB.GetLastMessage(u)
				if err != nil {
					return nil, err
				}
				return single, err
			} else {
				return ChatDB.GetAllMessages(u)
			}
		},
		func(packet connector.ChatMessagePacket) {
			err := ChatDB.AddChatMessage(packet.Id, false, packet.Content)
			if err != nil {
				log.Fatal(err)
				return
			}
			code, err := ChatDB.GetErrorCodeFromChatId(packet.Id)
			if err != nil {
				log.Fatal(err)
			}
			result := runPythonAI(fmt.Sprintf("%s. Fehlercode %d", packet.Content, code))
			err = ChatDB.AddChatMessage(packet.Id, true, result)
			if err != nil {
				log.Fatal(err)
			}
			//user now has to periodically check for new answers
		})
	if err != nil {
		log.Fatal(fmt.Errorf("error starting http service: %w", err))
	}

	wg.Wait()
}

func runPythonAI(prompt string) string {
	arg := prompt
	cmd := exec.Command("python", "cli.py", arg)

	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr

	cmd.Dir = "./AI"

	if err := cmd.Run(); err != nil {
		fmt.Println("error while executing python ai agent:", err)
		fmt.Println("stderr:", stderr.String())
		log.Fatal(err)
	}

	result := out.String()
	fmt.Println("Result:", result)
	return result
}

func NotifyNewErrorCode(machineName string, code int) {
	if code != 0 {
		mobile.Send("Maschinenfehler!", fmt.Sprintf("Fehlercode %d bei %s", code, machineName))
	}

	result := runPythonAI(fmt.Sprintf("Fehler %d", code))

	id, err := ChatDB.CreateChat(machineName, code)
	if err != nil {
		log.Fatal(fmt.Errorf("error while creating chat in database: %w", err))
	}
	err = ChatDB.AddChatMessage(id, true, result)
	if err != nil {
		log.Fatal(fmt.Errorf("error while sending chat message: %w", err))
	}

}
