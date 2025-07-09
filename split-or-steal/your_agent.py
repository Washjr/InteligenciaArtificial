import random

class ReinforcementLearningAgent:
  def __init__(self):
  
    # Lembrando a ultima acao
    self.last_opponent_action = None
    
    # Flag indicando se essa seria a ultima rodada
    self.last_round = False
    
  # Nome de seu agente deve ser colocado aqui  
  def get_name(self):
    return "Grupo/Apelido"

  # Um exemplo basico de algo proximo de tit-for-tat
  # apenas como demonstracao. Agente de aprendizagem
  # por reforco seria o objetivo
  def decision(self, amount, rounds_left, your_karma, his_karma):
    print(f"{amount=}, {rounds_left=}, {your_karma=}, {his_karma=}")
    self.last_round = True if rounds_left == 0 else False
    
    if self.last_opponent_action is None:
      return "split"
    elif self.last_opponent_action == "split":
      return "split"
    elif self.last_opponent_action == "steal":
      return "steal"
    else:
      raise RuntimeError("Unknown action")

  # Receba as acoes de cada agente e o reward obtido (vs total possivel)
  def result(self, your_action, his_action, total_possible, reward):
    if self.last_round:
      print("Forgetting last opponent action") # Vamos mudar de agente
      self.last_opponent_action = None;
    else:   
      self.last_opponent_action = his_action;
      print(f"For {self.get_name()=} {self.last_opponent_action=} ")    

