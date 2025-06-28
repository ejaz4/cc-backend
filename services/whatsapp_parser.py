import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class WhatsAppParser:
    """Parser for WhatsApp chat exports"""
    
    def __init__(self):
        # Common WhatsApp export patterns
        self.patterns = {
            # Standard format: [date, time] username: message
            'standard': r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*(.+?):\s*(.+)',
            
            # Alternative format: date, time - username: message
            'alternative': r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*(.+?):\s*(.+)',
            
            # System messages: [date, time] system message
            'system': r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*(.+)',
            
            # Media messages: [date, time] username: <attached: filename>
            'media': r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*(.+?):\s*<attached:\s*(.+)>',
        }
    
    def parse_chat_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse WhatsApp chat export file
        
        Args:
            file_path: Path to the chat export file
            
        Returns:
            Dictionary containing parsed chat data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return self.parse_chat_content(content)
        except Exception as e:
            logger.error(f"Error parsing chat file {file_path}: {e}")
            return {'error': str(e)}
    
    def parse_chat_content(self, content: str) -> Dict[str, Any]:
        """
        Parse WhatsApp chat content string
        
        Args:
            content: Raw chat content string
            
        Returns:
            Dictionary containing parsed chat data
        """
        try:
            lines = content.strip().split('\n')
            messages = []
            participants = set()
            start_date = None
            end_date = None
            
            for line in lines:
                if not line.strip():
                    continue
                
                message = self._parse_line(line)
                if message:
                    messages.append(message)
                    participants.add(message['username'])
                    
                    # Track date range
                    if not start_date or message['timestamp'] < start_date:
                        start_date = message['timestamp']
                    if not end_date or message['timestamp'] > end_date:
                        end_date = message['timestamp']
            
            return {
                'messages': messages,
                'participants': list(participants),
                'total_messages': len(messages),
                'date_range': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'parsed_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing chat content: {e}")
            return {'error': str(e)}
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single chat line
        
        Args:
            line: Single line from chat export
            
        Returns:
            Parsed message dictionary or None if not a valid message
        """
        try:
            # Try standard format first
            match = re.match(self.patterns['standard'], line)
            if match:
                date_str, time_str, username, content = match.groups()
                timestamp = self._parse_datetime(date_str, time_str)
                return {
                    'username': username.strip(),
                    'content': content.strip(),
                    'timestamp': timestamp,
                    'message_type': 'text',
                    'is_important': self._is_important_message(content)
                }
            
            # Try alternative format
            match = re.match(self.patterns['alternative'], line)
            if match:
                date_str, time_str, username, content = match.groups()
                timestamp = self._parse_datetime(date_str, time_str)
                return {
                    'username': username.strip(),
                    'content': content.strip(),
                    'timestamp': timestamp,
                    'message_type': 'text',
                    'is_important': self._is_important_message(content)
                }
            
            # Try media format
            match = re.match(self.patterns['media'], line)
            if match:
                date_str, time_str, username, filename = match.groups()
                timestamp = self._parse_datetime(date_str, time_str)
                return {
                    'username': username.strip(),
                    'content': f"<attached: {filename.strip()}>",
                    'timestamp': timestamp,
                    'message_type': 'media',
                    'is_important': False
                }
            
            # Try system message format
            match = re.match(self.patterns['system'], line)
            if match:
                date_str, time_str, content = match.groups()
                timestamp = self._parse_datetime(date_str, time_str)
                return {
                    'username': 'System',
                    'content': content.strip(),
                    'timestamp': timestamp,
                    'message_type': 'system',
                    'is_important': False
                }
            
            return None
        except Exception as e:
            logger.warning(f"Error parsing line '{line}': {e}")
            return None
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """
        Parse date and time strings into datetime object
        
        Args:
            date_str: Date string (e.g., "12/25/2023")
            time_str: Time string (e.g., "14:30" or "2:30 PM")
            
        Returns:
            Parsed datetime object
        """
        try:
            # Handle different date formats
            if '/' in date_str:
                # Convert MM/DD/YY to YYYY-MM-DD
                parts = date_str.split('/')
                if len(parts) == 3:
                    month, day, year = parts
                    if len(year) == 2:
                        year = '20' + year
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Handle different time formats
            time_str = time_str.strip()
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                # 12-hour format
                time_obj = datetime.strptime(time_str, '%I:%M %p').time()
            else:
                # 24-hour format
                if ':' in time_str and time_str.count(':') == 1:
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                else:
                    time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
            
            # Combine date and time
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            return datetime.combine(date_obj, time_obj)
        except Exception as e:
            logger.warning(f"Error parsing datetime '{date_str} {time_str}': {e}")
            return datetime.utcnow()
    
    def _is_important_message(self, content: str) -> bool:
        """
        Determine if a message is important based on content
        
        Args:
            content: Message content
            
        Returns:
            True if message is considered important
        """
        # Keywords that indicate important messages
        important_keywords = [
            'meeting', 'call', 'event', 'party', 'dinner', 'lunch', 'coffee',
            'deadline', 'due', 'urgent', 'important', 'reminder', 'schedule',
            'tomorrow', 'today', 'tonight', 'weekend', 'birthday', 'anniversary',
            'travel', 'flight', 'hotel', 'booking', 'reservation', 'appointment'
        ]
        
        content_lower = content.lower()
        
        # Check for important keywords
        for keyword in important_keywords:
            if keyword in content_lower:
                return True
        
        # Check for question marks (questions are often important)
        if '?' in content:
            return True
        
        # Check for exclamation marks (emphasized messages)
        if '!' in content:
            return True
        
        # Check for time patterns (scheduling)
        time_patterns = [
            r'\d{1,2}:\d{2}',  # HH:MM
            r'\d{1,2}:\d{2}\s*[AP]M',  # HH:MM AM/PM
            r'tomorrow', r'today', r'tonight'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def extract_key_updates(self, messages: List[Dict[str, Any]], max_updates: int = 10) -> List[Dict[str, Any]]:
        """
        Extract key updates from messages
        
        Args:
            messages: List of parsed messages
            max_updates: Maximum number of updates to return
            
        Returns:
            List of key updates
        """
        important_messages = [msg for msg in messages if msg.get('is_important', False)]
        
        # Sort by timestamp (most recent first)
        important_messages.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Group by user
        user_updates = {}
        for msg in important_messages:
            username = msg['username']
            if username not in user_updates:
                user_updates[username] = []
            user_updates[username].append(msg)
        
        # Select top updates per user
        key_updates = []
        for username, user_msgs in user_updates.items():
            # Take the most recent important message from each user
            if user_msgs:
                key_updates.append(user_msgs[0])
        
        # Sort by timestamp and limit
        key_updates.sort(key=lambda x: x['timestamp'], reverse=True)
        return key_updates[:max_updates] 