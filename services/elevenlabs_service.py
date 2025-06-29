import os
import logging
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from pydub import AudioSegment
from ..config import Config

from ..database.repository import UserProfileRepository

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service for ElevenLabs TTS integration with personality-based voice generation"""
    
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        self.user_profile_repo = UserProfileRepository()
        self.SPEAKER_VOICE_IDS = {
            "viraj": "Ext7H3eEv8VE8fllrG5V",
                             "akshith": "5AoQXpmMtIJan2CwtAOc",
                             "lakshan": "umz7RhlNzd4xcAqREdXt",
                             "keanu czirjak": "bFzANtxrZVStytIgIj6n",
                             "ejaz": "4EzftP6bvnPeQhye9MOz",
                            "narrator": "EXAVITQu4vr4xnSDxMaL"}

    def get_available_voices(self) -> List[str]:
        """Get list of available ElevenLabs voices"""
        try:
            response = requests.get(f"{self.base_url}/voices", headers=self.headers)
            response.raise_for_status()

            # voices_data = response.json() forget this
            voices = {"Viraj": "Ext7H3eEv8VE8fllrG5V",
                      "Akshith": "5AoQXpmMtIJan2CwtAOc",
                      "Lakshan": "umz7RhlNzd4xcAqREdXt",
                      "Keanu": "bFzANtxrZVStytIgIj6n",
                      "Ejaz": "4EzftP6bvnPeQhye9MOz"}
            # name:id

            # for voice in voices_data.get('voices', []):
            #     voice_info = {
            #         'voice_id': voice.get('voice_id'),
            #         'name': voice.get('name'),
            #         'category': voice.get('category'),
            #         'description': voice.get('description'),
            #         'labels': voice.get('labels', {}),
            #         'preview_url': voice.get('preview_url'),
            #         'similarity_boost': voice.get('similarity_boost'),
            #         'stability': voice.get('stability'),
            #         'style': voice.get('style'),
            #         'use_speaker_boost': voice.get('use_speaker_boost')
            #     }
            #     voices.append(voice_info)

            return voices.keys()

        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def generate_batch_speech_with_profiles(self, script_lines: List[str], session_id: str, participants: List[str], main_user: str, platform: str) -> List[Dict[str, Any]]:
        """
        Generate TTS audio for script lines with personality-based voice settings
        
        Args:
            script_lines: List of script lines to convert to speech
            session_id: Conversation session ID
            participants: List of participant usernames
            main_user: Main user ID
            platform: Platform name
            
        Returns:
            List of generation results
        """
        results = []
        
        # Create audio directory
        audio_dir = os.path.join(Config.AUDIO_FOLDER, session_id)
        os.makedirs(audio_dir, exist_ok=True)
        
        for i, line in enumerate(script_lines):
            try:
                # Extract speaker from line (format: "Speaker: content")
                if ':' in line:
                    speaker, content = line.split(':', 1)
                    speaker = speaker.strip()
                    content = content.strip()
                else:
                    speaker = participants[0] if participants else "Unknown"
                    content = line
                
                # Get user profile for personality-based voice settings
                profile = self.user_profile_repo.find_by_username(speaker, platform, main_user)
                voice_settings = self._get_personality_based_voice_settings(profile, speaker)
                
                # Generate audio
                result = self._generate_speech_with_settings(
                    content, 
                    speaker, 
                    session_id, 
                    i + 1, 
                    voice_settings
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error generating speech for line {i + 1}: {e}")
                results.append({
                    'success': False,
                    'username': speaker if 'speaker' in locals() else 'Unknown',
                    'line_number': i + 1,
                    'error': str(e)
                })
        
        return results
    
    def generate_batch_speech(self, script_lines: List[str], session_id: str) -> List[Dict[str, Any]]:
        """
        Generate TTS audio for script lines (legacy method)
        
        Args:
            script_lines: List of script lines to convert to speech
            session_id: Conversation session ID
            
        Returns:
            List of generation results
        """
        # Use the new method with default settings
        return self.generate_batch_speech_with_profiles(script_lines, session_id, [], 'default_user', 'unknown')
    
    def _get_personality_based_voice_settings(self, profile: Optional[Dict[str, Any]], speaker: str) -> Dict[str, Any]:
        """Get voice settings based on user personality profile"""
        default_settings = {
            'voice_id': 'pNInz6obpgDQGcFmaJgB',  # Default voice (Adam)
            'stability': 0.5,
            'similarity_boost': 0.75,
            'style': 0.0,
            'use_speaker_boost': True
        }
        
        if not profile:
            return default_settings
        
        # Get personality traits
        personality_traits = profile.get('personality_traits', [])
        communication_style = profile.get('communication_style', {})
        relationship_type = profile.get('relationship_type', 'friend')
        trust_score = profile.get('trust_score', 0.5)
        
        # Adjust voice settings based on personality
        settings = default_settings.copy()
        
        # Voice selection based on personality
        if 'professional' in personality_traits:
            settings['voice_id'] = 'pNInz6obpgDQGcFmaJgB'  # Adam - professional
        elif 'friendly' in personality_traits or 'humorous' in personality_traits:
            settings['voice_id'] = 'VR6AewLTigWG4xSOukaG'  # Josh - friendly
        elif 'grateful' in personality_traits or 'apologetic' in personality_traits:
            settings['voice_id'] = 'EXAVITQu4vr4xnSDxMaL'  # Bella - warm
        elif 'helpful' in personality_traits:
            settings['voice_id'] = '21m00Tcm4TlvDq8ikWAM'  # Rachel - helpful
        
        # Adjust stability based on communication style
        if communication_style.get('exclamation_heavy'):
            settings['stability'] = 0.3  # More expressive
        elif communication_style.get('formal'):
            settings['stability'] = 0.7  # More stable
        
        # Adjust similarity boost based on relationship
        if relationship_type == 'family':
            settings['similarity_boost'] = 0.9  # Higher similarity for family
        elif relationship_type == 'colleague':
            settings['similarity_boost'] = 0.6  # Lower similarity for colleagues
        
        # Adjust style based on emoji usage
        if communication_style.get('emoji_heavy'):
            settings['style'] = 0.3  # More expressive style
        
        # Use existing voice_id if available
        if profile.get('voice_id'):
            settings['voice_id'] = profile['voice_id']
        
        return settings
    
    def _generate_speech_with_settings(self, text: str, speaker: str, session_id: str, line_number: int, voice_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speech with specific voice settings"""
        try:
            # Prepare request payload
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": voice_settings.get('stability', 0.5),
                    "similarity_boost": voice_settings.get('similarity_boost', 0.75),
                    "style": voice_settings.get('style', 0.0),
                    "use_speaker_boost": voice_settings.get('use_speaker_boost', True)
                }
            }
            
            # Make API request
            voice_id = voice_settings.get('voice_id', 'JBFqnCBsd6RMkjVDRZzb')
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Save audio file
            filename = f"{speaker}_{line_number:03d}.mp3"
            file_path = os.path.join(Config.AUDIO_FOLDER, session_id, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Extract generation ID from response headers if available
            generation_id = response.headers.get('xi-generation-id', str(uuid.uuid4()))
            
            return {
                'success': True,
                'username': speaker,
                'line_number': line_number,
                'filename': filename,
                'file_path': file_path,
                'voice_id': voice_id,
                'file_size': file_size,
                'generation_id': generation_id,
                'voice_settings': voice_settings,
                'emotion_context': self._extract_emotion_context(text, voice_settings)
            }
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {
                'success': False,
                'username': speaker,
                'line_number': line_number,
                'error': str(e)
            }
    
    def _extract_emotion_context(self, text: str, voice_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Extract emotional context from text for voice generation"""
        text_lower = text.lower()
        
        emotion_context = {
            'detected_emotions': [],
            'intensity': 'medium',
            'tone': 'neutral'
        }
        
        # Detect emotions from text
        if any(word in text_lower for word in ['happy', 'excited', 'great', 'awesome', 'amazing']):
            emotion_context['detected_emotions'].append('joy')
            emotion_context['tone'] = 'positive'
        elif any(word in text_lower for word in ['sad', 'sorry', 'unfortunate', 'disappointed']):
            emotion_context['detected_emotions'].append('sadness')
            emotion_context['tone'] = 'negative'
        elif any(word in text_lower for word in ['urgent', 'important', 'critical', 'emergency']):
            emotion_context['detected_emotions'].append('urgency')
            emotion_context['intensity'] = 'high'
        elif any(word in text_lower for word in ['calm', 'relaxed', 'peaceful', 'gentle']):
            emotion_context['detected_emotions'].append('calmness')
            emotion_context['intensity'] = 'low'
        
        # Adjust voice settings based on emotions
        if 'joy' in emotion_context['detected_emotions']:
            voice_settings['stability'] = min(voice_settings.get('stability', 0.5) - 0.1, 0.3)
        elif 'urgency' in emotion_context['detected_emotions']:
            voice_settings['stability'] = min(voice_settings.get('stability', 0.5) - 0.2, 0.2)
        
        return emotion_context
    
    def clone_voice(self, name: str, description: str, files: List[str]) -> Optional[str]:
        """
        Clone a voice using audio samples
        
        Args:
            name: Voice name
            description: Voice description
            files: List of audio file paths
            
        Returns:
            Voice ID if successful, None otherwise
        """
        try:
            # Prepare files for upload
            files_data = []
            for file_path in files:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        files_data.append(('files', f))
            
            if not files_data:
                return None
            
            # Prepare form data
            data = {
                'name': name,
                'description': description
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/voices/add",
                headers={"xi-api-key": self.api_key},
                data=data,
                files=files_data
            )
            response.raise_for_status()
            
            voice_data = response.json()
            return voice_data.get('voice_id')
            
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            return None

    
    def get_voice_info(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific voice
        
        Args:
            voice_id: Voice ID
            
        Returns:
            Voice information dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices/{voice_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting voice info: {e}")
            return None
    
    def update_voice_settings(self, voice_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update voice settings
        
        Args:
            voice_id: Voice ID
            settings: New voice settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/voices/{voice_id}/settings/edit",
                headers=self.headers,
                json=settings
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            return False
    
    def assign_voice_to_user(self, user_id: str, voice_id: str, voice_name: str) -> bool:
        """
        Assign a voice to a user profile
        
        Args:
            user_id: User profile ID
            voice_id: ElevenLabs voice ID
            voice_name: Voice name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update user profile with voice information
            update_data = {
                'voice_id': voice_id,
                'voice_name': voice_name
            }
            
            success = self.user_profile_repo.update(user_id, update_data)
            return success
            
        except Exception as e:
            logger.error(f"Error assigning voice to user: {e}")
            return False
    
    def get_user_voice_preferences(self, main_user: str, platform: str = None) -> Dict[str, Any]:
        """
        Get voice preferences for all users of a main user
        
        Args:
            main_user: Main user ID
            platform: Platform filter (optional)
            
        Returns:
            Dictionary of user voice preferences
        """
        try:
            profiles = self.user_profile_repo.find_by_main_user(main_user, platform)
            
            voice_preferences = {}
            for profile in profiles:
                username = profile.get('username')
                if username:
                    voice_preferences[username] = {
                        'voice_id': profile.get('voice_id'),
                        'voice_name': profile.get('voice_name'),
                        'personality_traits': profile.get('personality_traits', []),
                        'communication_style': profile.get('communication_style', {})
                    }
            
            return voice_preferences
            
        except Exception as e:
            logger.error(f"Error getting user voice preferences: {e}")
            return {}

    def generate_voice_audio(self, text, voice_id, output_path):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def create_groupchat_audio(self, convo_json, final_output="groupchat_output.mp3"):
        audio_segments = []

        for entry in convo_json:
            speaker = entry["sender_name"]
            text = entry["script"]
            voice_id = self.SPEAKER_VOICE_IDS.get(speaker.lower())

            if not voice_id:
                raise ValueError(f"No voice ID mapped for speaker: {speaker}")

            temp_file = f"temp_{uuid.uuid4()}.mp3"
            self.generate_voice_audio(text, voice_id, temp_file)
            segment = AudioSegment.from_mp3(temp_file)
            audio_segments.append(segment)
            os.remove(temp_file)

        combined = sum(audio_segments[1:], audio_segments[0])  # Concatenate all
        combined.export(final_output, format="mp3")
        print(f"Generated audio file: {final_output}")

    def master(self, summarised_json):
        output_files = []

        # Step 1: Generate narrator extract audio
        extract_text = summarised_json[0].get("extract")
        narrator_voice_id = self.SPEAKER_VOICE_IDS.get("narrator")

        if not narrator_voice_id:
            raise ValueError("Narrator voice ID not configured.")

        extract_file = f"narrator_{uuid.uuid4()}.mp3"
        self.generate_voice_audio(extract_text, narrator_voice_id, extract_file)
        output_files.append(extract_file)

        # Step 2: Generate chat message audios
        for entry in summarised_json[1:]:
            speaker = entry["sender_name"]
            text = entry["script"]
            voice_id = self.SPEAKER_VOICE_IDS.get(speaker.lower())

            if not voice_id:
                raise ValueError(f"No voice ID mapped for speaker: {speaker}")

            temp_file = f"{speaker.lower()}_{uuid.uuid4()}.mp3"
            self.generate_voice_audio(text, voice_id, temp_file)
            output_files.append(temp_file)

        return output_files


eserv = ElevenLabsService()
eserv.master([
  { "extract": "Keanu starts the chat hyped, asking everyone what's up, and Ejaz and Mansa reply back with their usual chill vibes. They’re just catching up and keeping it casual." },
  { "sender_name": "Keanu Czirjak", "script": "Hey guys! What's up!!! I'm just here vibing and checking in with y'all." },
  { "sender_name": "ejaz", "script": "Yoooo Keanu! Just chillin, what's good with you?" },
  { "sender_name": "akshith", "script": "Wsup g! Nothing much, just vibing here. What's new?" }
])