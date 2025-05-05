# Pion WebRTC Peer Service

A minimal Go-based “answerer” peer for 1:1 WebRTC audio.  
It connects to your signaling server, receives an SDP offer from the iPhone client, answers it, decodes incoming Opus audio → PCM, runs VAD to detect speech start/end, and relays ICE candidates back.

---

## ▶️ Quick Start

1. **Install dependencies**  
```go
       go get github.com/pion/webrtc/v3  
       go get github.com/gorilla/websocket  
       go get github.com/pion/opus  
       go get github.com/asticode/go-webrtcvad  
```

2. **Build & run** 
```shell
       cd services/peer  
       go mod tidy  
       go run webrtc_peer.go  
```

   You should see:  
       Joined signaling server as backend-peer-abc  

---

## 🧱 How It Works

- **Signaling**  
   • Connects to `ws://localhost:8080/ws` as `backend-peer-abc`  
   • Listens for `{ "type":"signal", "from":..., "data":{ "sdp":... } }`  

- **PeerConnection**  
   • Creates a Pion `PeerConnection` answer  
   • Sends back `{ "type":"signal", "data":{ "sdp":<answer> } }`  
   • Relays ICE candidates via the same channel  

- **Audio Handling**  
   • OnTrack: reads RTP packets from the remote Opus track  
   • Decodes Opus → raw PCM (20 ms frames)  
   • Runs WebRTC VAD (mode 3)  
     - Logs `▶️ Speech started` on speech begin  
     - Logs `⏹ Speech ended` after ~200 ms silence  

- **Extension Hooks**  
   • TODOs in code mark where to buffer PCM for your Python agent  
   • TODOs mark where to trigger transcription or barge-in  

---

## 🔧 Postman Smoke-Test

1. **Open Postman → New → WebSocket Request**  
   Connect to:  
       ws://localhost:8080/ws  

2. **Join as iPhone client**  
```json
       { "type":"join", "id":"iphone-123" }  
```

3. **Send a fake SDP offer**  
```json
       {
         "type":"signal",
         "from":"iphone-123",
         "to":"backend-peer-abc",
         "data":{ "sdp":"<your-offer-SDP>" }
       }  
```

4. **Observe**  
   - Postman “Messages” shows the JSON answer from `backend-peer-abc`  
   - Peer logs show “🔊 Got track: …”, “▶️ Speech started”, “⏹ Speech ended”  

---

## ⚙️ Configuration

- **signalingURL**: ws://localhost:8080/ws  
- **peerID**: backend-peer-abc  
- **sampleRate**: 48000 Hz  
- **frameDuration**: 20 ms  
- **VAD mode**: 3 (most aggressive)  

---

Now you have a running Pion backend peer—ready for you to hook in the Python agent at the TODO markers!  