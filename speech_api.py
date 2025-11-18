from flask import Flask, request, jsonify
from groq import Groq  # ✅ Changed from Client to Groq
import os

app = Flask(__name__)

# Get API key from environment variable (more secure for Render)
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Speech-to-Text API',
        'version': '1.0'
    }), 200


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Speech-to-Text endpoint"""
    try:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({'error': 'API key not configured'}), 500

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        language = request.form.get('language', 'en')
        model = request.form.get('model', 'whisper-large-v3')

        print(f"\n{'='*50}")
        print(f"📝 Transcription Request:")
        print(f"   File: {audio_file.filename}")
        print(f"   Language: {language}")
        print(f"   Model: {model}")
        print(f"{'='*50}\n")

        # ✅ FIXED: Use Groq() instead of Client()
        client = Groq(api_key=GROQ_API_KEY)

        # Transcribe
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, audio_file.read()),
            model=model,
            language=language,
            response_format="json"
        )

        text = transcription.text
        print(f"✅ Transcription successful: {text}\n")

        return jsonify({
            'success': True,
            'text': text,
            'language': language,
            'model': model
        }), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to transcribe audio'
        }), 500


@app.route('/transcribe-with-timestamps', methods=['POST'])
def transcribe_with_timestamps():
    """Speech-to-Text with word-level timestamps"""
    try:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({'error': 'API key not configured'}), 500

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        language = request.form.get('language', 'en')
        model = request.form.get('model', 'whisper-large-v3')

        # ✅ FIXED: Use Groq() here too
        client = Groq(api_key=GROQ_API_KEY)

        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, audio_file.read()),
            model=model,
            language=language,
            response_format="verbose_json"
        )

        return jsonify({
            'success': True,
            'text': transcription.text,
            'language': transcription.language,
            'duration': transcription.duration,
            'segments': transcription.segments
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/')
def home():
    return jsonify({
        'message': 'Speech-to-Text API',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'transcribe': '/transcribe',
            'transcribe_with_timestamps': '/transcribe-with-timestamps'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("\n" + "="*60)
    print("🎤 SPEECH-TO-TEXT API SERVER")
    print("="*60)
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("⚠️ WARNING: Please add your Groq API key!")
    else:
        print("✅ API Key: Configured")
    print(f"\n🌐 Server: http://0.0.0.0:{port}")
    print("="*60 + "\n")
    app.run(debug=True, port=port, host='0.0.0.0')



