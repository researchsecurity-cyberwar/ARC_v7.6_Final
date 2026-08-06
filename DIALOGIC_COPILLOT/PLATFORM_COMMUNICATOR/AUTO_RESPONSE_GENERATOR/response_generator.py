class ResponseGenerator:
    """
    Generate professional responses.
    Menghasilkan respons profesional berdasarkan analisis konteks.
    """
    
    def __init__(self):
        self.response_templates = {
            'gratitude_and_followup': {
                'hackerone': "Thank you for the acceptance! I appreciate your team's thorough review process. Please let me know if you need any additional information or clarification regarding this finding.",
                'bugcrowd': "Thanks for validating this report! I'm glad it was helpful. Feel free to reach out if you need further details or assistance with remediation.",
                'intigriti': "Dankjewel voor de acceptatie! I appreciate the quick triage and validation. Please don't hesitate to contact me if you need anything else."
            },
            'professional_appeal': {
                'hackerone': "I understand the decision, but I'd like to respectfully appeal this rejection. Based on my testing, this vulnerability appears to meet the program's scope criteria because [REASON]. Could you please reconsider?",
                'bugcrowd': "Thank you for the review. I believe this finding may have been marked as duplicate incorrectly. My submission includes [UNIQUE_ASPECT] that differentiates it from existing reports.",
                'intigriti': "Ik begrijp de beslissing, maar ik zou graag een heroverweging willen vragen. Mijn bevinding valt binnen de scope omdat [REDEN]."
            },
            'evidence_provision': {
                'hackerone': "I've attached the requested evidence below:\n\n- Video PoC: [VIDEO_LINK]\n- HAR file: [HAR_LINK]\n- Step-by-step reproduction: [STEPS]\n\nPlease let me know if you need additional proof.",
                'bugcrowd': "Here's the evidence you requested:\n\n• Detailed reproduction steps\n• Network capture (PCAP)\n• Impact demonstration\n\nHappy to provide more if needed!",
                'intigriti': "Hierbij het gevraagde bewijs:\n\n- Video PoC\n- HAR-bestand\n- Reproductiestappen\n\nLaat het weten als je meer nodig hebt."
            },
            'detailed_explanation': {
                'hackerone': "I'd be happy to clarify! The vulnerability works as follows:\n\n1. [STEP_1]\n2. [STEP_2]\n3. [IMPACT]\n\nThe business impact is [BUSINESS_IMPACT] because [REASONING].",
                'bugcrowd': "Great question! Here's a detailed breakdown:\n\nTechnical Details: [TECHNICAL_DETAILS]\nBusiness Impact: [BUSINESS_IMPACT]\nRemediation: [REMEDIATION_SUGGESTION]",
                'intigriti': "Graag leg ik dit uit! De kwetsbaarheid werkt als volgt:\n\n1. [STAP_1]\n2. [STAP_2]\n3. [IMPACT]\n\nDe zakelijke impact is [ZAKELIJKE_IMPACT]."
            },
            'acknowledgment': {
                'hackerone': "Thank you for the update! I'll monitor the report for further developments.",
                'bugcrowd': "Got it! Thanks for keeping me in the loop.",
                'intigriti': "Begrepen! Dank voor de update."
            }
        }
    
    def generate_response(self, context_analysis: dict, customization: dict = None) -> str:
        """
        Hasilkan respons berdasarkan analisis konteks.
        """
        platform = context_analysis.get('platform', 'hackerone')
        response_type = context_analysis.get('recommended_response_type', 'acknowledgment')
        
        # Dapatkan template dasar
        template = self.response_templates.get(response_type, {}).get(
            platform, self.response_templates['acknowledgment']['hackerone']
        )
        
        # Sesuaikan dengan data kustom
        if customization:
            for placeholder, value in customization.items():
                template = template.replace(f"[{placeholder.upper()}]", str(value))
        
        # Pastikan tidak ada placeholder yang tersisa
        template = re.sub(r'\[[A-Z_]+\]', '[CUSTOM DATA NEEDED]', template)
        
        return template
    
    def customize_response_for_vulnerability(self, base_response: str, vulnerability_data: dict) -> str:
        """
        Sesuaikan respons untuk data kerentanan spesifik.
        """
        customizations = {
            'reason': vulnerability_data.get('scope_reasoning', 'the vulnerability affects core functionality'),
            'unique_aspect': vulnerability_data.get('unique_angle', 'this exploit chain combines multiple vulnerabilities'),
            'steps': vulnerability_data.get('reproduction_steps', 'detailed steps provided in original report'),
            'business_impact': vulnerability_data.get('business_impact', 'potential data exposure and financial loss'),
            'technical_details': vulnerability_data.get('technical_details', 'exploitation details in original submission'),
            'remediation_suggestion': vulnerability_data.get('remediation', 'implement proper input validation and output encoding'),
            'zakelijke_impact': vulnerability_data.get('business_impact', 'potentiële datalek en financieel verlies'),
            'stap_1': vulnerability_data.get('step_1', 'user accesses vulnerable endpoint'),
            'stap_2': vulnerability_data.get('step_2', 'malicious payload executed'),
            'impact': vulnerability_data.get('impact', 'session hijacking achieved')
        }
        
        for placeholder, value in customizations.items():
            base_response = base_response.replace(f"[{placeholder.upper()}]", str(value))
        
        return base_response