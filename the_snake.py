from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
INFO_PANEL_WIDTH = 200  # Ширина информационной панели
GAME_WIDTH = SCREEN_WIDTH - INFO_PANEL_WIDTH  # Ширина игрового поля
GRID_WIDTH = GAME_WIDTH // GRID_SIZE  # Количество ячеек по горизонтали
FIELD_BORDER_COLOR = (255, 0, 0)
FIELD_CENTER = GRID_WIDTH // 2, GRID_HEIGHT // 2

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона:
BOARD_BACKGROUND_COLOR = (0, 0, 99)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)
SEP_COLOR = (100, 100, 100)
PANEL_COLOR = (40, 40, 40)
FONT_COLOR = (255, 255, 255)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Base class for all game objects.

    Attributes:
        position (tuple): The (x, y) position of the object on the grid.
        body_color (tuple): The color of the object.
    """

    def __init__(self, body_color=None, position=FIELD_CENTER):
        """
        Initialize the base game object.

        Args:
            body_color (tuple, optional): RGB color for the object.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """
        Abstract method for drawing the object.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError('В дочернем классе не реализован метод draw')


class Apple(GameObject):
    """
    Represents an apple object in the game.

    Inherits from GameObject.
    """

    def randomize_position(self, occupied_positions=None):
        """
        Randomly creates the apple position on the game board,
        avoiding occupied cells.
        """
        occupied_positions = occupied_positions or []

        while True:
            self.position = (randint(0, GRID_WIDTH - 1),
                             randint(0, GRID_HEIGHT - 1))
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Draw the apple on the screen."""
        rect = pg.Rect(
            (self.position[0] * GRID_SIZE,
             self.position[1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def __init__(self, occupied_positions, body_color=APPLE_COLOR,
                 position=None):
        """
        Initialize the apple with a random position and color.
        Apple color is set to red with APPLE_COLOR constant.
        """
        super().__init__(body_color, position)
        if position is None:
            self.randomize_position(occupied_positions)


class Snake(GameObject):
    """
    Represents the snake object in the game.

    Inherits from GameObject.
    """

    def __init__(self, body_color=SNAKE_COLOR, position=FIELD_CENTER):
        """
        Initialize the snake with a starting position and color.
        Args:
            body_color (tuple): RGB color for the snake (default: SNAKE_COLOR).
            position (tuple): Initial position (x, y) (default: FIELD_CENTER).
        """
        super().__init__(body_color=body_color, position=position)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None  # Last segment position for erasing

    def draw(self):
        """Draw the snake on the screen."""
        for position in self.positions:
            rect = pg.Rect(
                (position[0] * GRID_SIZE, position[1] * GRID_SIZE),
                (GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pg.Rect(
            (self.positions[0][0] * GRID_SIZE,
             self.positions[0][1] * GRID_SIZE),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """
        Update the snake's direction based on the next direction.

        If a new direction is set, it updates the current direction.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """
        Get the current position of the snake's head.

        Returns:
            tuple: The (x, y) position of the snake's head.
        """
        return self.positions[0]

    def move(self):
        """
        Move the snake in the current direction.

        Updates the position of the snake and manages its length.
        """
        self.update_direction()
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x) % GRID_WIDTH
        new_y = (head_y + dir_y) % GRID_HEIGHT

        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """
        Reset the snake to its initial state.

        Clears the positions and resets the length and direction.
        """
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


class GameInfo:
    """Класс для отображения игровой информации в правой панели"""

    def __init__(self):
        self.font = pg.font.Font(None, 30)
        self.panel_rect = pg.Rect(
            GAME_WIDTH, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT)
        self.panel_color = PANEL_COLOR  # Темно-серый цвет панели
        self.score = 0

    def draw(self, snake_length, score):
        """Отрисовка информационной панели"""
        # Рисуем фон панели
        pg.draw.rect(screen, self.panel_color, self.panel_rect)
        separator = pg.Rect(GAME_WIDTH - 1, 0, 2, SCREEN_HEIGHT)
        pg.draw.rect(screen, SEP_COLOR, separator)

        # Отступы для текста
        x_pos = GAME_WIDTH + 20
        y_pos = 20
        line_height = 40

        # Заголовок
        title = self.font.render('Статистика', True, FONT_COLOR)
        screen.blit(title, (x_pos, y_pos))
        y_pos += line_height

        # Длина змейки
        length_text = self.font.render(
            f'Длина: {snake_length}', True, FONT_COLOR)
        screen.blit(length_text, (x_pos, y_pos))
        y_pos += line_height

        # Очки
        score_text = self.font.render(f'Очки: {score}', True, FONT_COLOR)
        screen.blit(score_text, (x_pos, y_pos))
        y_pos += line_height

    def reset(self):
        """Reset the game info to initial state."""
        self.score = 0


# Функция обработки действий пользователя


def handle_keys(game_object):
    """Process user input for controlling the game object."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def pause_game():
    """
    Pause the game until the user presses a key.

    Displays a pause message and waits for user input.
    """
    font = pg.font.Font(None, 36)
    text = font.render(
        'Game Over. Press any key to continue...', True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN or event.type == pg.QUIT:
                waiting = False


def main():
    """
    Main game loop.

    Handles initialization, event processing, drawing, a
    nd game updates.
    """
    # Инициализация PyGame:
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    game_info = GameInfo()

    while True:
        # Обработка событий
        handle_keys(snake)
        # Движение змейки
        snake.move()
        # Проверка столкновения с яблоком
        if snake.get_head_position() == apple.position:
            snake.length += 1
            game_info.score += 10
            apple.randomize_position(snake.positions)

        # Проверка столкновения с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            game_info.reset()
            pause_game()

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)  # Заливаем всё поле фоном
        game_info.draw(snake.length, game_info.score)
        # Отрисовка границ игрового поля
        game_field_rect = pg.Rect(
            0,  # X-координата начала
            0,  # Y-координата начала
            GAME_WIDTH,  # Ширина
            SCREEN_HEIGHT  # Высота
        )
        pg.draw.rect(screen, FIELD_BORDER_COLOR, game_field_rect, 2)
        snake.draw()
        apple.draw()
        pg.display.update()

        # Контроль скорости
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
