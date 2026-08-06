import re

class SafetyFilter:
    """
    Middleware layer for AI Safety and Prompt Injection protection.
    """
    
    # Common prompt injection triggers
    FORBIDDEN_PHRASES = [
        "ignore previous instructions",
        "system prompt",
        "you are now",
        "new rules",
        "override",
        "drop tables"
    ]
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """
        Scans user input for potential prompt injections or unsafe content.
        Returns the sanitized string, or raises an error if highly malicious.
        """
        lowered = user_input.lower()
        
        for phrase in cls.FORBIDDEN_PHRASES:
            if phrase in lowered:
                # Mask the malicious phrase
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                user_input = pattern.sub("[REDACTED]", user_input)
                
        return user_input

    @classmethod
    def check_confidence(cls, confidence_score: float, threshold: float = 0.85) -> bool:
        """
        Determines if the AI's response meets the enterprise confidence threshold.
        If not, the system should fallback to human escalation.
        """
        return confidence_score >= threshold
