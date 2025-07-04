# Signaling Server

A minimal WebSocket–based signaling service for 1:1 WebRTC connections.  
It lets any two peers (e.g. your iPhone client and your backend WebRTC peer) rendezvous, exchange SDP offers/answers and ICE candidates, then communicate audio/video directly.

---

## ▶️ Quick Start

1. **Install deps:**
```go  
    go get github.com/gorilla/websocket
```

2. **Run server:**  
```go  
    go run main.go  
```
Listens on `:8080` at `/ws`.

## 🔧 Postman Smoke-Test

1. **Open Postman → New → WebSocket Request**  
   URL: `ws://localhost:8080/ws` → **Connect**

2. **Peer 1 “join”**  
```json
    { "type":"join", "id":"peer1" }  
```
   —Check server log: `Peer joined: peer1`

3. **Peer 2 (new WS tab) “join”**  
```json
    { "type":"join", "id":"peer2" }  
```
   —Log: `Peer joined: peer2`

4. **Peer 1 → Peer 2 “signal”**  
```json
    {
      "type":"signal",
      "from":"peer1",
      "to":"peer2",
      "data": { "sdp":"fake-offer-SDP" }
    }  
```
   —Switch to Peer 2 tab: you should see this message.

5. **Peer 2 → Peer 1 “signal”**  
```json
    {
      "type":"signal",
      "from":"peer2",
      "to":"peer1",
      "data": { "sdp":"fake-answer-SDP" }
    }
```
   —Peer 1 tab receives it.

6. **Leave**  
```json
    { "type":"leave" }  
```
   —Connection closes; server log: `Peer left: peerX`

---

## 📦 Message Types

- **join**  
```json
    { "type":"join", "id":"<your-peer-id>" }
```
- **signal**  
```json
    { "type":"signal", "from":"A","to":"B","data":{…} }
```
- **leave**  
```json
    { "type":"leave" }
```

Now your peers can complete the SDP/ICE handshake and stream media directly—this server only relays control messages.