import logging
from typing import List, Dict, Any, Optional
import openai
from config import Config
import json
import re


logger = logging.getLogger(__name__)

class ChatSummarizer:
    """Service for generating AI-powered chat summaries with personality context"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_summary_with_context(self, messages: List[Dict[str, Any]], participants: List[str], user_contexts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary with personality and relationship context
        
        Args:
            messages: List of conversation messages
            participants: List of participant usernames
            user_contexts: Dictionary of user context data for each participant
            
        Returns:
            Summary data with script lines and context
        """
        try:
            # Prepare context information
            context_prompt = self._build_context_prompt(participants, user_contexts)
            
            # Prepare messages for summarization
            conversation_text = self._format_conversation(messages)
            
            # Create system prompt with context
            system_prompt = f"""You are an expert conversation summarizer for a Gen-Z focused app. Your task is to create engaging, concise summaries of group conversations that capture the key updates and dynamics.

{context_prompt}

Create a summary that:
1. Captures the most important updates and key points
2. Maintains the personality and communication style of each person
3. Highlights relationship dynamics and context
4. Is engaging and easy to listen to as audio
5. Focuses on actionable information and social updates

Format your response as a JSON object with:
- summary_text: A brief overview paragraph
- script_lines: Array of dialogue lines for TTS generation
- participants: List of participants involved
- personality_context: How personalities influenced the summary
- relationship_context: Key relationship dynamics
- tone_analysis: Overall conversation tone and mood
- word_count: Total word count of script lines

Each script line should be:
- 1-2 sentences maximum
- Natural and conversational
- Include the speaker's name
- Capture their personality and communication style
- Focus on key updates or important points

Example format:
{{
    "summary_text": "Brief overview...",
    "script_lines": [
        "{{speaker}}: {{content}}",
        "{{speaker}}: {{content}}"
    ],
    "participants": ["user1", "user2"],
    "personality_context": {{...}},
    "relationship_context": {{...}},
    "tone_analysis": {{...}},
    "word_count": 150
}}"""

            # Generate summary with OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please summarize this conversation:\n\n{conversation_text}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse response
            summary_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', summary_content, re.DOTALL)
                if json_match:
                    summary_data = json.loads(json_match.group())
                else:
                    # Fallback: create structured response
                    summary_data = self._create_fallback_summary(summary_content, participants)
                
                # Validate and enhance summary data
                summary_data = self._validate_and_enhance_summary(summary_data, participants, user_contexts)
                
                return summary_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                # Create fallback summary
                return self._create_fallback_summary(summary_content, participants)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {'error': str(e)}
    
    def generate_summary(self, messages: List[Dict[str, Any]], participants: List[str]) -> Dict[str, Any]:
        """
        Generate basic summary (legacy method)
        
        Args:
            messages: List of conversation messages
            participants: List of participant usernames
            
        Returns:
            Summary data
        """
        # Use context-aware method with empty contexts
        empty_contexts = {participant: {} for participant in participants}
        return self.generate_summary_with_context(messages, participants, empty_contexts)
    
    def _build_context_prompt(self, participants: List[str], user_contexts: Dict[str, Any]) -> str:
        """Build context prompt from user profiles and relationship data"""
        context_parts = []
        
        for participant, context in user_contexts.items():
            if not context:
                continue
                
            profile = context.get('profile', {})
            relationship_type = context.get('relationship_type', 'friend')
            personality_traits = context.get('personality_traits', [])
            interests = context.get('interests', [])
            trust_score = context.get('trust_score', 0.5)
            
            context_part = f"\n{participant}:"
            context_part += f"\n- Relationship: {relationship_type}"
            
            if personality_traits:
                context_part += f"\n- Personality: {', '.join(personality_traits)}"
            
            if interests:
                context_part += f"\n- Interests: {', '.join(interests)}"
            
            context_part += f"\n- Trust level: {trust_score:.1f}/1.0"
            
            # Add communication style if available
            if profile.get('communication_style'):
                style = profile['communication_style']
                style_desc = []
                if style.get('emoji_heavy'):
                    style_desc.append('uses many emojis')
                if style.get('formal'):
                    style_desc.append('formal language')
                if style.get('casual'):
                    style_desc.append('casual language')
                if style.get('question_heavy'):
                    style_desc.append('asks many questions')
                if style.get('exclamation_heavy'):
                    style_desc.append('uses many exclamations')
                
                if style_desc:
                    context_part += f"\n- Communication style: {', '.join(style_desc)}"
            
            context_parts.append(context_part)
        
        if context_parts:
            return "User Context:\n" + "\n".join(context_parts)
        else:
            return "No specific user context available."
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation messages for summarization"""
        formatted_lines = []
        
        for msg in messages:
            username = msg.get('username', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp')
            
            if timestamp:
                # Format timestamp
                if hasattr(timestamp, 'strftime'):
                    time_str = timestamp.strftime('%H:%M')
                else:
                    time_str = str(timestamp)[:5]
                formatted_lines.append(f"[{time_str}] {username}: {content}")
            else:
                formatted_lines.append(f"{username}: {content}")
        
        return "\n".join(formatted_lines)
    
    def _create_fallback_summary(self, summary_content: str, participants: List[str]) -> Dict[str, Any]:
        """Create fallback summary when JSON parsing fails"""
        # Extract key points from the summary content
        lines = summary_content.split('\n')
        script_lines = []
        
        # Try to extract dialogue-like content
        for line in lines:
            line = line.strip()
            if ':' in line and any(participant in line for participant in participants):
                # This looks like dialogue
                script_lines.append(line)
            elif line and len(line) < 100:  # Short lines might be key points
                # Assign to first participant as fallback
                if participants:
                    script_lines.append(f"{participants[0]}: {line}")
        
        # Limit script lines
        script_lines = script_lines[:10]
        
        return {
            'summary_text': summary_content[:200] + "..." if len(summary_content) > 200 else summary_content,
            'script_lines': script_lines,
            'participants': participants,
            'personality_context': {},
            'relationship_context': {},
            'tone_analysis': {'overall_tone': 'neutral'},
            'word_count': len(' '.join(script_lines).split())
        }
    
    def _validate_and_enhance_summary(self, summary_data: Dict[str, Any], participants: List[str], user_contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance summary data with additional context"""
        
        # Ensure required fields exist
        if 'summary_text' not in summary_data:
            summary_data['summary_text'] = "Conversation summary"
        
        if 'script_lines' not in summary_data:
            summary_data['script_lines'] = []
        
        if 'participants' not in summary_data:
            summary_data['participants'] = participants
        
        # Enhance personality context
        if 'personality_context' not in summary_data:
            summary_data['personality_context'] = {}
        
        for participant in participants:
            if participant in user_contexts:
                context = user_contexts[participant]
                profile = context.get('profile', {})
                
                summary_data['personality_context'][participant] = {
                    'traits': profile.get('personality_traits', []),
                    'interests': profile.get('interests', []),
                    'communication_style': profile.get('communication_style', {}),
                    'relationship_type': context.get('relationship_type', 'friend'),
                    'trust_score': context.get('trust_score', 0.5)
                }
        
        # Enhance relationship context
        if 'relationship_context' not in summary_data:
            summary_data['relationship_context'] = {
                'participant_count': len(participants),
                'relationship_types': {},
                'interaction_patterns': {}
            }
        
        # Analyze interaction patterns
        for participant in participants:
            if participant in user_contexts:
                context = user_contexts[participant]
                summary_data['relationship_context']['relationship_types'][participant] = context.get('relationship_type', 'friend')
        
        # Enhance tone analysis
        if 'tone_analysis' not in summary_data:
            summary_data['tone_analysis'] = {
                'overall_tone': 'neutral',
                'emotional_indicators': [],
                'engagement_level': 'medium'
            }
        
        # Calculate word count
        if 'word_count' not in summary_data:
            script_text = ' '.join(summary_data['script_lines'])
            summary_data['word_count'] = len(script_text.split())
        
        return summary_data
    
    def analyze_conversation_tone(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall tone and mood of a conversation"""
        try:
            # Extract conversation text
            conversation_text = self._format_conversation(messages)
            
            # Analyze with OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze the tone and mood of this conversation. Return a JSON object with: overall_tone (positive/negative/neutral), emotional_indicators (list of emotions detected), engagement_level (high/medium/low), and key_themes (list of main topics)."},
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis_content = response.choices[0].message.content.strip()
            
            try:
                # Try to parse JSON response
                json_match = re.search(r'\{.*\}', analysis_content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {
                        'overall_tone': 'neutral',
                        'emotional_indicators': [],
                        'engagement_level': 'medium',
                        'key_themes': []
                    }
            except json.JSONDecodeError:
                return {
                    'overall_tone': 'neutral',
                    'emotional_indicators': [],
                    'engagement_level': 'medium',
                    'key_themes': []
                }
                
        except Exception as e:
            logger.error(f"Error analyzing conversation tone: {e}")
            return {
                'overall_tone': 'neutral',
                'emotional_indicators': [],
                'engagement_level': 'medium',
                'key_themes': []
            }
    
    def extract_key_updates(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key updates and important information from messages"""
        try:
            # Filter important messages
            important_messages = [msg for msg in messages if msg.get('is_important', False)]
            
            if not important_messages:
                # If no messages marked as important, analyze all messages
                conversation_text = self._format_conversation(messages)
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Extract the 5 most important updates or key points from this conversation. Return as a JSON array of strings."},
                        {"role": "user", "content": conversation_text}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                
                try:
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        return []
                except json.JSONDecodeError:
                    return []
            else:
                # Return content from important messages
                return [msg.get('content', '') for msg in important_messages[:5]]
                
        except Exception as e:
            logger.error(f"Error extracting key updates: {e}")
            return []

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
        



chat = ChatSummarizer()
print(chat.generate_summary([{}]))