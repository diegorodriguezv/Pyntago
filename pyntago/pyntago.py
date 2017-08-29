#! /usr/bin/env python
"""Pyntago: A pentago board in python."""
import math
import os
from collections import namedtuple

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
COLOR_GREEN = (0, 255, 0)


class Event:
    """Superclass for any event."""

    def __init__(self):
        self.name = "Generic event"


class CycleEvent(Event):
    def __init__(self):
        self.name = "CPU cycle event"


# Board events
class BoardBuiltEvent(Event):
    def __init__(self, game):
        self.name = "Board built event"
        self.game = game


# Input events
class RequestQuitEvent(Event):
    def __init__(self):
        self.name = "Program quit request event"


class RequestMoveEvent(Event):
    def __init__(self, direction):
        self.name = "Move request event"
        self.direction = direction


class RequestSelectEvent(Event):
    def __init__(self):
        self.name = "Select request event"


# Block cursor keyboard events
class RequestBlockCursorMoveEvent(Event):
    def __init__(self, direction):
        self.name = "Move block cursor request event"
        self.direction = direction


class RequestBlockCursorSelectEvent(Event):
    def __init__(self):
        self.name = "Select block cursor request event"


# Block cursor events
class BlockCursorMoveEvent(Event):
    def __init__(self, block_cursor):
        self.name = "Move block cursor event"
        self.block_cursor = block_cursor


class BlockCursorSelectEvent(Event):
    def __init__(self, block_cursor):
        self.name = "Select block cursor event"
        self.block_cursor = block_cursor


class BlockCursorPlaceEvent(Event):
    def __init__(self, block_cursor):
        self.name = "Place block cursor event"
        self.block_cursor = block_cursor


class BlockCursorHideEvent(Event):
    def __init__(self, block_cursor):
        self.name = "Hide block cursor event"
        self.block_cursor = block_cursor


# Position cursor keyboard events
class RequestPositionCursorMoveEvent(Event):
    def __init__(self, direction):
        self.name = "Move position cursor request event"
        self.direction = direction


class RequestPositionCursorSelectEvent(Event):
    def __init__(self):
        self.name = "Select position cursor request event"


# Position cursor events
class PositionCursorMoveEvent(Event):
    def __init__(self, position_cursor):
        self.name = "Move position cursor event"
        self.position_cursor = position_cursor


class SelectPositionCursorEvent(Event):
    def __init__(self, position_cursor):
        self.name = "Select position cursor event"
        self.position_cursor = position_cursor


class PositionCursorPlaceEvent(Event):
    def __init__(self, position_cursor):
        self.name = "Place position cursor event"
        self.position_cursor = position_cursor


class PositionCursorHideEvent(Event):
    def __init__(self, position_cursor):
        self.name = "Hide position cursor event"
        self.position_cursor = position_cursor


# Direction cursor keyboard events
class RequestDirectionCursorMoveEvent(Event):
    def __init__(self, direction):
        self.name = "Move direction cursor request event"
        self.direction = direction


class RequestDirectionCursorSelectEvent(Event):
    def __init__(self):
        self.name = "Select direction cursor request event"


# Direction cursor events
class DirectionCursorMoveEvent(Event):
    def __init__(self, direction_cursor):
        self.name = "Move direction cursor event"
        self.direction_cursor = direction_cursor


class DirectionCursorSelectEvent(Event):
    def __init__(self, direction_cursor):
        self.name = "Select direction cursor event"
        self.direction_cursor = direction_cursor


class DirectionCursorPlaceEvent(Event):
    def __init__(self, direction_cursor):
        self.name = "Place direction cursor event"
        self.direction_cursor = direction_cursor


class DirectionCursorHideEvent(Event):
    def __init__(self, direction_cursor):
        self.name = "Hide direction cursor event"
        self.direction_cursor = direction_cursor


# Game events
class GameMoveUIEvent(Event):
    def __init__(self, game):
        self.name = "Start move UI event"
        self.game = game


class GameBlockSelectionUIEvent(Event):
    def __init__(self, game):
        self.name = "Start block selection UI event"
        self.game = game


class GameBlockRotationUIEvent(Event):
    def __init__(self, game):
        self.name = "Start block rotation UI event"
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
                    new_event = RequestQuitEvent()
                elif input_event.type == KEYDOWN:
                    if input_event.key == K_ESCAPE:
                        new_event = RequestQuitEvent()
                    elif input_event.key == K_UP or input_event.key == K_w:
                        new_event = RequestMoveEvent(DIRECTION_UP)
                    elif input_event.key == K_DOWN or input_event.key == K_s:
                        new_event = RequestMoveEvent(DIRECTION_DOWN)
                    elif input_event.key == K_LEFT or input_event.key == K_a:
                        new_event = RequestMoveEvent(DIRECTION_LEFT)
                    elif input_event.key == K_RIGHT or input_event.key == K_d:
                        new_event = RequestMoveEvent(DIRECTION_RIGHT)
                    elif input_event.key == K_RETURN:
                        new_event = RequestSelectEvent()
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
        # todo: should be quit event when/if there is a confirmation dialog
        if isinstance(event, RequestQuitEvent):
            # stop the loop
            self.alive = False


class BlockCursorSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((300, 300))
        self.image = self.image.convert_alpha()
        self.image.fill(COLOR_TRANSPARENT)
        self.color = COLOR_GREEN
        self.last_color = self.color
        pygame.draw.rect(self.image, self.color, (10, 10, 280, 280), 3)
        self.rect = self.image.get_rect()
        self.move_to = None

    def update(self):
        if self.move_to:
            self.rect.center = self.move_to
            self.move_to = None
        if self.last_color != self.color:
            pygame.draw.rect(self.image, self.color, (10, 10, 280, 280), 3)
            self.last_color = self.color


class PositionCursorSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((100, 100))
        self.image = self.image.convert_alpha()
        self.image.fill(COLOR_TRANSPARENT)
        self.color = COLOR_GREEN
        self.last_color = self.color
        pygame.draw.rect(self.image, self.color, (10, 10, 80, 80), 3)
        self.rect = self.image.get_rect()
        self.move_to = None

    def update(self):
        if self.move_to:
            self.rect.topleft = self.move_to
            self.move_to = None
        if self.last_color != self.color:
            pygame.draw.rect(self.image, self.color, (10, 10, 80, 80), 3)
            self.last_color = self.color


class DirectionCursorSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((300, 300))
        self.image = self.image.convert_alpha()
        self.image.fill(COLOR_TRANSPARENT)
        self.color = COLOR_GREEN
        self.last_color = self.color
        self.direction = None
        self.last_direction = None
        self.rect = self.image.get_rect()

    def update(self):
        if self.last_color != self.color or self.direction != self.last_direction:
            self.draw()
            self.last_color = self.color
            self.last_direction = self.direction

    def draw(self):
        self.image.fill(COLOR_TRANSPARENT)
        x_offset = 100 * math.sin(degrees_to_radians(20))
        y_offset = 100 * math.cos(degrees_to_radians(20))
        if self.direction == DIRECTION_LEFT or self.direction is None:
            pygame.draw.arc(self.image, self.color, (50, 50, 200, 200), degrees_to_radians(110),
                            degrees_to_radians(250), 3)
            arrow_start_pos = (150 - x_offset, 150 + y_offset)
            arrow_left_end_pos = (arrow_start_pos[0] - 20, arrow_start_pos[1] + 5)
            arrow_top_end_pos = (arrow_start_pos[0] - 5, arrow_start_pos[1] - 20)
            pygame.draw.line(self.image, self.color, arrow_start_pos, arrow_left_end_pos, 3)
            pygame.draw.line(self.image, self.color, arrow_start_pos, arrow_top_end_pos, 3)
        if self.direction == DIRECTION_RIGHT or self.direction is None:
            pygame.draw.arc(self.image, self.color, (50, 50, 200, 200), degrees_to_radians(290),
                            degrees_to_radians(70), 3)
            arrow_start_pos = (150 + x_offset, 150 + y_offset)
            arrow_right_end_pos = (arrow_start_pos[0] + 20, arrow_start_pos[1] + 5)
            arrow_top_end_pos = (arrow_start_pos[0] + 5, arrow_start_pos[1] - 20)
            pygame.draw.line(self.image, self.color, arrow_start_pos, arrow_right_end_pos, 3)
            pygame.draw.line(self.image, self.color, arrow_start_pos, arrow_top_end_pos, 3)


def degrees_to_radians(deg):
    return deg / 180.0 * math.pi


class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block, group=None):
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
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
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.marble = marble
        self.image = pygame.Surface((100, 100))
        self.image.fill(marble.color)


class MessageSprite(pygame.sprite.Sprite):
    def __init__(self, rect, font_color, font_size, font_name, group=None):
        if group is not None:
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(rect)
        self.font_color = font_color
        self.font_size = font_size
        self.font_name = font_name
        self.text = None
        self.last_text = None
        self.image = pygame.Surface((self.rect.width, self.rect.height)).convert_alpha()
        self.image.fill(COLOR_TRANSPARENT)

    def update(self):
        if self.last_text != self.text:
            self.image.fill(COLOR_TRANSPARENT)
            font = pygame.font.SysFont(self.font_name, self.font_size)
            text_surf = font.render(self.text, 1, self.font_color)
            text_width = text_surf.get_width()
            text_height = text_surf.get_height()
            self.image.blit(text_surf, (self.rect.width / 2 - text_width / 2,
                                        self.rect.height / 2 - text_height / 2))
            self.last_text = self.text


class PygameView:
    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.window = pygame.display.set_mode((850, 900))
        pygame.display.set_caption('Pyntago')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill(COLOR_BLACK)
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()
        self.back_sprites = pygame.sprite.RenderUpdates()
        self.front_sprites = pygame.sprite.RenderUpdates()
        self.message_sprite = MessageSprite((0, 850, 850, 50), COLOR_BLACK, 35, 'Comic Sans MS', self.front_sprites)
        self.block_cursor_sprite = BlockCursorSprite()
        self.direction_cursor_sprite = DirectionCursorSprite()
        self.position_cursor_sprite = PositionCursorSprite()

    def show_board(self, game):
        self.background.fill(COLOR_WHITE)
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()
        block_position = pygame.Rect((-300 + 124, 124, 300, 300))
        column = 0
        for block in game.blocks:
            if column < 2:
                block_position = block_position.move(301, 0)
            else:
                column = 0
                block_position = block_position.move(-301, 301)
            column += 1
            new_sprite = BlockSprite(block, self.back_sprites)
            new_sprite.rect = block_position

    def show_block_cursor(self, block_cursor):
        self.block_cursor_sprite.color = block_cursor.player.color
        block_sprite = self.get_block_sprite(block_cursor.block)
        self.block_cursor_sprite.rect.center = block_sprite.rect.center
        self.front_sprites.add(self.block_cursor_sprite)

    def move_block_cursor(self, block_cursor):
        self.block_cursor_sprite.color = block_cursor.player.color
        block_sprite = self.get_block_sprite(block_cursor.block)
        self.block_cursor_sprite.move_to = block_sprite.rect.center

    def hide_block_cursor(self):
        self.block_cursor_sprite.kill()

    def show_direction_cursor(self, direction_cursor):
        self.direction_cursor_sprite.color = direction_cursor.player.color
        block_cursor_sprite = self.block_cursor_sprite
        self.direction_cursor_sprite.rect.center = block_cursor_sprite.rect.center
        self.direction_cursor_sprite.direction = direction_cursor.direction
        self.front_sprites.add(self.direction_cursor_sprite)

    def move_direction_cursor(self, direction_cursor):
        self.direction_cursor_sprite.color = direction_cursor.player.color
        self.direction_cursor_sprite.direction = direction_cursor.direction

    def hide_direction_cursor(self):
        self.direction_cursor_sprite.kill()

    def update_position_cursor_sprite(self, position_cursor):
        block = get_block(position_cursor.position)
        block_position = get_pos_in_block(position_cursor.position, block)
        block_sprite = self.get_block_sprite(block)
        (x, y) = block_sprite.rect.topleft
        self.position_cursor_sprite.move_to = (x + 100 * block_position.x,
                                               y + 100 * block_position.y)

    def show_position_cursor(self, position_cursor):
        self.position_cursor_sprite.color = position_cursor.player.color
        self.update_position_cursor_sprite(position_cursor)
        self.front_sprites.add(self.position_cursor_sprite)

    def move_position_cursor(self, position_cursor):
        self.update_position_cursor_sprite(position_cursor)

    # todo: rename position_cursor to board_position_cursor
    # todo: rename position to BoardPosition
    def hide_position_cursor(self):
        self.position_cursor_sprite.kill()

    def show_message(self, game):
        self.message_sprite.text = game.message
        pygame.display.set_caption("Pyntago: " + game.message)

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
            self.show_board(event.game)
        elif isinstance(event, BlockCursorPlaceEvent):
            self.show_block_cursor(event.block_cursor)
        elif isinstance(event, BlockCursorMoveEvent):
            self.move_block_cursor(event.block_cursor)
        elif isinstance(event, BlockCursorHideEvent):
            self.hide_block_cursor()
        elif isinstance(event, DirectionCursorPlaceEvent):
            self.show_direction_cursor(event.direction_cursor)
        elif isinstance(event, DirectionCursorMoveEvent):
            self.move_direction_cursor(event.direction_cursor)
        elif isinstance(event, DirectionCursorHideEvent):
            self.hide_direction_cursor()
        elif isinstance(event, PositionCursorPlaceEvent):
            self.show_position_cursor(event.position_cursor)
        elif isinstance(event, PositionCursorMoveEvent):
            self.move_position_cursor(event.position_cursor)
        elif isinstance(event, PositionCursorHideEvent):
            self.hide_position_cursor()
        elif isinstance(event, MessageUpdateEvent):
            self.show_message(event.game)


Player = namedtuple('Player', 'name color')
Position = namedtuple('Position', 'x y')


class Game:
    """Model of the game."""
    STATE_PREPARING = 'preparing'
    STATE_MOVE = 'awaiting move'
    STATE_SELECT = 'awaiting selection'
    STATE_ROTATE = 'awaiting rotation'

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.state = Game.STATE_PREPARING
        self.players = [Player("White", COLOR_WHITE),
                        Player("Black", COLOR_BLACK)]
        self.current_player = self.players[0]
        self.block_cursor = BlockCursor(event_manager, start_block=0)
        self.position_cursor = PositionCursor(event_manager, start_position=Position(x=2, y=2))
        self.direction_cursor = DirectionCursor(event_manager)
        self.message = None
        self.move_count = 0
        self.marble_positions = {}
        self.blocks = range(4)

    def start(self):
        self.manager.post(BoardBuiltEvent(self))
        self.state = Game.STATE_MOVE
        self.manager.post(GameMoveUIEvent(self))
        self.update_message()

    def move_finished(self):
        self.state = Game.STATE_SELECT
        self.manager.post(GameBlockSelectionUIEvent(self))
        self.update_message()

    def selection_finished(self):
        self.state = Game.STATE_ROTATE
        self.manager.post(GameBlockRotationUIEvent(self))
        self.update_message()

    def rotation_finished(self):
        self.state = Game.STATE_MOVE
        # todo: check for winner
        # change current player
        self.current_player = [p for p in self.players if p != self.current_player][0]
        self.move_count += 1
        self.manager.post(GameMoveUIEvent(self))
        self.update_message()

    def update_message(self):
        self.message = "{0}'s turn, {1}".format(self.current_player.name, self.state)
        self.manager.post(MessageUpdateEvent(self))

    def notify(self, event):
        if isinstance(event, CycleEvent):
            if self.state == Game.STATE_PREPARING:
                self.start()
        elif isinstance(event, SelectPositionCursorEvent):
            if self.state == Game.STATE_MOVE:
                self.move_finished()
        elif isinstance(event, BlockCursorSelectEvent):
            if self.state == Game.STATE_SELECT:
                self.selection_finished()
        elif isinstance(event, DirectionCursorSelectEvent):
            if self.state == Game.STATE_ROTATE:
                self.rotation_finished()
        # Convert keyboard events according to current state
        elif isinstance(event, RequestMoveEvent):
            if self.state == Game.STATE_MOVE:
                self.manager.post(RequestPositionCursorMoveEvent(event.direction))
            elif self.state == Game.STATE_SELECT:
                self.manager.post(RequestBlockCursorMoveEvent(event.direction))
            elif self.state == Game.STATE_ROTATE:
                self.manager.post(RequestDirectionCursorMoveEvent(event.direction))
        elif isinstance(event, RequestSelectEvent):
            if self.state == Game.STATE_MOVE:
                self.manager.post(RequestPositionCursorSelectEvent())
            elif self.state == Game.STATE_SELECT:
                self.manager.post(RequestBlockCursorSelectEvent())
            elif self.state == Game.STATE_ROTATE:
                self.manager.post(RequestDirectionCursorSelectEvent())


#
# class Board:
#     """Model of the board."""
#     STATE_PREPARING = 'preparing'
#     STATE_BUILT = 'built'
#
#     def __init__(self, event_manager):
#         self.manager = event_manager
#         self.state = Board.STATE_PREPARING
#         self.positions = []
#         self.start_block_index = 0
#         self.start_position_index = 14
#
#     def build(self):
#         for i in range(6):
#             for j in range(6):
#                 pos = Position(i, j, self.manager)
#                 pos.block = self.blocks[pos.get_block()]
#                 self.positions.append(pos)
#         self.state = Board.STATE_BUILT


def position_neighbor(position, direction):
    if direction == DIRECTION_UP:
        if position.y > 0:
            return Position(position.x, position.y - 1)
    elif direction == DIRECTION_DOWN:
        if position.y < 5:
            return Position(position.x, position.y + 1)
    elif direction == DIRECTION_LEFT:
        if position.x > 0:
            return Position(position.x - 1, position.y)
    elif direction == DIRECTION_RIGHT:
        if position.x < 5:
            return Position(position.x + 1, position.y)
    return None


def get_block(position):
    if position.x < 3 and position.y < 3:
        return 0
    elif position.x >= 3 and position.y < 3:
        return 1
    elif position.x < 3 and position.y >= 3:
        return 2
    elif position.x >= 3 and position.y >= 3:
        return 3


def get_pos_in_block(position, block):
    if block == 0:
        return Position(position.x, position.y)
    elif block == 1:
        return Position(position.x - 3, position.y)
    elif block == 2:
        return Position(position.x, position.y - 3)
    elif block == 3:
        return Position(position.x - 3, position.y - 3)


def get_block_neighbor(block, direction):
    if direction == DIRECTION_UP:
        if block == 2:
            return 0
        if block == 3:
            return 1
    elif direction == DIRECTION_RIGHT:
        if block == 0:
            return 1
        elif block == 2:
            return 3
    elif direction == DIRECTION_LEFT:
        if block == 1:
            return 0
        elif block == 3:
            return 2
    elif direction == DIRECTION_DOWN:
        if block == 0:
            return 2
        elif block == 1:
            return 3
    return None


class BlockCursor:
    """Model of a cursor for selecting the next block to rotate."""
    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, event_manager, start_block):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.start_block = start_block
        self.block = None
        self.player = None
        self.state = BlockCursor.STATE_INACTIVE

    def place(self, player):
        if self.state == BlockCursor.STATE_ACTIVE:
            return
        self.block = self.start_block
        self.player = player
        self.state = BlockCursor.STATE_ACTIVE
        self.manager.post(BlockCursorPlaceEvent(self))

    def hide(self):
        if self.state == BlockCursor.STATE_ACTIVE:
            return
        self.state = BlockCursor.STATE_INACTIVE
        self.manager.post(BlockCursorHideEvent(self))

    def move(self, direction):
        if self.state == BlockCursor.STATE_INACTIVE:
            return
        neighbor = get_block_neighbor(self.block, direction)
        if neighbor is not None:
            self.block = neighbor
            self.manager.post(BlockCursorMoveEvent(self))

    def select(self):
        if self.state == BlockCursor.STATE_INACTIVE:
            return
        self.state = BlockCursor.STATE_INACTIVE
        self.manager.post(BlockCursorSelectEvent(self))

    def notify(self, event):
        # Game UI events
        if isinstance(event, GameBlockSelectionUIEvent):
            self.place(event.game.current_player)
        elif isinstance(event, GameBlockRotationUIEvent):
            self.hide()
        # Action request
        elif isinstance(event, RequestBlockCursorMoveEvent):
            self.move(event.direction)
        elif isinstance(event, RequestBlockCursorSelectEvent):
            self.select()


# todo: bug: position cursor doesn't change color
class PositionCursor:
    """Model of a cursor for selecting the position where a marble is going to be placed."""
    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, event_manager, start_position):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.start_position = start_position
        self.position = None
        self.player = None
        self.state = PositionCursor.STATE_INACTIVE

    def place(self, player):
        if self.state == PositionCursor.STATE_ACTIVE:
            return
        self.player = player
        self.position = self.start_position
        self.state = PositionCursor.STATE_ACTIVE
        self.manager.post(PositionCursorPlaceEvent(self))

    def hide(self):
        if self.state == PositionCursor.STATE_ACTIVE:
            return
        self.state = PositionCursor.STATE_INACTIVE
        self.manager.post(PositionCursorHideEvent(self))

    def move(self, direction):
        if self.state == PositionCursor.STATE_INACTIVE:
            return
        new_pos = position_neighbor(self.position, direction)
        if new_pos is not None:
            self.position = new_pos
            self.manager.post(PositionCursorMoveEvent(self))

    def select(self):
        if self.state == PositionCursor.STATE_INACTIVE:
            return
        self.state = PositionCursor.STATE_INACTIVE
        self.manager.post(SelectPositionCursorEvent(self))

    def notify(self, event):
        # Game UI events
        if isinstance(event, GameMoveUIEvent):
            self.place(event.game.current_player)
        elif isinstance(event, GameBlockSelectionUIEvent):
            self.hide()
        # Action request
        elif isinstance(event, RequestPositionCursorMoveEvent):
            self.move(event.direction)
        elif isinstance(event, RequestPositionCursorSelectEvent):
            self.select()


# todo: rename direction to rotation direction
class DirectionCursor:
    """Model of a cursor for selecting the direction for rotating a block."""
    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, event_manager):
        self.manager = event_manager
        self.manager.register_listener(self)
        self.direction = None
        self.player = None
        self.state = DirectionCursor.STATE_INACTIVE

    def place(self, player):
        if self.state == DirectionCursor.STATE_ACTIVE:
            return
        self.player = player
        self.state = DirectionCursor.STATE_ACTIVE
        self.direction = None
        self.manager.post(DirectionCursorPlaceEvent(self))

    def hide(self):
        if self.state == DirectionCursor.STATE_ACTIVE:
            return
        self.state = DirectionCursor.STATE_INACTIVE
        self.manager.post(DirectionCursorHideEvent(self))

    def move(self, direction):
        if self.state == DirectionCursor.STATE_INACTIVE:
            return
        if direction in (DIRECTION_RIGHT, DIRECTION_LEFT):
            self.direction = direction
        self.manager.post(DirectionCursorMoveEvent(self))

    def select(self):
        if self.state == DirectionCursor.STATE_INACTIVE:
            return
        if self.direction not in (DIRECTION_LEFT, DIRECTION_RIGHT):
            return
        self.state = DirectionCursor.STATE_INACTIVE
        self.manager.post(DirectionCursorSelectEvent(self))

    def notify(self, event):
        # Game UI events
        if isinstance(event, GameBlockRotationUIEvent):
            self.place(event.game.current_player)
        elif isinstance(event, GameMoveUIEvent):
            self.hide()
        # Action request
        elif isinstance(event, RequestDirectionCursorMoveEvent):
            self.move(event.direction)
        elif isinstance(event, RequestDirectionCursorSelectEvent):
            self.select()


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
