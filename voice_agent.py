import os
import sounddevice as sd
import soundfile as sf
import numpy as np
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
        
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        print("Recording...")
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels
        )
        sd.wait()
        print("Recording finished")
        return recording
    
    def save_audio(self, recording, filename="input.wav"):
        """Save recorded audio to file"""
        write_wav(filename, self.sample_rate, recording)
        return filename
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio using OpenAI's Whisper model"""
        with open(audio_file, "rb") as file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )
        return transcript.text
    
    def get_ai_response(self, text):
        """Get response from OpenAI's GPT model"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    
    def text_to_speech(self, text, output_file="output.wav"):
        """Convert text to speech using OpenAI's TTS model"""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        with open(output_file, 'wb') as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
        return output_file
    
    def play_audio(self, audio_file):
        """Play audio file"""
        data, samplerate = sf.read(audio_file)
        sd.play(data, samplerate)
        sd.wait()

def main():
    agent = VoiceAgent()
    
    # Record audio
    recording = agent.record_audio(duration=5)
    
    # Save the recording
    input_file = agent.save_audio(recording)
    
    # Transcribe the audio
    transcript = agent.transcribe_audio(input_file)
    print(f"Transcription: {transcript}")
    
    # Get AI response
    response = agent.get_ai_response(transcript)
    print(f"AI Response: {response}")
    
    # Convert response to speech
    output_file = agent.text_to_speech(response)
    
    # Play the response
    agent.play_audio(output_file)

if __name__ == "__main__":
    main() 