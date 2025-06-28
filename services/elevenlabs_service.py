import os
import logging
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from config import Config

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service for ElevenLabs TTS and assistant integration"""
    
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.base_url = Config.ELEVENLABS_BASE_URL
        self.headers = {
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs
        
        Returns:
            List of available voices
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=self.headers
            )
            response.raise_for_status()
            
            voices = response.json().get('voices', [])
            return [
                {
                    'voice_id': voice['voice_id'],
                    'name': voice['name'],
                    'category': voice.get('category', 'general'),
                    'description': voice.get('description', ''),
                    'labels': voice.get('labels', {}),
                    'sample_url': voice.get('sample_url')
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return []
    
    def generate_speech(self, text: str, voice_id: str, output_path: str) -> Dict[str, Any]:
        """
        Generate speech from text using ElevenLabs TTS
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            output_path: Path to save the audio file
            
        Returns:
            Dictionary with generation results
        """
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'file_size': file_size,
                'generation_id': str(uuid.uuid4()),
                'duration': self._estimate_duration(text)
            }
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_speech_stream(self, text: str, voice_id: str) -> Optional[bytes]:
        """
        Generate speech and return as bytes (for streaming)
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.content
        except Exception as e:
            logger.error(f"Error generating speech stream: {e}")
            return None
    
    def generate_batch_speech(self, script_lines: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
        """
        Generate speech for multiple script lines
        
        Args:
            script_lines: List of script line dictionaries
            session_id: Chat session ID
            
        Returns:
            List of generation results
        """
        results = []
        
        for line in script_lines:
            username = line['username']
            text = line['line']
            line_number = line['line_number']
            
            # Generate filename
            filename = f"{username.lower()}_line{line_number}.mp3"
            output_path = os.path.join(Config.AUDIO_FOLDER, session_id, filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get voice ID for user (you might want to implement user voice mapping)
            voice_id = self._get_voice_for_user(username)
            
            if voice_id:
                result = self.generate_speech(text, voice_id, output_path)
                result.update({
                    'username': username,
                    'line_number': line_number,
                    'filename': filename
                })
            else:
                result = {
                    'success': False,
                    'error': f"No voice found for user {username}",
                    'username': username,
                    'line_number': line_number,
                    'filename': filename
                }
            
            results.append(result)
        
        return results
    
    def _get_voice_for_user(self, username: str) -> Optional[str]:
        """
        Get voice ID for a user (placeholder implementation)
        
        Args:
            username: Username
            
        Returns:
            Voice ID or None
        """
        # This is a placeholder - you should implement proper user-voice mapping
        # For now, return a default voice
        default_voices = {
            '21m00Tcm4TlvDq8ikWAM': 'Rachel',
            'AZnzlk1XvdvUeBnXmlld': 'Domi',
            'EXAVITQu4vr4xnSDxMaL': 'Bella'
        }
        
        # Simple hash-based assignment
        import hashlib
        hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
        voice_ids = list(default_voices.keys())
        selected_voice = voice_ids[hash_value % len(voice_ids)]
        
        return selected_voice
    
    def _estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on text length
        
        Args:
            text: Text content
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: 150 words per minute
        word_count = len(text.split())
        return (word_count / 150) * 60
    
    def create_voice(self, name: str, description: str, files: List[str]) -> Optional[str]:
        """
        Create a custom voice using ElevenLabs
        
        Args:
            name: Voice name
            description: Voice description
            files: List of audio file paths for training
            
        Returns:
            Voice ID if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/voices/add"
            
            # Prepare files for upload
            files_data = []
            for file_path in files:
                with open(file_path, 'rb') as f:
                    files_data.append(('files', f))
            
            data = {
                'name': name,
                'description': description
            }
            
            response = requests.post(
                url,
                headers={'xi-api-key': self.api_key},
                data=data,
                files=files_data
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('voice_id')
        except Exception as e:
            logger.error(f"Error creating voice: {e}")
            return None
    
    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a custom voice
        
        Args:
            voice_id: Voice ID to delete
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/voices/{voice_id}"
            
            response = requests.delete(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting voice: {e}")
            return False
    
    def get_voice_settings(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice settings
        
        Args:
            voice_id: Voice ID
            
        Returns:
            Voice settings dictionary
        """
        try:
            url = f"{self.base_url}/voices/{voice_id}/settings/edit"
            
            response = requests.get(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting voice settings: {e}")
            return None
    
    def update_voice_settings(self, voice_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update voice settings
        
        Args:
            voice_id: Voice ID
            settings: Settings dictionary
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/voices/{voice_id}/settings/edit"
            
            response = requests.post(
                url,
                headers=self.headers,
                json=settings
            )
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            return False
    
    def get_usage_info(self) -> Optional[Dict[str, Any]]:
        """
        Get API usage information
        
        Returns:
            Usage information dictionary
        """
        try:
            url = f"{self.base_url}/user/subscription"
            
            response = requests.get(
                url,
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting usage info: {e}")
            return None 