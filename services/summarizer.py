import logging
from typing import List, Dict, Any, Optional
import openai
from config import Config

logger = logging.getLogger(__name__)

class ChatSummarizer:
    """Service for summarizing WhatsApp chat conversations"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def generate_summary(self, messages: List[Dict[str, Any]], participants: List[str]) -> Dict[str, Any]:
        """
        Generate a structured summary of the chat conversation
        
        Args:
            messages: List of parsed WhatsApp messages
            participants: List of participant usernames
            
        Returns:
            Dictionary containing summary and script lines
        """
        try:
            # Prepare context for the AI
            context = self._prepare_context(messages, participants)
            
            # Generate the summary using OpenAI
            summary_response = self._generate_summary_text(context)
            
            # Generate script lines
            script_lines = self._generate_script_lines(summary_response, participants)
            
            return {
                'summary_text': summary_response,
                'script_lines': script_lines,
                'participants': participants,
                'summary_type': 'dialogue',
                'word_count': len(summary_response.split()),
                'generated_by': self.model
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {'error': str(e)}
    
    def _prepare_context(self, messages: List[Dict[str, Any]], participants: List[str]) -> str:
        """
        Prepare context for the AI summarizer
        
        Args:
            messages: List of parsed messages
            participants: List of participants
            
        Returns:
            Formatted context string
        """
        # Filter out system messages and media messages
        text_messages = [
            msg for msg in messages 
            if msg.get('message_type') == 'text' and msg.get('username') != 'System'
        ]
        
        # Take the most recent messages (limit to avoid token limits)
        recent_messages = text_messages[-100:] if len(text_messages) > 100 else text_messages
        
        # Format messages for context
        formatted_messages = []
        for msg in recent_messages:
            timestamp = msg['timestamp'].strftime('%Y-%m-%d %H:%M')
            formatted_messages.append(
                f"[{timestamp}] {msg['username']}: {msg['content']}"
            )
        
        context = f"""
Participants: {', '.join(participants)}

Recent messages:
{chr(10).join(formatted_messages)}

Please create a concise summary of this WhatsApp group conversation and generate a short dialogue script where each participant shares their key updates or important information from the chat.
"""
        return context
    
    def _generate_summary_text(self, context: str) -> str:
        """
        Generate summary text using OpenAI
        
        Args:
            context: Prepared context string
            
        Returns:
            Generated summary text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that summarizes WhatsApp group conversations. 
                        Your task is to:
                        1. Analyze the conversation and identify key themes, updates, and important information
                        2. Create a concise summary (max 300 words)
                        3. Generate a natural dialogue script where each participant shares their most important update
                        
                        The dialogue should be conversational and engaging, like a group call where everyone shares their news.
                        Keep each person's lines short and natural (1-2 sentences max).
                        Focus on the most recent and relevant information from the chat."""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _generate_script_lines(self, summary_text: str, participants: List[str]) -> List[Dict[str, Any]]:
        """
        Extract script lines from the summary text
        
        Args:
            summary_text: Generated summary text
            participants: List of participants
            
        Returns:
            List of script line dictionaries
        """
        try:
            # Use OpenAI to extract structured script lines
            script_prompt = f"""
Based on this summary, create a structured dialogue script where each participant speaks:

Summary: {summary_text}

Participants: {', '.join(participants)}

Please format the response as a JSON array of objects with this structure:
[
    {{
        "username": "participant_name",
        "line": "what they say",
        "line_number": 1
    }},
    ...
]

Make sure each participant gets at least one line, and the dialogue flows naturally.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates structured dialogue scripts from summaries. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": script_prompt
                    }
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            import json
            script_lines = json.loads(response.choices[0].message.content.strip())
            
            # Validate and clean the script lines
            cleaned_lines = []
            for i, line in enumerate(script_lines):
                if isinstance(line, dict) and 'username' in line and 'line' in line:
                    cleaned_lines.append({
                        'username': line['username'],
                        'line': line['line'],
                        'line_number': i + 1
                    })
            
            return cleaned_lines
        except Exception as e:
            logger.error(f"Error generating script lines: {e}")
            # Fallback: create simple script lines
            return self._create_fallback_script_lines(summary_text, participants)
    
    def _create_fallback_script_lines(self, summary_text: str, participants: List[str]) -> List[Dict[str, Any]]:
        """
        Create fallback script lines if OpenAI parsing fails
        
        Args:
            summary_text: Summary text
            participants: List of participants
            
        Returns:
            List of script line dictionaries
        """
        lines = []
        for i, participant in enumerate(participants):
            lines.append({
                'username': participant,
                'line': f"Hey everyone! Just wanted to share an update from our group chat.",
                'line_number': i + 1
            })
        
        return lines
    
    def generate_bullet_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a bullet-point summary of key updates
        
        Args:
            messages: List of parsed messages
            
        Returns:
            Dictionary containing bullet-point summary
        """
        try:
            # Extract important messages
            important_messages = [msg for msg in messages if msg.get('is_important', False)]
            
            if not important_messages:
                return {
                    'summary_text': "No important updates found in this conversation.",
                    'bullet_points': [],
                    'summary_type': 'bullet_points'
                }
            
            # Group by user
            user_updates = {}
            for msg in important_messages:
                username = msg['username']
                if username not in user_updates:
                    user_updates[username] = []
                user_updates[username].append(msg['content'])
            
            # Create bullet points
            bullet_points = []
            for username, updates in user_updates.items():
                # Take the most recent update from each user
                bullet_points.append({
                    'username': username,
                    'update': updates[-1] if updates else "No specific updates"
                })
            
            summary_text = f"Key updates from {len(user_updates)} participants in the group chat."
            
            return {
                'summary_text': summary_text,
                'bullet_points': bullet_points,
                'summary_type': 'bullet_points',
                'word_count': len(summary_text.split()),
                'generated_by': self.model
            }
        except Exception as e:
            logger.error(f"Error generating bullet summary: {e}")
            return {'error': str(e)} 