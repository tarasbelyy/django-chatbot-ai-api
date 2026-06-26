bots = dict()


class SimpleBot:
    def __init__(self, chat_bot, user):
        self.user = user
        self.chat_bot = chat_bot
        self.scenario = chat_bot.scenario
        self.steps = {
            step.name: {
                'message': step.message,
                'transitions': step.transitions
            } for step in self.scenario.steps.all()
        }
        self.step = None
    
    def is_runnable(self):
        return True
    
    def start(self):
        self.step = 'start'
        step = self.steps.get('start')
        responce = ...
        return responce
    
    def get_response(self, move, detail=None):
        next_step_name = self.step.transitions.get(move)
        if next_step_name is None:
            return ...
        self.step = self.steps.get(next_step_name)
        if self.step.name == 'exit':
            ...
        responce = ...
        return responce
    

def run_bots(chat_bot, user, move, detail=None):
    if move == 'start':
        bot = SimpleBot(chat_bot, user)
        if not bot.is_runnable():
            return ...
        bots[(chat_bot, user)] = bot
        response = bot.start()
        return response
    else:
        bot = bots.get((chat_bot, user))
        if bot is None:
            return ...
        response = bot.get_response(move, detail)
        if response.get('transitions') == 'exit':
            del bots[(chat_bot, user)]
        return response
