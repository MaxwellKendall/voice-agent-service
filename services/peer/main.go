package main

import (
	"log"
	"net/url"

	"github.com/baabaaox/go-webrtcvad"
	"github.com/gorilla/websocket"
	"github.com/pion/opus"
	"github.com/pion/webrtc/v3"
)

const (
	signalingURL  = "ws://localhost:8080/ws"
	peerID        = "backend-peer-abc"
	targetID      = "iphone-123"
	sampleRate    = 48000                             // Hz
	channels      = 1                                 // mono
	frameDuration = 20                                // ms
	frameSamples  = sampleRate / 1000 * frameDuration // 960 samples for 20ms
)

type SignalMessage struct {
	Type string      `json:"type"`
	To   string      `json:"to,omitempty"`
	From string      `json:"from,omitempty"`
	ID   string      `json:"id,omitempty"`
	Data interface{} `json:"data,omitempty"`
}

func main() {
	// Connect to signaling server
	u, err := url.Parse(signalingURL)
	if err != nil {
		log.Fatal("Invalid signaling URL:", err)
	}
	ws, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		log.Fatal("Signaling WS error:", err)
	}
	defer ws.Close()

	// Join with our peer ID
	joinMsg := SignalMessage{Type: "join", ID: peerID}
	if err := ws.WriteJSON(joinMsg); err != nil {
		log.Fatal("Join error:", err)
	}

	// Listen for incoming offers
	for {
		var msg SignalMessage
		if err := ws.ReadJSON(&msg); err != nil {
			log.Println("Read signal error:", err)
			return
		}
		if msg.Type == "signal" {
			handleOffer(ws, msg)
		}
	}
}

func handleOffer(ws *websocket.Conn, msg SignalMessage) {
	// Unpack SDP
	data := msg.Data.(map[string]interface{})
	sdp := data["sdp"].(string)

	// Create PeerConnection
	peerConnection, err := webrtc.NewPeerConnection(webrtc.Configuration{})
	if err != nil {
		log.Fatal(err)
	}

	// Set up Opus decoder & VAD
	dec, err := opus.NewDecoder(sampleRate, channels)
	if err != nil {
		log.Fatal("Opus decoder error:", err)
	}
	vad, err := webrtcvad.New()
	if err != nil {
		log.Fatal("VAD init error:", err)
	}
	vad.SetMode(3) // 0=least aggressive .. 3=most aggressive

	// Track speech state
	var (
		inSpeech      bool
		silenceStreak int
	)

	// Handle incoming audio track
	peerConnection.OnTrack(func(track *webrtc.TrackRemote, recv *webrtc.RTPReceiver) {
		log.Println("🔊 Got track:", track.Codec().MimeType)

		go func() {
			for {
				// Read RTP packet
				pkt, _, readErr := track.ReadRTP()
				if readErr != nil {
					log.Println("RTP read error:", readErr)
					return
				}

				// Decode Opus → PCM
				pcm := make([]int16, frameSamples)
				decoded, decodeErr := dec.Decode(pkt.Payload, frameSamples, false)
				if decodeErr != nil {
					log.Println("Opus decode error:", decodeErr)
					continue
				}
				copy(pcm, decoded)

				// Run VAD
				isSpeech, vadErr := vad.IsSpeech(pcm, sampleRate)
				if vadErr != nil {
					log.Println("VAD error:", vadErr)
					continue
				}

				// Speech state machine
				if isSpeech {
					silenceStreak = 0
					if !inSpeech {
						inSpeech = true
						log.Println("▶️ Speech started")
						// TODO: notify agent to start buffering audio
					}
				} else {
					silenceStreak++
					if inSpeech && silenceStreak*frameDuration >= 200 {
						inSpeech = false
						log.Println("⏹ Speech ended")
						// TODO: send buffered audio for transcription
					}
				}
			}
		}()
	})

	// Apply remote SDP
	offer := webrtc.SessionDescription{Type: webrtc.SDPTypeOffer, SDP: sdp}
	if err := peerConnection.SetRemoteDescription(offer); err != nil {
		log.Fatal(err)
	}

	// Create and set answer
	answer, err := peerConnection.CreateAnswer(nil)
	if err != nil {
		log.Fatal(err)
	}
	if err := peerConnection.SetLocalDescription(answer); err != nil {
		log.Fatal(err)
	}

	// Send answer via signaling
	answerMsg := SignalMessage{
		Type: "signal",
		To:   msg.From,
		From: peerID,
		Data: map[string]string{"sdp": answer.SDP},
	}
	if err := ws.WriteJSON(answerMsg); err != nil {
		log.Fatal("Send answer failed:", err)
	}

	// Relay ICE candidates
	peerConnection.OnICECandidate(func(c *webrtc.ICECandidate) {
		if c == nil {
			return
		}
		iceMsg := SignalMessage{
			Type: "signal",
			To:   msg.From,
			From: peerID,
			Data: map[string]interface{}{"candidate": c.ToJSON()},
		}
		ws.WriteJSON(iceMsg)
	})

	// Keep running
	select {}
}
