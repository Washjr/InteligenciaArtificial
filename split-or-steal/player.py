class Player:
    def __init__(self, agent):
        self.agent = agent
        self.name = agent.get_name()
        self.total_amount = 0
        self.karma = 0
        self.last_decision = None

    def reset_karma(self) -> None:
        self.karma = 0

    def add_karma(self, value) -> None:
        self.karma = max(-5, min(5, self.karma + value))

    def decision(self, total_amount, rounds_left, your_karma, his_karma) -> str:
        self.last_decision = self.agent.decision(total_amount, rounds_left, your_karma, his_karma)
        return self.last_decision

    def result(self, your_action, his_action, total_possible, reward) -> None:
        self.agent.result(your_action, his_action, total_possible, reward)