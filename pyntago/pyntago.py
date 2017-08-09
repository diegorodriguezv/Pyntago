#! /usr/bin/env python
"""Pyntago: A pentago board in python."""

import pygame
from pygame.locals import *


def debug(msg):
    print(msg)


DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

COLOR_TRANSPARENT = (0, 0, 0, 0)
COLOR_BLOCK = (200, 10, 10)
COLOR_HOLE = (165, 42, 42)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)


class Event:
    """Superclass for any event."""

    def __init__(self):
        self.name = "Generic event"


class CycleEvent(Event):
    def __init__(self):
        self.name = "CPU cycle event"


class QuitEvent(Event):
    def __init__(self):
        self.name = "Program quit event"


class BoardBuiltEvent(Event):
    def __init__(self, board):
        self.name = "Board built event"
        self.board = board


class GameStartedEvent(Event):
    def __init__(self, game):
        self.name = "Game started event"
        self.game = game


class PlaceMarbleEvent(Event):
    def __init__(self, marble):
        self.name = "Place marble event"
        self.marble = marble


class RotateBlockEvent(Event):
    def __init__(self, block):
        self.name = "Rotate block event"
        self.block = block


class MoveCursorRequestEvent(Event):
    def __init__(self, cursor):
        self.name = "Move cursor request event"
        self.cursor = cursor


class SelectCursorRequestEvent(Event):
    def __init__(self, cursor):
        self.name = "Select cursor request event"
        self.cursor = cursor


class EventManager:
    """"Coordinates communication between Models, Views and Controllers."""

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []

    def register_listener(self, listener):
        self.listeners[listener] = 1

    def deregister_listener(self, listener):
        if listener in self.listeners:
            del self.listeners[listener]

    def post(self, event):
        if not isinstance(event, CycleEvent):
            debug("Event: " + event.name)
        for listener in self.listeners:
            listener.notify(event)


class KeyboardController:
    """Takes pygame events from the keyboard to control the model."""

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)

    def notify(self, event):
        if isinstance(event, CycleEvent):
            for input_event in pygame.event.get():
                new_event = None
                if input_event.type == QUIT:
                    new_event = QuitEvent()
                elif input_event.type == KEYDOWN:
                    if input_event.key == K_ESCAPE:
                        new_event = QuitEvent()
                    elif input_event.key == K_UP or input_event.key == K_w:
                        new_event = MoveCursorRequestEvent(DIRECTION_UP)
                    elif input_event.key == K_DOWN or input_event.key == K_s:
                        new_event = MoveCursorRequestEvent(DIRECTION_DOWN)
                    elif input_event.key == K_LEFT or input_event.key == K_a:
                        new_event = MoveCursorRequestEvent(DIRECTION_LEFT)
                    elif input_event.key == K_RIGHT or input_event.key == K_d:
                        new_event = MoveCursorRequestEvent(DIRECTION_RIGHT)
                    elif input_event.key == K_RETURN:
                        new_event = SelectCursorRequestEvent()
                if new_event:
                    self.manager.post(new_event)


class CycleController:
    """Controls the CPU (animation) cycle."""

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.alive = True

    def run(self):
        while self.alive:
            self.manager.post(CycleEvent())

    def notify(self, event):
        if isinstance(event, QuitEvent):
            # stop the loop
            self.alive = False


class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.block = block
        self.image = pygame.Surface((300, 300))
        self.image.fill(COLOR_BLOCK)
        # draw the 9 holes in the block
        hole = pygame.Surface((100, 100))
        hole = hole.convert_alpha()
        hole.fill(COLOR_TRANSPARENT)
        pygame.draw.circle(hole, COLOR_HOLE, (50, 50), 20, 3)
        for i in range(3):
            for j in range(3):
                self.image.blit(hole, (i * 100, j * 100))


class MarbleSprite(pygame.sprite.Sprite):
    def __init__(self, marble, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.marble = marble
        self.image = pygame.Surface((100, 100))
        self.image.fill(marble.color)


class PygameView:
    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        pygame.init()
        self.window = pygame.display.set_mode((850, 900))
        pygame.display.set_caption("Pyntago")
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill(COLOR_BLACK)
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text = "Starting..."
        text_img = my_font.render(text, 1, COLOR_WHITE)
        self.background.blit(text_img, (0, 850))
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()
        self.back_sprites = pygame.sprite.RenderUpdates()
        self.front_sprites = pygame.sprite.RenderUpdates()

    def show_board(self, board):
        self.background.fill(COLOR_WHITE)
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()
        block_position = pygame.Rect((-300 + 124, 124, 300, 300))
        column = 0
        for block in board.blocks:
            if column < 2:
                block_position = block_position.move(301, 0)
            else:
                column = 0
                block_position = block_position.move(-301, 301)
            column += 1
            new_sprite = BlockSprite(block, self.back_sprites)
            new_sprite.rect = block_position

    def get_block_sprite(self, block):
        for sprite in self.back_sprites:
            if hasattr(sprite, "block") and sprite.block == block:
                return sprite

    def notify(self, event):
        if isinstance(event, CycleEvent):
            self.back_sprites.clear(self.window, self.background)
            self.front_sprites.clear(self.window, self.background)
            self.back_sprites.update()
            self.front_sprites.update()
            dirty_rects_back = self.back_sprites.draw(self.window)
            dirt_rects_front = self.front_sprites.draw(self.window)
            pygame.display.update(dirt_rects_front + dirty_rects_back)
        elif isinstance(event, BoardBuiltEvent):
            self.show_board(event.board)
            # todo: PlaceMarbleEvent
            # todo: RotateBlockEvent
            # todo: MoveCursorRequestEvent
            # todo: SelectCursorRequestEvent


class Game:
    """Model of the game."""
    STATE_PREPARING = 'preparing'
    STATE_RUNNING = 'running'
    STATE_PAUSED = 'paused'

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.state = Game.STATE_PREPARING
        self.players = [Player(event_manager, "White", COLOR_WHITE), Player(event_manager, "Black", COLOR_BLACK)]
        self.board = Board(event_manager)

    def start(self):
        self.board.build()
        self.state = Game.STATE_RUNNING
        self.manager.post(GameStartedEvent(self))

    def notify(self, event):
        if isinstance(event, CycleEvent):
            if self.state == Game.STATE_PREPARING:
                self.start()


class Player:
    """Model of a player."""

    def __init__(self, event_manager, name, color):
        self.manager = event_manager
        self.game = None
        self.name = name
        self.color = color
        self.manager.register_listener(self)

    def __str__(self):
        return '<Player %s %s>'.format(self.name, id(self))

    def notify(self, event):
        pass


class Board:
    """Model of the board."""
    STATE_PREPARING = 'preparing'
    STATE_BUILT = 'built'

    def __init__(self, event_manager):
        self.manager = event_manager
        self.state = Board.STATE_PREPARING
        self.blocks = []

    def build(self):
        for i in range(4):
            self.blocks.append(Block(self.manager))

        # todo: declare neighbors
        self.state = Board.STATE_BUILT
        self.manager.post(BoardBuiltEvent(self))


class Block:
    """Model of a block."""

    def __init__(self, event_manager):
        self.manager = event_manager
        # todo: declare neighbors


def main():
    """Program entry point."""
    manager = EventManager()
    keybd = KeyboardController(manager)
    cycle = CycleController(manager)
    view = PygameView(manager)
    game = Game(manager)
    cycle.run()


if __name__ == "__main__":
    main()
