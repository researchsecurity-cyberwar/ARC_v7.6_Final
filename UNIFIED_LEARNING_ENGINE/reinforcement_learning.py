"""
Reinforcement Learning System - RL-based decision making
Menggunakan reinforcement learning untuk optimize detection strategies
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class ReinforcementLearner:
    """
    Reinforcement learning system untuk optimize detection dan exploitation strategies
    """

    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        self.rl_state_file = os.path.join(self.base_dir, "rl_state.json")
        self.q_table_file = os.path.join(self.base_dir, "q_table.json")
        
        # Q-Learning parameters
        self.learning_rate = 0.1  # Alpha
        self.discount_factor = 0.9  # Gamma
        self.epsilon = 0.1  # Exploration rate
        
        # State tracking
        self.q_table = {}  # State-Action values
        self.state_history = []
        self.reward_history = []
        
        # Load existing state
        self._load_rl_state()
    
    def get_state(self, context: Dict[str, Any]) -> str:
        """
        Convert context menjadi state representation
        
        Args:
            context: Vulnerability context
            
        Returns:
            State string representation
        """
        # Create state dari key features
        vuln_type = context.get('technique', 'unknown')
        severity = context.get('severity', 'medium')
        has_cve = 'yes' if context.get('cve_id') else 'no'
        has_cwe = 'yes' if context.get('cwe_id') else 'no'
        category = context.get('technique_category', 'general')
        
        # State format: "vuln_type:severity:cve:cwe:category"
        state = f"{vuln_type}:{severity}:{has_cve}:{has_cwe}:{category}"
        
        return state
    
    def get_actions(self, context: Dict[str, Any]) -> List[str]:
        """
        Get available actions untuk context
        
        Args:
            context: Vulnerability context
            
        Returns:
            List of possible actions
        """
        vuln_type = context.get('technique', 'unknown')
        
        # Define actions berdasarkan vulnerability type
        base_actions = [
            'detect_standard',
            'detect_enhanced',
            'detect_stealth',
            'skip_detection'
        ]
        
        # Add specific actions berdasarkan technique
        specific_actions = {
            'xss': ['detect_dom_xss', 'detect_stored_xss', 'detect_reflected_xss'],
            'sqli': ['detect_blind_sqli', 'detect_error_sqli', 'detect_union_sqli'],
            'ssrf': ['detect_ssrf_outband', 'detect_ssrf_inband'],
            'idor': ['detect_idor_api', 'detect_idor_sequential'],
            'lfi': ['detect_lfi_direct', 'detect_lfi_php_wrapper'],
            'rfi': ['detect_rfi_remote', 'detect_rfi_filters'],
            'command_injection': ['detect_cmd_time', 'detect_cmd_oob'],
            'bola': ['detect_bola_idor', 'detect_bola_mass_assignment'],
            'jwt': ['detect_jwt_none', 'detect_jwt_weak_secret'],
            'reentrancy': ['detect_reentrancy_call', 'detect_reentrancy_delegatecall']
        }
        
        actions = base_actions + specific_actions.get(vuln_type, [])
        
        return actions
    
    def choose_action(self, state: str, actions: List[str], training: bool = True) -> str:
        """
        Choose action menggunakan epsilon-greedy policy
        
        Args:
            state: Current state
            actions: Available actions
            training: Whether in training mode (use epsilon-greedy)
            
        Returns:
            Selected action
        """
        if not actions:
            return 'skip_detection'
        
        # Exploration: random action
        if training and os.getenv('ARC_RL_EXPLORATION', 'true').lower() == 'true':
            if hash(state + datetime.now().isoformat()) % 100 < self.epsilon * 100:
                import random
                return random.choice(actions)
        
        # Exploitation: best action dari Q-table
        best_action = None
        best_value = float('-inf')
        
        for action in actions:
            q_key = f"{state}:{action}"
            q_value = self.q_table.get(q_key, 0.0)
            
            if q_value > best_value:
                best_value = q_value
                best_action = action
        
        return best_action if best_action else actions[0]
    
    def update_q_value(self, state: str, action: str, reward: float, 
                       next_state: str, next_actions: List[str]):
        """
        Update Q-value menggunakan Q-learning formula
        
        Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
        """
        # Current Q-value
        q_key = f"{state}:{action}"
        current_q = self.q_table.get(q_key, 0.0)
        
        # Max Q-value untuk next state
        max_next_q = 0.0
        if next_actions:
            max_next_q = max([
                self.q_table.get(f"{next_state}:{a}", 0.0) 
                for a in next_actions
            ])
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        # Update Q-table
        self.q_table[q_key] = new_q
        
        # Log update
        self.reward_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'action': action,
            'reward': reward,
            'old_q': current_q,
            'new_q': new_q,
            'update_magnitude': abs(new_q - current_q)
        })
    
    def calculate_reward(self, outcome: str, context: Dict[str, Any], 
                        detection_time: float = 0.0) -> float:
        """
        Calculate reward berdasarkan outcome dan context
        
        Args:
            outcome: success/failure/partial
            context: Experience context
            detection_time: Time taken untuk detection
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Base reward dari outcome
        if outcome == 'success':
            reward = 10.0
        elif outcome == 'failure':
            reward = -5.0
        elif outcome == 'partial':
            reward = 2.0
        
        # Bonus berdasarkan severity
        severity = context.get('severity', 'medium').lower()
        severity_bonus = {
            'critical': 5.0,
            'high': 3.0,
            'medium': 1.0,
            'low': 0.5,
            'info': 0.1
        }
        reward += severity_bonus.get(severity, 0.0)
        
        # Bonus untuk CVE/CWE findings
        if context.get('cve_id'):
            reward += 2.0
        if context.get('cwe_id'):
            reward += 1.0
        
        # Penalty untuk slow detection
        if detection_time > 0:
            if detection_time > 60:  # > 1 minute
                reward -= 2.0
            elif detection_time > 30:  # > 30 seconds
                reward -= 1.0
        
        # Bonus untuk novel techniques (belum pernah dilihat)
        vuln_type = context.get('technique', 'unknown')
        if vuln_type not in self.state_history:
            reward += 1.0
        
        return reward
    
    def learn_from_experience(self, experience: Dict[str, Any]):
        """
        Learn dari single experience
        
        Args:
            experience: Experience dict
        """
        context = experience.get('context', {})
        outcome = experience.get('outcome', 'unknown')
        actions_taken = experience.get('actions_taken', [])
        
        # Extract primary action
        primary_action = 'detect_standard'
        if actions_taken:
            primary_action = actions_taken[0].get('type', primary_action)
        
        # Get state dan next state
        state = self.get_state(context)
        next_context = {**context, 'last_outcome': outcome}
        next_state = self.get_state(next_context)
        
        # Get actions untuk states
        current_actions = self.get_actions(context)
        next_actions = self.get_actions(next_context)
        
        # Calculate reward
        detection_time = experience.get('result_data', {}).get('detection_time', 0.0)
        reward = self.calculate_reward(outcome, context, detection_time)
        
        # Update Q-table
        self.update_q_value(state, primary_action, reward, next_state, next_actions)
        
        # Track state
        if state not in self.state_history:
            self.state_history.append(state)
        
        # Save periodically
        if len(self.reward_history) % 10 == 0:
            self._save_rl_state()
    
    def get_best_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get best detection strategy untuk context
        
        Args:
            context: Vulnerability context
            
        Returns:
            Strategy recommendations
        """
        state = self.get_state(context)
        actions = self.get_actions(context)
        
        # Get Q-values untuk all actions
        action_values = {}
        for action in actions:
            q_key = f"{state}:{action}"
            action_values[action] = self.q_table.get(q_key, 0.0)
        
        # Sort by Q-value
        sorted_actions = sorted(action_values.items(), key=lambda x: x[1], reverse=True)
        
        best_action = sorted_actions[0][0] if sorted_actions else 'detect_standard'
        best_value = sorted_actions[0][1] if sorted_actions else 0.0
        
        return {
            'recommended_action': best_action,
            'confidence': abs(best_value),
            'all_actions': dict(sorted_actions),
            'state': state,
            'exploration_rate': self.epsilon
        }
    
    def batch_learn(self, experiences: List[Dict[str, Any]]):
        """
        Learn dari batch of experiences
        
        Args:
            experiences: List of experience dicts
        """
        print(f"🔄 Batch RL learning from {len(experiences)} experiences...")
        
        learned = 0
        for exp in experiences:
            try:
                self.learn_from_experience(exp)
                learned += 1
            except Exception as e:
                print(f"⚠️ Failed to learn from experience: {e}")
        
        # Decay epsilon (less exploration over time)
        self.epsilon = max(0.01, self.epsilon * 0.99)
        
        print(f"✅ RL batch learning completed: {learned} experiences processed")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get RL learning statistics"""
        total_states = len(self.state_history)
        total_q_values = len(self.q_table)
        
        # Calculate average Q-value
        avg_q = 0.0
        if self.q_table:
            avg_q = sum(self.q_table.values()) / len(self.q_table)
        
        # Calculate recent rewards
        recent_rewards = self.reward_history[-100:] if len(self.reward_history) > 100 else self.reward_history
        avg_reward = 0.0
        if recent_rewards:
            avg_reward = sum(r['reward'] for r in recent_rewards) / len(recent_rewards)
        
        return {
            'total_states_visited': total_states,
            'total_q_values': total_q_values,
            'average_q_value': round(avg_q, 4),
            'epsilon': self.epsilon,
            'recent_avg_reward': round(avg_reward, 4),
            'total_updates': len(self.reward_history),
            'learning_progress': 'improving' if avg_reward > 0 else 'learning'
        }
    
    def export_policy(self) -> Dict[str, Any]:
        """
        Export learned policy untuk documentation
        
        Returns:
            Policy dict
        """
        # Group Q-values by state
        policy = defaultdict(dict)
        
        for q_key, q_value in self.q_table.items():
            parts = q_key.rsplit(':', 1)
            if len(parts) == 2:
                state = parts[0]
                action = parts[1]
                policy[state][action] = q_value
        
        # Get top policies
        top_policies = {}
        for state, actions in policy.items():
            if actions:
                best_action = max(actions.items(), key=lambda x: x[1])
                top_policies[state] = {
                    'best_action': best_action[0],
                    'q_value': best_action[1],
                    'all_actions': actions
                }
        
        return {
            'policy': dict(top_policies),
            'total_states': len(policy),
            'exported_at': datetime.now().isoformat()
        }
    
    def _save_rl_state(self):
        """Save RL state to disk"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            
            rl_state = {
                'q_table': self.q_table,
                'state_history': self.state_history,
                'reward_history': self.reward_history[-1000:],  # Keep last 1000
                'epsilon': self.epsilon,
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor
            }
            
            with open(self.rl_state_file, 'w') as f:
                json.dump(rl_state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save RL state: {e}")
    
    def _load_rl_state(self):
        """Load RL state from disk"""
        try:
            if os.path.exists(self.rl_state_file):
                with open(self.rl_state_file, 'r') as f:
                    rl_state = json.load(f)
                    
                    self.q_table = rl_state.get('q_table', {})
                    self.state_history = rl_state.get('state_history', [])
                    self.reward_history = rl_state.get('reward_history', [])
                    self.epsilon = rl_state.get('epsilon', 0.1)
                    self.learning_rate = rl_state.get('learning_rate', 0.1)
                    self.discount_factor = rl_state.get('discount_factor', 0.9)
                    
                    print(f"📂 RL state loaded: {len(self.q_table)} Q-values, {len(self.state_history)} states")
        except Exception as e:
            print(f"⚠️ Failed to load RL state: {e}")
    
    def integrate_with_closed_loop(self, closed_loop_feedback):
        """
        Integrate reinforcement learning dengan closed-loop feedback
        
        Args:
            closed_loop_feedback: ClosedLoopFeedback instance
        """
        print("🔗 Reinforcement Learning integrated with Closed-Loop Feedback")
        
        # This creates a bridge where closed-loop generates experiences
        # and RL learns from them to optimize strategies