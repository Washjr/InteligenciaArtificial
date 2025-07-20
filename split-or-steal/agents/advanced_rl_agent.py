from collections import defaultdict
import random
import numpy as np

class AdvancedRLAgent:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1):
        # Hyperparâmetros
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Q-table usando a mesma estrutura do RLAgent
        self.Q = defaultdict(lambda: [0.0, 0.0])
        self.action_list = ["split", "steal"]
        
        # Variáveis de estado como no RLAgent
        self.current_input = None
        self.current_output = None
        self.last_round = False
        
        # Histórico do oponente para análise de padrões
        self.opponent_history = []
        self.game_count = 0

    def reset(self):
        self.current_input = None
        self.current_output = None
        self.opponent_history.clear()

    def _get_opponent_pattern(self):
        if len(self.opponent_history) < 3:
            return 0  # unknown
            
        recent_actions = self.opponent_history[-5:]
        split_rate = sum(1 for action in recent_actions if action == 'split') / len(recent_actions)
        
        if split_rate > 0.7:
            return 1  # cooperative
        elif split_rate < 0.3:
            return -1  # aggressive
        else:
            return 0  # mixed

    def extract_rl_state(self, state):
        """Extrai um estado simplificado para o Q-learning"""
        amount, rounds_left, your_karma, his_karma, last_round = state

        # Usa as 5 posições do karma (de -2 a +2)
        your_karma_pos = max(-2, min(2, your_karma))  # Clamp entre -2 e +2
        his_karma_sign = np.sign(his_karma)                 # -1, 0, 1
        opp_pattern = self._get_opponent_pattern()  # -1, 0, 1
        amount_level = 1 if amount > 150 else -1 if amount < 50 else 0
        round_context = 1 if last_round else 0
        
        return (your_karma_pos, his_karma_sign, opp_pattern, amount_level, round_context)

    def choose_action(self, state):
        state = self.extract_rl_state(state)
        
        # Epsilon-greedy com decay
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(["split", "steal"])
        else:
            action = self.action_list[np.argmax(self.Q[state])]
        
        return action

    def update_qtable(self, state, action, reward, next_state):
        """Atualização Q-learning usando a mesma fórmula do RLAgent"""
        alp = self.alpha
        gam = self.gamma
        action_index = self.action_list.index(action)
        state = self.extract_rl_state(state)
        next_state = self.extract_rl_state(next_state)
        self.Q[state][action_index] = (1 - alp) * self.Q[state][action_index] + alp * (reward + gam * np.max(self.Q[next_state]))

    def get_name(self):
        return "AdvancedRL"

    def decision(self, amount, rounds_left, your_karma, his_karma):
        self.last_round = True if rounds_left == 0 else False
        
        novel_input = (amount, rounds_left, your_karma, his_karma, self.last_round)

        if self.current_input is not None:
            self.update_qtable(self.current_input, self.current_output[0], self.current_output[-1], novel_input)
            
        self.current_input = novel_input
        
        return self.choose_action(self.current_input)

    def result(self, your_action, his_action, total_possible, reward):
        """Método chamado após cada rodada para atualizar o agente"""
        # Atualiza histórico do oponente
        self.opponent_history.append(his_action)
        if len(self.opponent_history) > 10:
            self.opponent_history.pop(0)
        
        # Calcula recompensa customizada
        custom_reward = self._calculate_reward(your_action, his_action, reward, total_possible)
        
        self.current_output = (your_action, his_action, total_possible, custom_reward)
        
        # Decay epsilon após cada jogo
        if self.last_round:
            self.epsilon = max(0.01, self.epsilon * 0.999)
            self.game_count += 1
            
    def _calculate_reward(self, your_action, his_action, actual_reward, total_possible):
        """Calcula recompensa customizada para melhorar aprendizado"""
        # Recompensa base similar ao RLAgent mas com bonificações
        if your_action == "steal" and his_action == "steal": 
            base_reward = 0
        elif your_action == "steal" and his_action == "split":
            base_reward = 2
        elif your_action == "split" and his_action == "split":
            base_reward = 1
        elif your_action == "split" and his_action == "steal":
            base_reward = -1
        
        # Adiciona pequenos ajustes baseados no contexto
        if your_action == "split" and his_action == "split":
            base_reward += 0.1  # Pequeno bônus por cooperação mútua
        
        return base_reward