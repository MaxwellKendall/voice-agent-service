# 🗺️ High-Performance Voice Agent Backend - Roadmap

## 🎯 Goal
Enable ultra-fast 1:1 real-time communication between iPhone and AI agent using WebRTC, OpenAI, and Python — with <1s end-to-end latency.

---

## 📐 System Overview
iPhone WebRTC Mic 🔊
⇅ Signaling (WebSocket - Go)
⇅ Media (Pion WebRTC - Go)
⇅ Audio to Python Agent (Redis or UNIX socket)
⇅ Agent (Whisper → OpenAI → TTS)
⇅ Audio Stream to iPhone (HTTP2 / WebSocket)

---

## 🔧 Components

| Layer             | Tech                        | Purpose                                 |
|------------------|-----------------------------|-----------------------------------------|
| Signaling         | Go + Gorilla WebSocket      | Exchange SDP/ICE offers fast            |
| Media Server      | Go + Pion                   | Consume & optionally stream audio       |
| Audio Bridge      | Redis Streams / UNIX socket | Send PCM audio to Python agent          |
| Agent Logic       | Python + FastAPI            | Transcribe, reason, respond             |
| TTS Audio Out     | HTTP2/WS stream             | Send TTS audio back to iPhone           |
| Observability     | Prometheus + OTEL           | Debug latency & trace sessions          |

---

## 🧱 Phase Roadmap

### ✅ Phase 1: MVP Loop
- [ ] Implement Go WebSocket signaling server
- [ ] Stand up Go WebRTC server (Pion)
- [ ] Connect iPhone → Pion via signaling
- [ ] Forward decoded audio to Python via socket
- [ ] Transcribe → respond via OpenAI
- [ ] Generate TTS response
- [ ] Stream audio back to iPhone over HTTP

### ⚙️ Phase 2: Real-Time TTS Streaming
- [ ] Implement chunked HTTP2 / WS audio stream
- [ ] Add barge-in and interruption handling

### 🚀 Phase 3: Scaling & Observability
- [ ] Run all services in containers (Docker)
- [ ] Add Redis/NATS for session state/fanout
- [ ] Add Prometheus + OpenTelemetry for tracing
- [ ] Auto-scale agent workers + media servers

---

## 🛠 Dev Stack

- **Languages**: Go (signaling/media), Python (agent)
- **Infra**: Redis, Prometheus, Docker, Kubernetes (eventually)
- **Audio**: Opus → PCM → Whisper → OpenAI → TTS → stream

---

## 🎁 Deliverables

- Modular services: signaling, media, agent
- Low-latency pipelines
- Scalable infrastructure
- Easy to debug and extend