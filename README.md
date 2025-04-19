# Custom Voice Agent

A Python-based voice agent that can record audio, transcribe it, generate responses using GPT, and convert the responses back to speech.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the voice agent:
```bash
python voice_agent.py
```

The program will:
1. Record 5 seconds of audio from your microphone
2. Transcribe the audio using OpenAI's Whisper model
3. Generate a response using GPT-3.5-turbo
4. Convert the response to speech using OpenAI's TTS model
5. Play the response through your speakers

## Requirements

- Python 3.8+
- OpenAI API key
- Microphone
- Speakers 