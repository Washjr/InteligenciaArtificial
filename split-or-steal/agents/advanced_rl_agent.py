from collections import defaultdict
import random

class AdvancedRLAgent:
    def __init__(self):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.1
        self.opponent_history = []  # Simplificado para uma lista
        self.last_state = None
        self.last_action = None
        self.last_round = False
        self.game_count = 0

    def reset(self):
        self.last_state = None
        self.last_action = None
        self.opponent_history.clear()

    def _get_opponent_pattern(self):
        if len(self.opponent_history) < 3:
            return 'unknown'
            
        recent_actions = self.opponent_history[-5:]
        split_rate = sum(1 for action in recent_actions if action == 'split') / len(recent_actions)
        
        if split_rate > 0.7:
            return 'cooperative'
        elif split_rate < 0.3:
            return 'aggressive'
        else:
            return 'mixed'

    def get_state(self, your_karma, his_karma, round_context, amount):
        # Estado baseado nos parâmetros disponíveis
        opp_pattern = self._get_opponent_pattern()
        your_karma_level = 'high' if your_karma > 0.5 else 'low' if your_karma < -0.5 else 'neutral'
        his_karma_level = 'high' if his_karma > 0.5 else 'low' if his_karma < -0.5 else 'neutral'
        amount_level = 'high' if amount > 150 else 'low' if amount < 50 else 'medium'
        
        return (your_karma_level, his_karma_level, opp_pattern, round_context, amount_level)
    
    def choose_action(self, state):
        # Epsilon-greedy com decay
        if random.random() < self.epsilon:
            action = random.choice(['split', 'steal'])
        else:
            split_value = self.q_table[state]['split']
            steal_value = self.q_table[state]['steal']
            action = 'split' if split_value > steal_value else 'steal'
        
        return action
    
    def get_name(self):
        return "AdvancedRL"

    def decision(self, amount, rounds_left, your_karma, his_karma):
        # Define o contexto da rodada
        self.last_round = rounds_left == 0
        round_context = 'final' if self.last_round else 'normal'
        
        # Cria um identificador do estado baseado nos parâmetros disponíveis
        state = self.get_state(your_karma, his_karma, round_context, amount)
        action = self.choose_action(state)
        
        self.last_state = state
        self.last_action = action
        return action

    def result(self, your_action, his_action, total_possible, reward):
        """Método chamado após cada rodada para atualizar o agente"""
        # Calcula recompensa customizada baseada nas ações
        custom_reward = self._calculate_reward(your_action, his_action, reward, total_possible)
        
        # Q-Learning update
        if self.last_state and self.last_action:
            current_q = self.q_table[self.last_state][self.last_action]
            self.q_table[self.last_state][self.last_action] = current_q + self.alpha * (custom_reward - current_q)
        
        # Atualiza histórico do oponente
        self.opponent_history.append(his_action)
        if len(self.opponent_history) > 10:
            self.opponent_history.pop(0)
        
        # Decay epsilon após cada jogo
        if self.last_round:
            self.epsilon = max(0.01, self.epsilon * 0.999)
            self.game_count += 1
            
    def _calculate_reward(self, your_action, his_action, actual_reward, total_possible):
        """Calcula recompensa customizada para melhorar aprendizado"""
        # Recompensa base é o reward real normalizado
        base_reward = actual_reward / max(total_possible, 1) if total_possible > 0 else 0
        
        # Bonificações por cooperação mútua
        if your_action == "split" and his_action == "split":
            return base_reward + 0.5  # Cooperação mútua é boa
        elif your_action == "steal" and his_action == "split":
            return base_reward + 0.3  # Exploração bem-sucedida
        elif your_action == "split" and his_action == "steal":
            return base_reward - 0.3  # Penalidade por ser explorado
        else:  # steal vs steal
            return base_reward - 0.1  # Ambos perderam
            
        return base_reward