import os
import queue
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write as write_wav
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.sample_rate = 44100
        self.channels = 1
        self.block_size = 4096
        
    def stream_audio(self, duration=5):
        """Stream audio from microphone for a fixed duration"""
        print("\nRecording for", duration, "seconds...")
        
        # Calculate total frames needed
        total_frames = int(duration * self.sample_rate)
        frames_read = 0
        audio_data = []
        
        def callback(indata, frames, time, status):
            nonlocal frames_read
            if status:
                print(f"Status: {status}")
            audio_data.append(indata.copy())
            frames_read += frames
            remaining = duration - (frames_read / self.sample_rate)
            if remaining > 0:
                print(f"\rRecording... {remaining:.1f}s remaining", end="", flush=True)
        
        stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            callback=callback
        )
        
        with stream:
            sd.sleep(int(duration * 1000))
        
        print("\nProcessing...")
        return np.concatenate(audio_data)
    
    def save_audio(self, recording, filename="input.wav"):
        """Save recorded audio to file"""
        write_wav(filename, self.sample_rate, recording)
        return filename
    
    def stream_transcribe(self, audio_file):
        """Stream transcribe audio using OpenAI's Whisper model"""
        with open(audio_file, "rb") as file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )
        return transcript.text
    
    def stream_response(self, text):
        """Stream response from OpenAI's GPT model"""
        response_stream = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": text}
            ],
            stream=True
        )
        
        full_response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)
        print()
        return full_response
    
    def stream_tts_and_play(self, text):
        """Stream TTS conversion and play audio in real-time"""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save the audio to a temporary file
        temp_file = "temp.wav"
        with open(temp_file, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        # Play the audio
        data, samplerate = sf.read(temp_file)
        sd.play(data, samplerate)
        sd.wait()
        
        # Clean up temporary file
        os.remove(temp_file)

def main():
    agent = VoiceAgent()
    
    while True:
        try:
            # Stream audio input
            recording = agent.stream_audio(duration=5)
            
            # Save the recording (temporary, for Whisper API)
            input_file = agent.save_audio(recording)
            
            # Stream transcribe the audio
            transcript = agent.stream_transcribe(input_file)
            print(f"\nTranscription: {transcript}")
            
            # Stream get AI response
            print("\nAI Response:")
            response = agent.stream_response(transcript)
            
            # Stream TTS and play
            agent.stream_tts_and_play(response)
            
            # Clean up temporary file
            os.remove(input_file)
            
            print("\nReady for next input...")
            
        except KeyboardInterrupt:
            print("\nStopping voice agent...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main() 