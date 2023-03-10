from otree.api import Bot
from . import *


#testing the experiment using bot
class PlayerBot(Bot):

    def play_round(self):

        # Instructions
        if self.round_number == 1:
            yield Instructions
            yield Instructions2

        if self.round_number == C.known_full[0]:
            yield Instructions_known_full
        elif self.round_number == C.known_limit[0]:
            yield Instructions_known_limit
        elif self.round_number == C.unknown_full[0]:
            yield Instructions_unknown_full
        elif self.round_number == C.unknown_limit[0]:
            yield Instructions_unknown_limit

        # Show_payoff
        if C.unknown_limit[1] >= self.round_number >= C.known_full[0]:
            yield Show_payoff

        # Decision
        if C.known_limit[1] >= self.round_number >= C.known_full[0]:
            yield Decision_known, dict(cooperate=True)
        else:
            yield Decision_unknown, dict(cooperate=True)

        # Results
        if C.known_full[1] >= self.round_number >= C.known_full[0]:
            yield Results_known_full
        elif C.unknown_full[1] >= self.round_number >= C.unknown_full[0]:
            yield Results_unknown_full
        elif C.known_limit[1] >= self.round_number >= C.known_limit[0] or C.unknown_limit[1] >= self.round_number >= C.unknown_limit[0]:
            yield Results_unknown_limit

