import re


class CanarytokenDetector:
    """
    Detect Canarytokens & deception markers in HTTP responses.
    Wrap the standalone function-based implementation for class-based integration.
    """

    def __init__(self):
        self.canary_headers = ['x-canary', 'x-honeypot', 'deception-token']
        self.canary_patterns = [
            r'canarytoken.*[a-f0-9]{32}',
            r'honeytoken.*[a-f0-9]{32}',
            r'deception_id.*[a-f0-9]{32}'
        ]

    def detect(self, content):
        """
        Detect canarytokens in response content (headers dict or body string).
        Returns a list of detected canarytoken markers.
        """
        detected = []

        if isinstance(content, dict):
            # Treat as headers dictionary
            for header_name, header_value in content.items():
                header_name_lower = header_name.lower()
                if any(canary in header_name_lower for canary in self.canary_headers):
                    detected.append(f"{header_name}: {header_value}")
        elif isinstance(content, str):
            # Treat as body content
            for pattern in self.canary_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                detected.extend(matches)

        return detected


# Backward-compatible standalone functions
def detect_canarytokens_in_headers(headers):
    """
    Deteksi Canarytokens dalam header HTTP.
    """
    canary_headers = ['x-canary', 'x-honeypot', 'deception-token']
    detected = []

    for header_name, header_value in headers.items():
        header_name_lower = header_name.lower()
        if any(canary in header_name_lower for canary in canary_headers):
            detected.append(f"{header_name}: {header_value}")

    return detected


def detect_canarytokens_in_body(body_content):
    """
    Deteksi Canarytokens dalam body respons.
    """
    canary_patterns = [
        r'canarytoken.*[a-f0-9]{32}',
        r'honeytoken.*[a-f0-9]{32}',
        r'deception_id.*[a-f0-9]{32}'
    ]

    detected = []
    for pattern in canary_patterns:
        matches = re.findall(pattern, body_content, re.IGNORECASE)
        detected.extend(matches)

    return detected
