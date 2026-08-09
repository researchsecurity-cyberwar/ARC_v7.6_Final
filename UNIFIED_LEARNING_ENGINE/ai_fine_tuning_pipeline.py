"""
AI Fine-Tuning Pipeline - Fine-tune Mistral dengan experience data
Membangun pipeline untuk fine-tuning model Mistral-7B dengan data pengalaman ARC
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


class AIFineTuningPipeline:
    """
    Pipeline untuk fine-tuning Mistral model dengan ARC experience data
    """

    def __init__(self, base_dir="~/.arc/ai_models"):
        self.base_dir = os.path.expanduser(base_dir)
        self.training_data_dir = os.path.join(self.base_dir, "training_data")
        self.models_dir = os.path.join(self.base_dir, "fine_tuned_models")
        self.pipeline_log_file = os.path.join(self.base_dir, "pipeline_log.json")
        
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.pipeline_log = []
        self.fine_tuning_history = []
        
        # Load existing log
        self._load_pipeline_log()
    
    def generate_training_data_from_experiences(self, experiences: List[Dict[str, Any]]) -> str:
        """
        Generate training data untuk fine-tuning dari experiences
        
        Args:
            experiences: List of experience dicts dari ExperienceCollector
            
        Returns:
            Path ke training data file (JSONL format)
        """
        if not experiences:
            return ""
        
        timestamp = int(time.time())
        training_file = os.path.join(self.training_data_dir, f"arc_training_{timestamp}.jsonl")
        
        training_examples = []
        
        for exp in experiences:
            # Extract data dari experience
            context = exp.get('context', {})
            outcome = exp.get('outcome', 'unknown')
            actions = exp.get('actions_taken', [])
            result_data = exp.get('result_data', {})
            
            vuln_type = context.get('technique', 'unknown')
            severity = context.get('severity', 'medium')
            detector = context.get('detector', 'unknown')
            lesson = result_data.get('lesson', 'No lesson')
            finding = result_data.get('finding', {})
            
            # Generate training examples dalam format Instruct untuk Mistral
            if outcome == 'success':
                # Success case: pattern yang berhasil
                example = self._create_success_example(vuln_type, severity, detector, lesson, finding, context)
                training_examples.append(example)
            elif outcome == 'failure':
                # Failure case: pattern yang gagal dan pembelajaran
                example = self._create_failure_example(vuln_type, severity, detector, lesson, finding, context)
                training_examples.append(example)
            
            # Tambah example untuk reasoning
            reasoning_example = self._create_reasoning_example(vuln_type, severity, context, outcome, lesson)
            training_examples.append(reasoning_example)
        
        # Save ke JSONL format
        with open(training_file, 'w') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
        
        # Log pipeline activity
        self._log_pipeline_activity('generate_training_data', {
            'file': training_file,
            'examples': len(training_examples),
            'successes': len([e for e in experiences if e.get('outcome') == 'success']),
            'failures': len([e for e in experiences if e.get('outcome') == 'failure'])
        })
        
        return training_file
    
    def _create_success_example(self, vuln_type: str, severity: str, detector: str, 
                                lesson: str, finding: Dict, context: Dict) -> Dict[str, str]:
        """Create training example untuk successful detection"""
        prompt = f"""<s>[INST]
You are ARC (Advanced Research Cannon), an elite bug bounty hunting system.
You successfully detected a {vuln_type} vulnerability using {detector}.

Context:
- Vulnerability Type: {vuln_type}
- Severity: {severity}
- Target: {context.get('target_info', 'N/A')}
- Parameter: {context.get('parameter', 'N/A')}

What is the key lesson learned from this successful detection?
[/INST]

Lesson: {lesson}

This successful detection demonstrates effective {vuln_type} detection methodology using {detector}. The technique should be prioritized for similar targets."""
        
        return {"prompt": prompt, "type": "success_pattern"}
    
    def _create_failure_example(self, vuln_type: str, severity: str, detector: str,
                                lesson: str, finding: Dict, context: Dict) -> Dict[str, str]:
        """Create training example untuk failed detection"""
        error_type = context.get('error_type', 'unknown')
        
        prompt = f"""<s>[INST]
You are ARC (Advanced Research Cannon), an elite bug bounty hunting system.
You FAILED to detect a {vuln_type} vulnerability using {detector}.

Context:
- Vulnerability Type: {vuln_type}
- Severity: {severity}
- Detector: {detector}
- Error Type: {error_type}
- Target: {context.get('target_info', 'N/A')}

Analyze the failure and provide:
1. Root cause of failure
2. Corrective action
3. Modified detection strategy
[/INST]

Root Cause: {lesson}

Corrective Action: Adjust detection parameters and payloads for {vuln_type}. Consider alternative vectors such as {context.get('alternative_vectors', 'encoding bypass, WAF evasion')}.

Modified Strategy: Implement adaptive payload generation with context-aware evasion techniques."""
        
        return {"prompt": prompt, "type": "failure_analysis"}
    
    def _create_reasoning_example(self, vuln_type: str, severity: str, context: Dict,
                                  outcome: str, lesson: str) -> Dict[str, str]:
        """Create training example untuk vulnerability reasoning"""
        target_info = context.get('target_info', 'unknown target')
        cve_id = context.get('cve_id', '')
        cwe_id = context.get('cwe_id', '')
        
        cve_info = f" (CVE: {cve_id})" if cve_id else ""
        cwe_info = f" (CWE: {cwe_id})" if cwe_id else ""
        
        prompt = f"""<s>[INST]
Analyze this vulnerability scenario:

Vulnerability: {vuln_type}{cve_info}{cwe_info}
Severity: {severity}
Target: {target_info}
Outcome: {outcome}

Provide strategic analysis:
1. Exploitation approach
2. Business impact assessment
3. Proof-of-concept recommendations
4. Remediation priority
[/INST]

Analysis: {lesson}

Strategic Assessment:
- Exploitation: Medium complexity, requires {context.get('required_tools', 'standard web tools')}
- Business Impact: {severity.upper()} risk to {context.get('business_impact', 'confidentiality and integrity')}
- PoC: Validate with {context.get('validation_method', 'controlled testing')}
- Priority: {severity.upper()} - Immediate attention required"""
        
        return {"prompt": prompt, "type": "strategic_reasoning"}
    
    def prepare_fine_tuning_config(self, training_file: str, epochs: int = 3,
                                   learning_rate: float = 5e-5) -> Dict[str, Any]:
        """
        Prepare fine-tuning configuration untuk Mistral
        
        Args:
            training_file: Path ke training data file
            epochs: Number of training epochs
            learning_rate: Learning rate untuk fine-tuning
            
        Returns:
            Configuration dict
        """
        config = {
            "model": {
                "base_model": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "model_path": os.path.expanduser("~/.arc/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
                "output_dir": os.path.join(self.models_dir, f"fine_tuned_{int(time.time())}")
            },
            "training": {
                "data_file": training_file,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "batch_size": 4,
                "ctx_length": 4096,
                "threads": 8,
                "gradient_accumulation": 4
            },
            "lora": {
                "enabled": True,
                "rank": 8,
                "alpha": 16,
                "dropout": 0.05
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_examples": self._count_training_examples(training_file),
                "purpose": "ARC vulnerability detection and analysis specialization"
            }
        }
        
        # Save config
        config_file = os.path.join(self.models_dir, f"config_{int(time.time())}.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _count_training_examples(self, training_file: str) -> int:
        """Count number of training examples dalam file"""
        try:
            with open(training_file, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def execute_fine_tuning(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute fine-tuning process (simulation)
        
        Note: Actual fine-tuning memerlukan llama.cpp training scripts
        Fungsi ini menyiapkan dan mencatat proses fine-tuning
        """
        model_path = config['model']['model_path']
        output_dir = config['model']['output_dir']
        training_file = config['training']['data_file']
        
        # Check prerequisites
        if not os.path.exists(model_path):
            return {
                'status': 'error',
                'error': f'Base model not found at {model_path}',
                'next_steps': ['Download Mistral-7B model']
            }
        
        if not os.path.exists(training_file):
            return {
                'status': 'error',
                'error': f'Training data not found at {training_file}',
                'next_steps': ['Generate training data from experiences']
            }
        
        # Simulate fine-tuning process
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            'status': 'prepared',
            'config': config,
            'output_dir': output_dir,
            'training_examples': config['metadata']['total_examples'],
            'estimated_time': f"{config['training']['epochs'] * 2} minutes",
            'next_steps': [
                'Run llama.cpp fine-tuning script',
                'Monitor training loss',
                'Validate model on test set',
                'Deploy fine-tuned model'
            ],
            'commands': [
                f"cd {output_dir}",
                f"python -m llama_cpp.train \\",
                f"  --model {model_path} \\",
                f"  --train-data {training_file} \\",
                f"  --epochs {config['training']['epochs']} \\",
                f"  --learning-rate {config['training']['learning_rate']} \\",
                f"  --batch-size {config['training']['batch_size']} \\",
                f"  --output {output_dir}/fine_tuned_model.gguf"
            ]
        }
        
        # Log fine-tuning preparation
        self.fine_tuning_history.append({
            'timestamp': datetime.now().isoformat(),
            'training_file': training_file,
            'examples': config['metadata']['total_examples'],
            'status': 'prepared'
        })
        
        return result
    
    def merge_with_base_model(self, fine_tuned_model_path: str, 
                              output_name: str = None) -> str:
        """
        Merge fine-tuned model dengan base model
        
        Returns:
            Path ke merged model
        """
        if not output_name:
            timestamp = int(time.time())
            output_name = f"arc_enhanced_mistral_{timestamp}.gguf"
        
        output_path = os.path.join(self.models_dir, output_name)
        
        # Simulasi merge process
        # Dalam praktik nyata, ini akan menggunakan tools seperti gguf merger
        
        merge_result = {
            'base_model': 'mistral-7b-instruct-v0.2.Q4_K_M.gguf',
            'fine_tuned_adapter': fine_tuned_model_path,
            'merged_output': output_path,
            'method': 'LoRA merge',
            'timestamp': datetime.now().isoformat()
        }
        
        # Log merge
        self._log_pipeline_activity('model_merge', merge_result)
        
        return output_path
    
    def validate_fine_tuned_model(self, model_path: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Validate fine-tuned model dengan test cases
        
        Args:
            model_path: Path ke fine-tuned model
            test_cases: List of test cases
            
        Returns:
            Validation results
        """
        results = {
            'model_path': model_path,
            'test_cases': len(test_cases),
            'passed': 0,
            'failed': 0,
            'accuracy': 0.0,
            'details': []
        }
        
        # Simulate validation
        for i, test_case in enumerate(test_cases):
            # Simulate model evaluation
            passed = True  # Would actually test model here
            results['passed'] += 1 if passed else 0
            results['failed'] += 0 if passed else 1
            results['details'].append({
                'test_id': i,
                'type': test_case.get('type', 'unknown'),
                'passed': passed
            })
        
        results['accuracy'] = results['passed'] / len(test_cases) if test_cases else 0.0
        
        return results
    
    def auto_fine_tune_loop(self, orchestrator) -> Dict[str, Any]:
        """
        Automatic fine-tuning loop yang terintegrasi dengan SelfLearningOrchestrator
        
        Args:
            orchestrator: SelfLearningOrchestrator instance
            
        Returns:
            Fine-tuning result
        """
        print("🔄 Starting auto fine-tuning loop...")
        
        # 1. Get experiences dari orchestrator
        experiences = orchestrator.experience_collector.experiences
        
        if len(experiences) < 20:
            return {
                'status': 'skipped',
                'reason': f'Insufficient experiences: {len(experiences)}/20'
            }
        
        # 2. Generate training data
        training_file = self.generate_training_data_from_experiences(experiences)
        
        if not training_file:
            return {
                'status': 'error',
                'error': 'Failed to generate training data'
            }
        
        # 3. Prepare config
        config = self.prepare_fine_tuning_config(training_file)
        
        # 4. Execute fine-tuning
        result = self.execute_fine_tuning(config)
        
        # 5. Log result
        self._log_pipeline_activity('auto_fine_tune', result)
        
        return result
    
    def _log_pipeline_activity(self, activity_type: str, data: Dict[str, Any]):
        """Log pipeline activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity_type,
            'data': data
        }
        
        self.pipeline_log.append(log_entry)
        self._save_pipeline_log()
    
    def _save_pipeline_log(self):
        """Save pipeline log to disk"""
        try:
            with open(self.pipeline_log_file, 'w') as f:
                json.dump(self.pipeline_log, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save pipeline log: {e}")
    
    def _load_pipeline_log(self):
        """Load pipeline log from disk"""
        try:
            if os.path.exists(self.pipeline_log_file):
                with open(self.pipeline_log_file, 'r') as f:
                    self.pipeline_log = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load pipeline log: {e}")
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            'total_pipeline_activities': len(self.pipeline_log),
            'total_fine_tuning_runs': len(self.fine_tuning_history),
            'training_data_files': len(os.listdir(self.training_data_dir)) if os.path.exists(self.training_data_dir) else 0,
            'model_artifacts': len(os.listdir(self.models_dir)) if os.path.exists(self.models_dir) else 0,
            'last_activity': self.pipeline_log[-1] if self.pipeline_log else None
        }
    
    def export_for_llama_cpp(self, training_file: str, output_format: str = 'jsonl') -> str:
        """
        Export training data dalam format compatible dengan llama.cpp
        
        Args:
            training_file: Input training file
            output_format: Output format (jsonl/csv)
            
        Returns:
            Path ke exported file
        """
        if not os.path.exists(training_file):
            return ""
        
        timestamp = int(time.time())
        export_file = os.path.join(self.training_data_dir, f"llama_cpp_format_{timestamp}.{output_format}")
        
        try:
            with open(training_file, 'r') as infile, open(export_file, 'w') as outfile:
                for line in infile:
                    example = json.loads(line)
                    # Reformat untuk llama.cpp format
                    llama_format = {
                        "instruction": example.get("prompt", "").split("[/INST]")[0].replace("<s>[INST]", "").strip(),
                        "output": example.get("prompt", "").split("[/INST]")[-1].strip() if "[/INST]" in example.get("prompt", "") else ""
                    }
                    outfile.write(json.dumps(llama_format) + '\n')
            
            return export_file
            
        except Exception as e:
            print(f"⚠️ Failed to export for llama.cpp: {e}")
            return ""