package main

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{}
var peers = make(map[string]*websocket.Conn)

func main() {
	http.HandleFunc("/ws", handleWebSocket)

	log.Println("Signaling server started on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}
	defer conn.Close()

	var peerID string

	for {
		var msg map[string]interface{}
		if err := conn.ReadJSON(&msg); err != nil {
			log.Println("Read error:", err)
			break
		}

		switch msg["type"] {
		case "join":
			peerID = msg["id"].(string)
			peers[peerID] = conn
			log.Println("Peer joined:", peerID)

		case "signal":
			targetID := msg["to"].(string)
			if targetConn, ok := peers[targetID]; ok {
				if err := targetConn.WriteJSON(msg); err != nil {
					log.Println("Write to", targetID, "failed:", err)
				}
			}

		case "leave":
			delete(peers, peerID)
			log.Println("Peer left:", peerID)
			return
		}
	}
}