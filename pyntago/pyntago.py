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


# Keyboard events
class MoveRequestEvent(Event):
    def __init__(self, direction):
        self.name = "Move request event"
        self.direction = direction


class SelectEvent(Event):
    def __init__(self):
        self.name = "Select event"


# Marble events
class PlaceMarbleEvent(Event):
    def __init__(self, marble, player):
        self.name = "Place marble event"
        self.marble = marble
        self.player = player


# Block events
class RotateBlockEvent(Event):
    def __init__(self, block, player):
        self.name = "Rotate block event"
        self.block = block
        self.player = player


class MoveBlockCursorRequestEvent(Event):
    def __init__(self, block_cursor, player, direction):
        self.name = "Move block cursor request event"
        self.block_cursor = block_cursor
        self.player = player
        self.direction = direction


class MoveBlockCursorEvent(Event):
    def __init__(self, block_cursor, player, direction):
        self.name = "Move block cursor event"
        self.block_cursor = block_cursor
        self.player = player
        self.direction = direction


class SelectBlockCursorEvent(Event):
    def __init__(self, block_cursor, player):
        self.name = "Select block cursor request event"
        self.block_cursor = block_cursor
        self.player = player


class PlaceBlockCursorEvent(Event):
    def __init__(self, block_cursor):
        self.name = "Place block cursor event"
        self.block_cursor = block_cursor


# Game events
class GameMoveUIEvent(Event):
    def __init__(self, game):
        self.name = "Start move UI event"
        self.game = game


class GameRotateUIEvent(Event):
    def __init__(self, game):
        self.name = "Start rotate UI event"
        self.game = game


class MessageUpdateEvent(Event):
    def __init__(self, game):
        self.name = "Message update event"
        self.game = game


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
                        new_event = MoveRequestEvent(DIRECTION_UP)
                    elif input_event.key == K_DOWN or input_event.key == K_s:
                        new_event = MoveRequestEvent(DIRECTION_DOWN)
                    elif input_event.key == K_LEFT or input_event.key == K_a:
                        new_event = MoveRequestEvent(DIRECTION_LEFT)
                    elif input_event.key == K_RIGHT or input_event.key == K_d:
                        new_event = MoveRequestEvent(DIRECTION_RIGHT)
                    elif input_event.key == K_RETURN:
                        new_event = SelectEvent()
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


class BlockCursorSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface((300, 300))
        self.image = self.image.convert_alpha()
        self.image.fill(COLOR_TRANSPARENT)
        pygame.draw.rect(self.image, COLOR_BLACK, (10, 10, 280, 280), 3)
        self.rect = self.image.get_rect()
        self.move_to = None

    def update(self):
        if self.move_to:
            self.rect.center = self.move_to
            self.move_to = None


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


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, size, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.font = pygame.font.SysFont("Arial", size)
        self.text_surf = self.font.render(text, 1, color)
        self.Surf = pygame.Surface((width, height))
        w = self.text_surf.get_width()
        h = self.text_surf.get_height()
        self.Surf.blit(self.text_surf, width / 2 - w / 2, height / 2 - h / 2)



class PygameView:
    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        pygame.init()
        self.window = pygame.display.set_mode((850, 900))
        pygame.display.set_caption("Pyntago")
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill(COLOR_BLACK)
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
        # message_sprite = TextSprite()

    def show_block_cursor(self, block_cursor):
        cursor_sprite = BlockCursorSprite(self.front_sprites)
        block_sprite = self.get_block_sprite(block_cursor.block)
        cursor_sprite.rect.center = block_sprite.rect.center

    def move_block_cursor(self, block_cursor):
        block_cursor_sprite = self.get_block_cursor_sprite()
        block_sprite = self.get_block_sprite(block_cursor.block)
        block_cursor_sprite.move_to = block_sprite.rect.center

    def get_block_sprite(self, block):
        for sprite in self.back_sprites:
            if hasattr(sprite, "block") and sprite.block == block:
                return sprite

    def get_block_cursor_sprite(self):
        for sprite in self.front_sprites:
            # there will be only one
            if isinstance(sprite, BlockCursorSprite):
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
        elif isinstance(event, PlaceBlockCursorEvent):
            self.show_block_cursor(event.block_cursor)
        elif isinstance(event, MoveBlockCursorEvent):
            self.move_block_cursor(event.block_cursor)

            # todo: PlaceMarbleEvent
            # todo: RotateBlockEvent
            # todo: MoveCursorRequestEvent
            # todo: SelectCursorRequestEvent


class Game:
    """Model of the game."""
    STATE_PREPARING = 'preparing'
    STATE_MOVE = 'awaiting move'
    STATE_ROTATE = 'awaiting rotation'

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.state = Game.STATE_PREPARING
        self.players = [Player(event_manager, "White", COLOR_WHITE), Player(event_manager, "Black", COLOR_BLACK)]
        self.board = Board(event_manager)
        self.current_player = self.players[0]
        self.message = "%s's turn".format(self.current_player)
        self.block_cursor = BlockCursor(event_manager)

    def start(self):
        self.board.build()
        self.state = Game.STATE_MOVE
        # todo: just to test bock cursor movement
        self.state = Game.STATE_ROTATE
        self.manager.post(GameRotateUIEvent(self))

    def notify(self, event):
        if isinstance(event, CycleEvent):
            if self.state == Game.STATE_PREPARING:
                self.start()
        if isinstance(event, PlaceMarbleEvent):
            if self.state == Game.STATE_MOVE:
                self.state = Game.STATE_ROTATE
        if isinstance(event, RotateBlockEvent):
            if self.state == Game.STATE_ROTATE:
                self.state = Game.STATE_MOVE
        if isinstance(event, MoveRequestEvent):
            if self.state == Game.STATE_ROTATE:
                self.manager.post(MoveBlockCursorRequestEvent(self.block_cursor,
                                                              self.current_player, event.direction))


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
        self.start_block_index = 0

    def build(self):
        for i in range(4):
            self.blocks.append(Block(self.manager))
        self.blocks[2].neighbors[DIRECTION_UP] = self.blocks[0]
        self.blocks[3].neighbors[DIRECTION_UP] = self.blocks[1]
        self.blocks[0].neighbors[DIRECTION_RIGHT] = self.blocks[1]
        self.blocks[2].neighbors[DIRECTION_RIGHT] = self.blocks[3]
        self.blocks[1].neighbors[DIRECTION_LEFT] = self.blocks[0]
        self.blocks[3].neighbors[DIRECTION_LEFT] = self.blocks[2]
        self.blocks[0].neighbors[DIRECTION_DOWN] = self.blocks[2]
        self.blocks[1].neighbors[DIRECTION_DOWN] = self.blocks[3]
        self.state = Board.STATE_BUILT
        self.manager.post(BoardBuiltEvent(self))


class Block:
    """Model of a block."""

    def __init__(self, event_manager):
        self.manager = event_manager
        self.neighbors = list(range(4))
        self.neighbors[DIRECTION_UP] = None
        self.neighbors[DIRECTION_DOWN] = None
        self.neighbors[DIRECTION_LEFT] = None
        self.neighbors[DIRECTION_RIGHT] = None

    def move_possible(self, direction):
        if self.neighbors[direction]:
            return True


class BlockCursor:
    """Model of a cursor for selecting the next block to rotate."""
    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.block = None
        self.state = BlockCursor.STATE_INACTIVE

    def move(self, player, direction):
        if self.state == BlockCursor.STATE_INACTIVE:
            return
        if self.block.move_possible(direction):
            destination = self.block.neighbors[direction]
            self.block = destination
            self.manager.post(MoveBlockCursorEvent(self, player, direction))

    def place(self, block):
        self.block = block
        self.state = BlockCursor.STATE_ACTIVE
        self.manager.post(PlaceBlockCursorEvent(self))

    def notify(self, event):
        if isinstance(event, GameRotateUIEvent):
            board = event.game.board
            self.place(board.blocks[board.start_block_index])
        elif isinstance(event, MoveBlockCursorRequestEvent):
            self.move(event.player, event.direction)


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
