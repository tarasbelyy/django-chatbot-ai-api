bots = dict()


class MoveNotValidError(Exception):
    pass


class BotNotRunnableError(Exception):
    pass


class BotNotExistsError(Exception):
    pass


class SimpleBot:
    def __init__(self, user, chat_bot):
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
        self.step = self.steps.get('start')
        response = {
            'message': self.step.get('message'),
            'next': self.step.get('transitions').keys()
        }
        return response
    
    def get_response(self, move, detail=None):
        next_step_name = self.step.get('transitions').get(move)
        if next_step_name is None:
            raise MoveNotValidError(
                f'Options: {list(self.step.get('transitions').keys())}'
            )
        self.step = self.steps.get(next_step_name)
        if next_step_name == 'exit':
            response = {
                'message': self.step.get('message'),
                'next': 'exit'
            }
            return response
        response = {
            'message': self.step.get('message'),
            'next': self.step.get('transitions').keys()
        }
        return response


def run_bots(user, chat_bot, move, detail=None):
    if move == 'start':
        bot = SimpleBot(user, chat_bot)
        if not bot.is_runnable():
            raise BotNotRunnableError
        bots[(user, chat_bot)] = bot
        response = bot.start()
        return response
    else:
        bot = bots.get((user, chat_bot))
        if bot is None:
            raise BotNotExistsError
        response = bot.get_response(move, detail)
        if response.get('next') == 'exit':
            bots.pop((user, chat_bot))
        return response
