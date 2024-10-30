from pico2d import *
import random

def start_event(e):
    return e[0] == 'START'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def auto_run_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass

class AutoRun:
    @staticmethod
    def enter(boy, e=None):
        if boy.face_dir==1:
            boy.dir = 3
            boy.action = 0
        if boy.face_dir==-1:
            boy.dir = -3
            boy.action = 0


    @staticmethod
    def exit(boy, e=None):
        boy.dir = 0  # AutoRun 종료 시 멈춤
        boy.face_dir=boy.face_dir*-1

    @staticmethod
    def do(boy):
        if boy.dir>0:
            boy.face_dir = -1
        else:
            boy.face_dir = 1
        boy.x += boy.dir * 5
        boy.frame = (boy.frame + 1) % 8  # 애니메이션 프레임 업데이트

        # 경계를 체크하여 방향 전환
        if boy.x <= 0:
            boy.dir = 3
            boy.face_dir = 1
        if boy.x >= 800:
            boy.dir = -3
            boy.face_dir = -1

        # 5초가 지나면 Idle로 전환
        if get_time() - boy.start_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))  # 타임아웃 이벤트 발생
            # 화살표 키 입력에 따라 상태 전환
            if boy.state_machine.event_q:
                for event in boy.state_machine.event_q:
                    if right_down(event):
                        boy.state_machine.add_event(('INPUT', event[1]))
                        boy.state_machine.add_event(('KEY_EVENT', event[1]))  # 키 이벤트 추가
                    elif left_down(event):
                        boy.state_machine.add_event(('INPUT', event[1]))
                        boy.state_machine.add_event(('KEY_EVENT', event[1]))  # 키 이벤트 추가
    @staticmethod
    def draw(boy):
        # 방향에 따라 소년 그리기
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                           0, '', boy.x, boy.y, 170, 170)
        else:  # 왼쪽으로 향하는 경우
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                           0, 'h', boy.x, boy.y, 170, 170)

class Idle:
    @staticmethod
    def enter(boy, e=None):
        if boy.face_dir == 1:
            boy.action = 3
        elif boy.face_dir == -1:
            boy.action = 2
        boy.start_time = get_time()  # Idle 상태의 시작 시간을 초기화

    @staticmethod
    def exit(boy, e=None):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 2:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e):
            boy.dir, boy.face_dir, boy.action = 1, 1, 1
        elif left_down(e):
            boy.dir, boy.face_dir, boy.action = -1, -1, 0
        elif right_up(e) or left_up(e):
            boy.dir = 0

    @staticmethod
    def exit(boy, e=None):
        boy.dir = 0

    @staticmethod
    def do(boy):
        boy.x += boy.dir * 5
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class Sleep:
    @staticmethod
    def enter(boy, e=None):
        boy.action = 3
        boy.frame = 0

    @staticmethod
    def exit(boy, e=None):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2,  # 90-degree rotation
                '',  # No flip
                boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:

            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                -3.141592 / 2,  # -90-degree rotation
                'h',  # Horizontal flip
                boy.x + 25, boy.y - 25, 100, 100
            )


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


class StateMachine:
    def __init__(self, obj):
        self.obj = obj
        self.event_q = []  # 이벤트 저장 큐

    def start(self, state):
        self.cur_state = state
        self.cur_state.enter(self.obj, ('START', 0))

    def update(self):
        while self.event_q:
            e = self.event_q.pop(0)

            for check_event, next_state in self.transitions.get(self.cur_state, {}).items():
                if check_event(e):
                    self.cur_state.exit(self.obj, e)
                    self.cur_state = next_state
                    self.cur_state.enter(self.obj, e)
                    return

        self.cur_state.do(self.obj)

    def draw(self):
        self.cur_state.draw(self.obj)

    def add_event(self, e):
        self.event_q.append(e)

    def set_transitions(self, transitions):
        self.transitions = transitions


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.face_dir = 1  # 초기 face_dir을 오른쪽(1)으로 설정
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Run: {right_up: Idle, left_up: Idle, left_down: Run, right_down: Run},
                Idle: {time_out: Sleep, right_down: Run, left_down: Run, auto_run_down: AutoRun},
                Sleep: {space_down: Idle, right_down: Run, left_down: Run},
                AutoRun: {time_out: Idle, right_down: Run, left_down: Run}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.add_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()


def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

        else:
            if event.type in (SDL_KEYDOWN, SDL_KEYUP):
                boy.handle_event(event)


def reset_world():
    global running
    global grass
    global world
    global boy

    running = True
    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)


def update_world():
    for o in world:
        o.update()


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()