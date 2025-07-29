import time

_runtime_points_cache = dict()


class UserBuffer:
    def __init__(self, user_id, ques_message_id, last_ques_id):
        self.points = 0
        self.last_active_time = time.time()
        self.user_id = user_id
        self.ques_message_id = ques_message_id
        self.last_ques_id = last_ques_id


_runtime_buffer = dict()


def user_is_found(user_id):
    return str(user_id) in _runtime_buffer

def get_user(user_id):

    return _runtime_buffer[str(user_id)]

def delete_user(user_id):
    _runtime_buffer.pop(str(user_id), None)


def create_new_user(user_id, ques_message_id, last_ques_id):
    _runtime_buffer[str(user_id)] = UserBuffer(str(user_id), ques_message_id, last_ques_id)
    return _runtime_buffer[str(user_id)]
