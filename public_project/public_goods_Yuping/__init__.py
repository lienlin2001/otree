# Version 3/6


from otree.api import *

doc = """
Public Project Game
"""

class C(BaseConstants):
    NAME_IN_URL = 'public_project_game'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 96  # total is 72 rounds with 12 different sessions
    ROUNDS_IN_BLOCK = 48
    NUM_SESSIONS = 2

    # Timeout
    timeout_sec_showpayoff = 10
    timeout_sec_decision = 20  # 20 seconds for a round
    timeout_sec_results = 10

    # Payoff
    payoff_hete_low = '-6-8-10-12-' # use string is because otree can't save list
    payoff_hete_high = '-2-4-6-8-'
    payoff_homo_low = '-9-9-9-9-'
    payoff_homo_high ='-5-5-5-5-'
    payoff_fail = 5
    payoff_notcoop = 10
    NUM_PAYOFF = 4 # Number of scenarios for payoff

    # Threshold
    thresholds = [1, 2, 3, 4]

    # Round - should be removed
    blocks = ['known_full', 'known_limit', 'unknown_limit']
    known_full = [1, 9]
    known_limit = [10, 18]
    unknown_full = [19, 27]
    unknown_limit = [28, 36]


class Subsession(BaseSubsession):
    scenarios = models.IntegerField() # save the list of the sequence of the scenario for the group

class Group(BaseGroup):

   # Decision of the group
   voting_result = models.IntegerField()  # the voting result
   is_pass = models.BooleanField() #  Whether the project pass or not (voting_result >= threshold)

   # Scenario
   threshold = models.IntegerField()
   scenario = models.IntegerField()  # save the payoff for the payoff and threshold in each group

   # Blocks and Session
   block = models.IntegerField
   session = models.IntegerField

class Player(BasePlayer):

    # Decision
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Not cooperate']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,)  # Whether subject choose to cooperate or not

    is_no_decision = models.BooleanField()  # whether the subject decide within the time

    # Reaction time
    reaction_time = models.FloatField(initial=0)

    # Scenario
    fail_payoff = models.IntegerField(initial=C.payoff_fail) #payoff of failing the project
    noncoop_payoff = models.IntegerField(initial=C.payoff_notcoop) #payoff of not cooperate and the project pass
    coop_payoff = models.IntegerField() #payoff of cooperate and the project pass

    # Payoff
    actual_payoff = models.IntegerField() #actual payoff that the subject receive

    # Identity
    name = models.StringField() # The name used in the game
    identity = models.IntegerField() # The identity for each round

    # Test
    test1_1 = models.IntegerField(label="請填入你的答案:")
    test1_2 = models.IntegerField(label="請填入你的答案:")
    test1_3 = models.IntegerField(label="請填入你的答案:")
    test1_4 = models.IntegerField(label="請填入你的答案:")
    test1_5 = models.IntegerField(label="請填入你的答案:")

# Functions

def generate_scenarios(): # generate all the combination of the scenarios, there are total 16 scenarios
    scenarios = []
    scenario_payoff = [C.payoff_hete_high, C.payoff_hete_low, C.payoff_homo_high, C.payoff_homo_low]
    thresholds = C.thresholds
    for i in range(C.NUM_PAYOFF): # 0,1,2,3
        for j in thresholds:
            scenarios.append([scenario_payoff[i],j])
    return scenarios

def assign_name(group: Group): # assign each player his/her name in the session, change in different session
    import random
    import string
    names = [i for i in string.ascii_uppercase[:C.PLAYERS_PER_GROUP]]
    random.shuffle(names) # shuffle the sequence of name
    for p, i in zip(group.get_players(), range(C.PLAYERS_PER_GROUP)):
        p.name = names[i]
        p.participant.name = names[i]

def assign_identity_payoff(group: Group, scenario): # function that is used to assgin the identiy to each player in each round under different scenairos
    import random
    players = group.get_players() # return a list of all the players in the group
    identities = list(range(1,C.PLAYERS_PER_GROUP+1)) # generate the list of identity
    random.shuffle(identities)

    for p, i in zip(players, range(C.PLAYERS_PER_GROUP)):
        p.identity = identities[i]  # identity will change in every round
        p.coop_payoff = scenario[0][int(p.identity - 1)] # assign the corresponding identity's payoff for each player
        p.noncoop_payoff = C.payoff_notcoop
        p.fail_payoff = C.payoff_fail

def decode_payoff_list(scenario): # decode the payoff list I saved
    payoff_list = scenario.split('-')
    payoff_list = [int(s.strip()) for s in payoff_list]
    return payoff_list


'''
def assign_scenario(subsession: Subssession, scenarios):
    import random
    random.shuffle(scenarios)
    group = subsession.get_groups()
    for g in group:
        g.scenario = scenario[0]
        g.threshold = scenario[1]
'''

def creating_session(subsession): # creating session for unknown and known
    import random
    scenarios = generate_scenarios()

    if subsession.round_number % C.ROUNDS_IN_BLOCK == 1  : # If the round number can be divided by Rounds in a block now is round 1 and 37
        subsession.group_randomly()  # group randomly
        groups = subsession.get_groups()

        # assign name in the game for each group
        for g in groups:
            assign_name(g)

        # randomly assign the scenario for each group
        for g in groups:
            scenario = random.choice(scenarios)
            g.scenario = scenario[0]
            g.threshold = scenario[1]
            assign_identity_payoff(g, scenario)  # assign identity for each player

    else:
        subsession.group_like_round((subsession.round_number//C.ROUNDS_IN_BLOCK)+1) # it should be like round 1 or 37
        groups = subsession.get_groups()

        for p in subsession.get_players():
            p.name = p.participant.name

        # assign the scenario for each group
        for g in groups:
            scenario = random.choice(scenarios)
            g.scenario = scenario[0]
            g.threshold = scenario[1]
            assign_identity_payoff(g, scenario) # assign identity for each player

    # assign blocks
    block_list = C.blocks
    for g in subsession.get_groups():
        random.shuffle(block_list)
        if 1 <= subsession.round_number <= 16 or  49 <= subsession.round_number <= 64:
            g.block = block_list[0]
        elif 17 <= subsession.round_number <= 32 or  65 <= subsession.round_number <= 80:
            g.block = block_list[1]
        elif 33 <= subsession.round_number <= 48 or 81 <= subsession.round_number <= 96:
            g.block = block_list[2]

def set_payoffs(group:Group): # set the payoff of the decision made
    players = group.get_players()
    voting_result = [p.cooperate for p in players]
    group.voting_result = sum(voting_result)

    for p in players:
        if group.voting_result >= group.threshold:
            if p.cooperate == True:
                p.actual_payoff = p.coop_payoff
            else:
                p.actual_payoff = p.noncoop_payoff
        else:
            p.actual_payoff = p.fail_payoff


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == 1  # only round 1 need experiment instruction

class Introduction2(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == C.ROUNDS_IN_BLOCK + 1 # When the session is finished

class Instructions_showpayoff(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == 1  # only round 1 need experiment instruction

class Instructions_decision(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == 1  # only round 1 need experiment instruction

class Instructions_results(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.round_number == 1  # only round 1 need experiment instruction

class Instructions_known_full(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'known_full'  # only display in the round for known full

class Instructions_known_limit(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'known_limit'  # only display in the round for known full

class Instructions_unknown_limit(Page):
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'unknown_limit'  # only display in the round for known full

class InstructionsWaitPage(WaitPage): # Wait for everyone in the same group to finish instructions
    wait_for_all_groups = False # make sure it won't wait for all the participant

class Show_payoff(Page):

    timeout_seconds = C.timeout_sec_showpayoff

    '''@staticmethod
    def is_displayed(player):  # built-in methods
        return C.unknown_limit[1] >= player.round_number >= C.known_full[0] # don't need this line'''

    @staticmethod
    def vars_for_template(player: Player):  # Use this to pass variables to the template.

        scenario_list = decode_payoff_list(player.group.scenario)

        return dict(
            scenario_payoff1=scenario_list[0],
            scenario_payoff2=scenario_list[1],
            scenario_payoff3=scenario_list[2],
            scenario_payoff4=scenario_list[3],
        )

class Decision_known(Page): #knowing other people's identity and their payoff
    form_model = 'player'
    form_fields = ['cooperate', 'reaction_time']
    timeout_seconds = C.timeout_sec_decision  # built-in
    threshold = Group.threshold

    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'known_full' or 'known_limit'

    @staticmethod
    def before_next_page(player, timeout_happened):  # built-in methods
        import random
        if timeout_happened:
            player.is_no_decision = True  # if the time is up, set player as making no decision
            player.cooperate = random.choice([True, False]) # set the decision of not choice as random

    @staticmethod
    def vars_for_template(player: Player): # Use this to pass variables to the template.
        player_name_list = [0, 0, 0, 0]
        for p in player.group.get_players():  # show the player's identity on page
            if p.identity == 1:
                player_name_list[0] = p.name
            elif p.identity == 2:
                player_name_list[1] = p.name
            elif p.identity == 3:
                player_name_list[2] = p.name
            else:
                player_name_list[3] = p.name

        scenario_list = decode_payoff_list(player.group.scenario)

        return dict(
            player_name = player_name_list,
            scenario_payoff1 = scenario_list[0],
            scenario_payoff2 = scenario_list[1],
            scenario_payoff3 = scenario_list[2],
            scenario_payoff4 = scenario_list[3],
            name1 = player_name_list[0],
            name2 = player_name_list[1],
            name3 = player_name_list[2],
            name4 = player_name_list[3],
        )

class Decision_unknown(Page): # Don't know other people's identity
    form_model = 'player'
    form_fields = ['cooperate', 'reaction_time']
    timeout_seconds = C.timeout_sec_decision  # built-in
    threshold = Group.threshold

    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'unknown_limit'

    @staticmethod
    def before_next_page(player, timeout_happened):  # built-in methods
        import random
        if timeout_happened:
            player.is_no_decision = True  # if the time is up, set player as making no decision
            player.cooperate = random.choice([True, False]) # set the decision of not choice as random


    @staticmethod
    def vars_for_template(player: Player): # Use this to pass variables to the template.

        scenario_list = decode_payoff_list(player.group.scenario)

        return dict(
            scenario_payoff1 = scenario_list[0],
            scenario_payoff2 = scenario_list[1],
            scenario_payoff3 = scenario_list[2],
            scenario_payoff4 = scenario_list[3],
        )

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = False # make sure it won't wait for all the participant
    after_all_players_arrive = set_payoffs # built-in methods. After every subjects decided, activate set_payoffs


class Results_known_full(Page):
    '''
    timeout_seconds = C.timeout_sec_results  # built-in
    '''
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'known_full'

    @staticmethod
    def vars_for_template(player: Player):  # Use this to pass variables to the template.
        player_name_list = [0, 0, 0, 0]
        player_actual_payoff = [0, 0, 0, 0]
        player_decision = [0, 0, 0, 0]
        color = [0, 0, 0, 0]

        for p in player.group.get_players():  # show the player's identity on page

            if p.identity == 1:
                player_name_list[0] = p.name
                player_actual_payoff[0] = p.actual_payoff
                player_decision.append(p.cooperate)
                if p.cooperate == True:
                    player_decision1 = '合作'
                else:
                    player_decision1 = '不合作'
            elif p.identity == 2:
                player_name_list[1] = p.name
                player_actual_payoff[1] = p.actual_payoff
                player_decision.append(p.cooperate)
                if p.cooperate == True:
                    player_decision2 = '合作'
                else:
                    player_decision2 = '不合作'
            elif p.identity == 3:
                player_name_list[2] = p.name
                player_actual_payoff[2] = p.actual_payoff
                player_decision.append(p.cooperate)
                if p.cooperate == True:
                    player_decision3 = '合作'
                else:
                    player_decision3 = '不合作'
            else:
                player_name_list[3] = p.name
                player_actual_payoff[3] = p.actual_payoff
                player_decision.append(p.cooperate)
                if p.cooperate == True:
                    player_decision4 = '合作'
                else:
                    player_decision4 = '不合作'

        scenario_list = decode_payoff_list(player.group.scenario)

        for d in player_decision:
            if d == True:
                color.append('red')
            else:
                color.append('blue')

        return dict(
            player_name=player_name_list,
            scenario_payoff1=scenario_list[0],
            scenario_payoff2=scenario_list[1],
            scenario_payoff3=scenario_list[2],
            scenario_payoff4=scenario_list[3],
            name1=player_name_list[0],
            name2=player_name_list[1],
            name3=player_name_list[2],
            name4=player_name_list[3],
            decision1 = player_decision1,
            decision2 = player_decision2,
            decision3 = player_decision3,
            decision4 = player_decision4,
            actual_payoff1 = player_actual_payoff[0],
            actual_payoff2 = player_actual_payoff[1],
            actual_payoff3 = player_actual_payoff[2],
            actual_payoff4 = player_actual_payoff[3],
            color1=color[0],
            color2=color[1],
            color3=color[2],
            color4=color[3]

        )


class Results_known_limit(Page): # also can be used in down_down_up
    '''
    timeout_seconds = C.timeout_sec_results
    '''
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'known_limit'

    @staticmethod
    def vars_for_template(player: Player):  # Use this to pass variables to the template.

        player_actual_payoff = [0, 0, 0, 0]
        for p in player.group.get_players():  # show the player's identity on page
            if p.identity == 1:
                player_actual_payoff[0] = p.actual_payoff
                if p.cooperate == True:
                    player_decision1 = '合作'
                else:
                    player_decision1 = '不合作'
            elif p.identity == 2:
                player_actual_payoff[1] = p.actual_payoff
                if p.cooperate == True:
                    player_decision2 = '合作'
                else:
                    player_decision2 = '不合作'
            elif p.identity == 3:
                player_actual_payoff[2] = p.actual_payoff
                if p.cooperate == True:
                    player_decision3 = '合作'
                else:
                    player_decision3 = '不合作'
            else:
                player_actual_payoff[3] = p.actual_payoff
                if p.cooperate == True:
                    player_decision4 = '合作'
                else:
                    player_decision4 = '不合作'

        scenario_list = decode_payoff_list(player.group.scenario)

        return dict(
            scenario_payoff1=scenario_list[0],
            scenario_payoff2=scenario_list[1],
            scenario_payoff3=scenario_list[2],
            scenario_payoff4=scenario_list[3],
            decision1 = player_decision1,
            decision2 = player_decision2,
            decision3 = player_decision3,
            decision4 = player_decision4,
            actual_payoff1 = player_actual_payoff[0],
            actual_payoff2 = player_actual_payoff[1],
            actual_payoff3 = player_actual_payoff[2],
            actual_payoff4 = player_actual_payoff[3],
        )


class Results_unknown_limit(Page): # also can be used in known_limit
    '''
    timeout_seconds = C.timeout_sec_results
    '''
    @staticmethod
    def is_displayed(player):  # built-in methods
        return player.group.block == 'unknown_limit'

    @staticmethod
    def vars_for_template(player: Player):  # Use this to pass variables to the template.

        scenario_list = decode_payoff_list(player.group.scenario)

        decision_list = ['?', '?', '?', '?']
        if player.cooperate == True:
            decision_list[player.identity - 1] = "合作"
        else:
            decision_list[player.identity - 1] = "不合作"

        player_actual_payoff = ['?', '?', '?', '?']
        player_actual_payoff[player.identity - 1] = player.actual_payoff

        return dict(
            scenario_payoff1=scenario_list[0],
            scenario_payoff2=scenario_list[1],
            scenario_payoff3=scenario_list[2],
            scenario_payoff4=scenario_list[3],
            decision1=decision_list[0],
            decision2=decision_list[1],
            decision3=decision_list[2],
            decision4=decision_list[3],
            actual_payoff1=player_actual_payoff[0],
            actual_payoff2=player_actual_payoff[1],
            actual_payoff3=player_actual_payoff[2],
            actual_payoff4=player_actual_payoff[3],
        )

class Finish(Page):
    timeout_seconds = 60

    @staticmethod
    def is_displayed(player): # display if the condition satisfy
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):  # built-in methods，將 total_payoff 的值傳到 html 頁面
        return {
            "total_payoff": sum([p.actual_payoff for p in player.in_all_rounds()])
        }

page_sequence = [Introduction, Introduction2, Instructions_showpayoff, Instructions_decision, Instructions_results,  Instructions_unknown_limit, Instructions_known_full, Instructions_known_limit, InstructionsWaitPage, Show_payoff, Decision_known, Decision_unknown, ResultsWaitPage, Results_known_full, Results_known_limit, Results_unknown_limit, Finish ]

        