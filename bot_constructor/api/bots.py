from collections import deque

from openai import OpenAI


client = OpenAI(
    base_url='https://openai.api.proxyapi.ru/v1'
)

bots = dict()


class MoveNotValidError(Exception):
    pass


class BotNotRunnableError(Exception):
    pass


class BotNotExistsError(Exception):
    pass


def get_ai_response(bot_description, step_details, previous, user_content):
    messages_payload = [
        {'role': 'system', 'content': bot_description}
    ] + list(previous) + [
        {'role': 'user', 'content': '. '.join([step_details, user_content])}
    ]
    ai_response = client.chat.completions.create(
        model='openai/gpt-5.4-nano',
        messages=messages_payload,
        max_completion_tokens=2000,
        temperature=1.0
    )
    return (
        ai_response.choices[0].message.content,
        ai_response.usage.completion_tokens
    )


def has_all_paths(steps):
    start = steps.get('start')
    reachable_steps_names = {'start'}
    stack_ = [start]
    while stack_:
        current_step = stack_.pop()
        for _, next_step_name in current_step.get('transitions').items():
            if next_step_name not in reachable_steps_names:
                reachable_steps_names.add(next_step_name)
                stack_.append(steps.get(next_step_name))
    if 'exit' not in reachable_steps_names:
        return False
    reachable_steps_names.remove('start')
    reachable_steps_names.remove('exit')
    verified_steps_names = {'start'}
    for intermediate_step_name in reachable_steps_names:
        visited_steps_names = {intermediate_step_name}
        intermediate_step = steps.get(intermediate_step_name)
        stack_ = [intermediate_step]
        found = False
        while stack_ and not found:
            current_step = stack_.pop()
            for _, next_step_name in (current_step
                                      .get('transitions').items()):
                if (next_step_name == 'exit' or
                        next_step_name in verified_steps_names):
                    found = True
                    break
                if next_step_name not in visited_steps_names:
                    visited_steps_names.add(next_step_name)
                    stack_.append(steps.get(next_step_name))
        if not found:
            return False
        verified_steps_names.add(intermediate_step_name)
    return True


class SimpleAIBot:
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
        self.bot_description = '. '.join(
            [self.chat_bot.description, self.scenario.description]
        )
        self.step = None
        self.previous = deque(maxlen=4)

    def is_runnable(self):
        if 'start' not in self.steps or 'exit' not in self.steps:
            return False
        return has_all_paths(self.steps)

    def start(self):
        self.step = self.steps.get('start')
        ai_message, completion_tokens = get_ai_response(
            self.bot_description,
            self.step.get('message'),
            self.previous,
            'Привет'
        )
        response = {
            'message': ai_message,
            'next': self.step.get('transitions').keys(),
            'completion_tokens': completion_tokens
        }
        return response

    def get_response(self, move, user_content=None):
        next_step_name = self.step.get('transitions').get(move)
        if next_step_name is None:
            raise MoveNotValidError(
                f'Options: {list(self.step.get('transitions').keys())}'
            )
        self.step = self.steps.get(next_step_name)
        ai_message, completion_tokens = get_ai_response(
            self.bot_description,
            self.step.get('message'),
            self.previous,
            user_content
        )
        response = {
            'message': ai_message,
            'completion_tokens': completion_tokens
        }
        if next_step_name == 'exit':
            response['next'] = '-'
            return response
        response['next'] = self.step.get('transitions').keys()
        self.previous.append({'role': 'user', 'content': user_content})
        self.previous.append({'role': 'assistant', 'content': ai_message})
        return response


def run_bots(user, chat_bot, move, user_content=None):
    if move == 'start':
        bot = SimpleAIBot(user, chat_bot)
        if not bot.is_runnable():
            raise BotNotRunnableError
        bots[(user, chat_bot)] = bot
        response = bot.start()
        return response
    else:
        bot = bots.get((user, chat_bot))
        if bot is None:
            raise BotNotExistsError
        response = bot.get_response(move, user_content)
        if response.get('next') == '-':
            bots.pop((user, chat_bot))
        return response


def test_openai():
    ai_response = client.chat.completions.create(
        model='openai/gpt-4.1-nano',
        messages=[
            {'role': 'system', 'content': 'Nice assistant'},
            {'role': 'user', 'content': 'Say hay. I am Taras Belyy'}
        ],
        max_tokens=100
    )
    print(ai_response.choices[0].message.content)
    print(ai_response.usage.completion_tokens)


if __name__ == '__main__':
    test_openai()
