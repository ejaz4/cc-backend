# test_elevenlabs_service.py

import os
from elevenlabs_service import ElevenLabsService  # adjust import path if needed
from config import Config


def test_generate_basic_speech():
    # Set up
    service = ElevenLabsService()
    test_session_id = "test_session"
    test_script = ["TestUser: Hello, this is a test of the ElevenLabs TTS service."]

    # Run
    results = service.generate_batch_speech(script_lines=test_script, session_id=test_session_id)

    # Check and print results
    for result in results:
        print("==== Result ====")
        print(f"Success: {result.get('success')}")
        print(f"File Path: {result.get('file_path')}")
        print(f"Voice ID: {result.get('voice_id')}")
        print(f"Error: {result.get('error')}")
        print("================")

        # Check if file was saved
        if result.get('success') and os.path.exists(result['file_path']):
            print(f"MP3 file generated successfully: {result['file_path']}")
        else:
            print("MP3 file was not generated.")



if __name__ == "__main__":
    test_generate_basic_speech()
