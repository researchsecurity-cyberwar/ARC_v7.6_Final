import re
from typing import Dict, List

class ContextAnalyzer:
    """
    Analyze discussion context & intent.
    Menganalisis konteks diskusi dan maksud dari pesan platform.
    """
    
    def __init__(self):
        self.intent_patterns = {
            'request_clarification': [
                r'(?:can you|could you|please).*?(?:clarify|explain|detail)',
                r'(?:what|how|why).*?(?:exactly|specifically)'
            ],
            'request_evidence': [
                r'(?:provide|show|send).*?(?:proof|evidence|video|screenshot)',
                r'(?:reproduce|replicate).*?(?:issue|vulnerability)'
            ],
            'triage_update': [
                r'(?:status|state|triage).*?(?:update|changed|modified)',
                r'(?:moved|transferred).*?(?:queue|category|severity)'
            ],
            'acceptance_notification': [
                r'(?:accepted|validated|confirmed).*?(?:vulnerability|report)',
                r'(?:eligible|qualified).*?(?:for bounty|reward)'
            ],
            'rejection_notification': [
                r'(?:rejected|invalid|duplicate).*?(?:vulnerability|report)',
                r'(?:out of scope|not eligible)'
            ]
        }
        
        self.sentiment_indicators = {
            'positive': ['great', 'excellent', 'well done', 'thank you', 'appreciate'],
            'neutral': ['please', 'could you', 'would you', 'regarding', 'about'],
            'negative': ['unfortunately', 'however', 'but', 'issue', 'problem']
        }
    
    def analyze_discussion_context(self, message_text: str, platform: str) -> Dict:
        """
        Analisis konteks diskusi dari pesan platform.
        """
        analysis = {
            'original_message': message_text[:200] + '...' if len(message_text) > 200 else message_text,
            'platform': platform,
            'detected_intent': None,
            'intent_confidence': 0.0,
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'key_entities': [],
            'recommended_response_type': None,
            'urgency_level': 'normal'
        }
        
        try:
            # Deteksi intent
            intent, confidence = self._detect_intent(message_text)
            analysis['detected_intent'] = intent
            analysis['intent_confidence'] = confidence
            
            # Analisis sentimen
            sentiment, score = self._analyze_sentiment(message_text)
            analysis['sentiment'] = sentiment
            analysis['sentiment_score'] = score
            
            # Ekstrak entitas kunci
            entities = self._extract_key_entities(message_text, platform)
            analysis['key_entities'] = entities
            
            # Tentukan tipe respons yang direkomendasikan
            analysis['recommended_response_type'] = self._determine_response_type(intent, sentiment, platform)
            
            # Tentukan tingkat urgensi
            analysis['urgency_level'] = self._assess_urgency(intent, sentiment, platform)
        
        except Exception as e:
            analysis['error'] = f'Context analysis failed: {str(e)}'
        
        return analysis
    
    def _detect_intent(self, text: str) -> tuple:
        """Deteksi intent dari teks."""
        text_lower = text.lower()
        best_intent = None
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.9 if 'acceptance' in intent or 'rejection' in intent else 0.7
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
                    break
        
        return best_intent or 'general_inquiry', best_confidence
    
    def _analyze_sentiment(self, text: str) -> tuple:
        """Analisis sentimen teks."""
        text_lower = text.lower()
        positive_count = sum(1 for word in self.sentiment_indicators['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_indicators['negative'] if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive', min(positive_count * 0.3, 1.0)
        elif negative_count > positive_count:
            return 'negative', min(negative_count * 0.3, 1.0)
        else:
            return 'neutral', 0.5
    
    def _extract_key_entities(self, text: str, platform: str) -> List[str]:
        """Ekstrak entitas kunci dari teks."""
        entities = []
        
        # Ekstrak ID laporan
        report_id_match = re.search(r'#(\d+)', text)
        if report_id_match:
            entities.append(f"report_id:{report_id_match.group(1)}")
        
        # Ekstrak URL
        url_matches = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        for url in url_matches[:3]:  # Batasi 3 URL
            entities.append(f"url:{url}")
        
        # Ekstrak istilah platform-spesifik
        if platform == 'hackerone':
            if 'triaged' in text.lower():
                entities.append('status:triaged')
            if 'bounty' in text.lower():
                entities.append('topic:bounty')
        
        return entities
    
    def _determine_response_type(self, intent: str, sentiment: str, platform: str) -> str:
        """Tentukan tipe respons yang direkomendasikan."""
        if intent == 'acceptance_notification':
            return 'gratitude_and_followup'
        elif intent == 'rejection_notification':
            return 'professional_appeal'
        elif intent == 'request_evidence':
            return 'evidence_provision'
        elif intent == 'request_clarification':
            return 'detailed_explanation'
        else:
            return 'acknowledgment'
    
    def _assess_urgency(self, intent: str, sentiment: str, platform: str) -> str:
        """Nilai tingkat urgensi."""
        if intent in ['acceptance_notification', 'rejection_notification']:
            return 'high'
        elif sentiment == 'negative':
            return 'medium'
        else:
            return 'normal'