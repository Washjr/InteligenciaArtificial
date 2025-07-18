import random
import numpy as np

def always_split_callback(total_amount, rounds_left, your_karma, his_karma):
    return 'split'

def always_steal_callback(total_amount, rounds_left, your_karma, his_karma):
    return 'steal'

def always_random_callback(total_amount, rounds_left, your_karma, his_karma):
    return random.choice(['steal', 'split'])

def always_his_karma_callback(total_amount, rounds_left, your_karma, his_karma):
    return "split" if his_karma >= 0 else "steal" 

def always_steal_on_last_round_callback(total_amount, rounds_left, your_karma, his_karma):
    return "steal" if rounds_left <= 0 else "split" 

def always_karma_positive_callback(total_amount, rounds_left, your_karma, his_karma):
    return "steal" if your_karma >= 1 else "split" 


class StaticAgent:
    def __init__(self, name, decision_callback):
        self.decision_callback = decision_callback
        self.name = name
      
    def get_name(self):
        return self.name

    def decision(self, total_amount, rounds_left, your_karma, his_karma):
        return self.decision_callback(total_amount, rounds_left, your_karma, his_karma)

    def result(self, your_action, his_action, total_possible, reward):
        pass

class Splitter(StaticAgent):
    def __init__(self):
        super().__init__("Splitter", always_split_callback)
      
class Stealer(StaticAgent):
    def __init__(self):
        super().__init__("Stealer", always_steal_callback)   

class Randy(StaticAgent):
    def __init__(self):
        super().__init__("Randy", always_random_callback)  

class Karmine(StaticAgent):
    def __init__(self):
        super().__init__("Karmine", always_his_karma_callback)  
    
class Pretender(StaticAgent):
    def __init__(self):
        super().__init__("Pretender", always_karma_positive_callback)  

class Opportunist(StaticAgent):
    def __init__(self):
        super().__init__("Opportunist", always_steal_on_last_round_callback)   


class TitForTat(StaticAgent):
    """
    Tit-for-Tat: começa cooperando e depois imita a última ação do oponente.
    """
    def __init__(self):
        super().__init__("TitForTat", decision_callback=None)
        self.last_opponent_action = None
        self.last_round = False

    def decision(self, total_amount, rounds_left, your_karma, his_karma):
        self.last_round = True if rounds_left == 0 else False

        if self.last_opponent_action is None:
            return "split"
        return self.last_opponent_action

    def result(self, your_action, his_action, total_possible, reward):  
        self.last_opponent_action = None if self.last_round else his_action  


class Pavlov(StaticAgent): 
    """
    Win-Stay, Lose-Shift (Pavlov): se ganhou algo, repete própria ação; senão, troca.
    """
    def __init__(self):
        super().__init__('Pavlov', decision_callback=None)
        self.last_action = 'split'
        self.last_round = False

    def decision(self, total_amount, rounds_left, your_karma, his_karma) -> str:
        self.last_round = True if rounds_left == 0 else False

        return self.last_action

    def result(self, your_action, his_action, total_possible, reward) -> None:
        if reward > 0:
            self.last_action = your_action
        else:
            self.last_action = 'steal' if your_action == 'split' else 'split'

        if self.last_round:
            self.last_action = 'split' 


class ThresholdAgent(StaticAgent):
    """
    Percentile Threshold: rouba se o valor atual está abaixo de um percentil
    dos valores observados; senão divide.
    """
    def __init__(self, percentile: float = 50.0):
        super().__init__(f'Threshold{int(percentile)}', decision_callback=None)
        self.history = []
        self.percentile = percentile
        self.last_round = False

    def decision(self, total_amount, rounds_left, your_karma, his_karma) -> str:        
        self.last_round = True if rounds_left == 0 else False

        if not self.history:
            thresh = total_amount
        else:
            thresh = float(np.percentile(self.history, self.percentile))

        self.history.append(total_amount)
        return 'steal' if total_amount < thresh else 'split'

    def result(self, your_action, his_action, total_possible, reward) -> None:
        if self.last_round:
            self.history.clear()


