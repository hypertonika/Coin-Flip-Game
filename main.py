import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройка экрана
WIDTH, HEIGHT = 1280, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Flip Game")

# Цвета
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (63, 86, 186)
# Шрифты
font = pygame.font.SysFont(None, 40)


# Загрузка музыки
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.set_volume(1)  # Установка начальной громкости
pygame.mixer.music.play(-1)  # Начать воспроизведение музыки немедленно
music_paused = False
music_position = 0
plus_one_sound = pygame.mixer.Sound('answer.mp3')
finish_sound = pygame.mixer.Sound('finish.mp3')


# Монета
coin_images = [pygame.image.load('heads1.png'), pygame.image.load('tails1.png')]
coin_rect = coin_images[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
background_image = pygame.image.load('background3.png').convert()
# Переменные анимации
animation_frames = 10
current_frame = 0
flipping = False

# Игровые переменные
score = 0
previous_result = None
guess = None
time_remaining = 0
menu_exit_time = 0  # Переменная для хранения времени при выходе в меню
difficulty = 0
difficulty_time = {0: 90, 1: 60, 2: 30}

# Функция для сохранения счета и сложности в файл
def save_score(score, difficulty, player_name):
    difficulty_map = {0: "Easy", 1: "Medium", 2: "Hard"}
    difficulty_name = difficulty_map.get(difficulty, "Unknown")
    with open('score.txt', 'a') as file:
        file.write(f"Player: {player_name}, Score: {score}, Difficulty: {difficulty_name}\n")

# Класс кнопки
class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        x, y = pos
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

# Функция для броска монетыS
def flip_coin():
    return random.choice(["heads", "tails"])

# Функция для отображения меню
def display_menu(buttons, music_on, selected_button_index):
    screen.fill(WHITE)
    menu_title = font.render("Coin Flip Game", True, BLACK)
    title_width, title_height = font.size("Coin Flip Game")
    screen.blit(menu_title, ((WIDTH - title_width) // 2, 50))

    # Отображение логотипа
    logo = pygame.image.load('logo1.png')
    logo_rect = logo.get_rect(center=(WIDTH // 2, 100))
    screen.blit(background_image, (0,0))
    screen.blit(logo, logo_rect)

    for i, button in enumerate(buttons):
        button.draw(screen)
        if i == selected_button_index:
            pygame.draw.rect(screen, RED, (button.x - 5, button.y - 5, button.width + 10, button.height + 10), 3)

    # Опция музыки
    music_text = font.render("Music: ON" if music_on else "Music: OFF", True, WHITE)
    screen.blit(music_text, (20, HEIGHT - 50))

    pygame.display.flip()

# Функция для отображения таблицы лидеров
def display_leaderboard():
    screen.fill(WHITE)
    leaderboard_title = font.render("Leaderboard", True, WHITE)
    screen.blit(leaderboard_title, ((WIDTH - leaderboard_title.get_width()) // 2, 50))
    screen.blit(background_image, (0, 0))
    # Загрузка данных из файла score.txt
    leaderboard_data = []
    try:
        with open('score.txt', 'r') as file:
            leaderboard_data = file.readlines()
    except FileNotFoundError:
        # Если файл не найден, выводим сообщение о отсутствии данных
        no_data_text = font.render("No leaders found, be the first!", True, WHITE)
        screen.blit(no_data_text, ((WIDTH - no_data_text.get_width()) // 2, 150))
        pygame.display.flip()
        return

    # Если файл найден, продолжаем обработку данных и отображение таблицы лидеров
    if not leaderboard_data:
        # Если список данных пуст, выводим сообщение о отсутствии лидеров
        no_data_text = font.render("No leaders found, be the first!", True, WHITE)
        screen.blit(no_data_text, ((WIDTH - no_data_text.get_width()) // 2, 150))
    else:
        # Если есть данные, продолжаем обработку и отображение таблицы лидеров
        # Создание словаря для отслеживания количества записей для каждой сложности
        difficulty_displayed = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}

        # Сортировка данных сначала по сложности, затем по очкам
        sorted_leaderboard_data = []
        for line in leaderboard_data:
            if "Difficulty: " in line and "Score: " in line:
                sorted_leaderboard_data.append(line)

        sorted_leaderboard_data.sort(key=lambda x: (difficulty_order[x.split("Difficulty: ")[1].split(",")[0].strip()],
                                                    -int(x.split("Score: ")[1].split(",")[0].strip())
                                                    if "Score: " in x else 0), reverse=False)

        # Отображение данных таблицы лидеров
        y_offset = 150
        for entry in sorted_leaderboard_data:
            if y_offset > HEIGHT - 50:
                break  # Если достигнут предел экрана, выходим из цикла
            if "Score: " in entry and "Difficulty: " in entry:  # Проверяем наличие ключевых фраз в записи
                difficulty = entry.split("Difficulty: ")[1].split(",")[0].strip()
                if difficulty_displayed[difficulty] < 5:  # Отображаем только первые 5 записей для каждой сложности
                    if difficulty_displayed[difficulty] == 0:
                        difficulty_text = font.render(f"Difficulty: {difficulty}", True, WHITE)
                        screen.blit(difficulty_text, (50, y_offset))
                        y_offset += 40  # Увеличиваем отступ перед каждой новой сложностью
                    entry_data = entry.split(",")  # Разделяем запись по запятой
                    name_score_text = f"{entry_data[0]}, {entry_data[1]}"  # Берем первые две части записи (имя и счет)
                    entry_text = font.render(name_score_text.strip(), True, WHITE)  # Отображаем только имя и счет
                    screen.blit(entry_text, (300, y_offset))  # Сдвигаем отображение вправо для лучшей читаемости
                    y_offset += 40
                    difficulty_displayed[difficulty] += 1

    pygame.display.flip()


# Функция для отображения игры
def display_game():
    global flipping, current_frame, score, previous_result, guess, coin_rect, time_remaining

    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))
    # Отображение монеты
    if flipping:
        current_frame += 1
        if current_frame >= animation_frames:
            flipping = False
        else:
            angle = 180 * current_frame / animation_frames
            rotated_image = pygame.transform.rotate(coin_images[0], angle)
            coin_rect = rotated_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(rotated_image, coin_rect)
    else:
        if previous_result:
            if previous_result == "heads":
                screen.blit(coin_images[0], coin_rect)
            else:
                screen.blit(coin_images[1], coin_rect)

    # Отображение счета
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    # Отображение "+1" анимации
    if show_plus_one_animation:
        plus_one_text = font.render("+1", True, GREEN)
        screen.blit(plus_one_text, (20 + score_text.get_width() + 10, 20))

    # Отображение оставшегося времени
    time_text = font.render(f"Time Remaining: {max(time_remaining, 0):.2f} s", True, WHITE)
    screen.blit(time_text, (WIDTH - 350, 20))

    # Отображение предыдущего результата броска
    if previous_result:
        result_text = font.render(f"Result: {previous_result.capitalize()}", True, WHITE)
        screen.blit(result_text, (20, 60))

    # Отображение ставки игрока
    if guess:
        guess_text = font.render(f"Your Guess: {guess.capitalize()}", True, WHITE)
        screen.blit(guess_text, (20, 100))

    # Отображение инструкций
    instructions_text = font.render("Press SPACE to flip the coin.", True, WHITE)
    screen.blit(instructions_text, (20, HEIGHT - 40))
    instructions_text = font.render("Press H to guess Heads. Press T to guess Tails.", True, WHITE)
    screen.blit(instructions_text, (20, HEIGHT - 80))

    pygame.display.flip()

# Добавление функции для отображения экрана ввода имени игрока
def display_name_input():
    screen.fill(WHITE)
    prompt_text = font.render("Enter Player Name:", True, WHITE)
    screen.blit(prompt_text, ((WIDTH - prompt_text.get_width()) // 2, 250))

    input_rect = pygame.Rect((WIDTH - 400) // 2, 300, 400, 50)
    color_inactive = WHITE
    color_active = GREEN
    color = color_inactive
    active = False
    name = ''
    while True:
        screen.fill(WHITE) # Очищаем экран перед перерисовкой
        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, color, input_rect, 2)  # Рисуем рамку поля ввода
        screen.blit(prompt_text, ((WIDTH - prompt_text.get_width()) // 2, 250))  # Отображаем текст инструкции

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return name
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

        screen.blit(font.render(name, True, WHITE), (input_rect.x + 5, input_rect.y + 5))  # Выводим имя
        pygame.display.flip()  # Обновляем экран

    return name

# Основной цикл
running = True
show_menu = True
music_on = True
difficulty_selected = False
guess_selected = False  # переменная для отслеживания выбора ставки

clock = pygame.time.Clock()

menu_buttons = [
    Button("Start Game", 500, 250, 300, 50, action="start"),
    Button("Toggle Music", 500, 350, 300, 50, action="music_toggle"),
    Button("Leaderboard", 500, 450, 300, 50, action="leaderboard"),
    Button("Quit", 500, 550, 300, 50, action="quit")
]

difficulty_buttons = []
selected_button_index = 0  # Индекс выбранной кнопки в меню

# Variables for +1 animation
show_plus_one_animation = False
plus_one_animation_timer = 0

while running:
    dt = clock.tick(30) / 1000.0


    if show_menu:
        display_menu(menu_buttons, music_on, selected_button_index)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(menu_buttons):
                        if button.is_clicked(pygame.mouse.get_pos()):
                            selected_button_index = i
                            if button.action == "start":
                                show_menu = False
                                # Получаем имя игрока перед отображением меню выбора сложности
                                player_name = display_name_input()
                                difficulty_buttons = [
                                    Button("Easy (90s)", 500, 250, 300, 50, action=0),
                                    Button("Medium (60s)", 500, 350, 300, 50, action=1),
                                    Button("Hard (30s)", 500, 450, 300, 50, action=2)
                                ]
                                display_menu(difficulty_buttons, music_on, 0)
                                break
                            elif button.action == "quit":
                                running = False
                            elif button.action == "music_toggle":
                                music_on = not music_on
                                if music_on:
                                    pygame.mixer.music.unpause()
                                else:
                                    pygame.mixer.music.pause()
                                display_menu(menu_buttons, music_on, selected_button_index)
                            elif button.action == "leaderboard":
                                display_leaderboard()  # Отображаем таблицу лидеров
                                pygame.time.delay(3000)  # Задержка перед возвратом в меню
                                show_menu = True
                                display_menu(menu_buttons, music_on, selected_button_index)  # Отображаем меню после таблицы лидеров
                                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Перемещение вверх по меню
                    selected_button_index = (selected_button_index - 1) % len(menu_buttons)
                elif event.key == pygame.K_DOWN:  # Перемещение вниз по меню
                    selected_button_index = (selected_button_index + 1) % len(menu_buttons)
                elif event.key == pygame.K_RETURN:  # Выбор кнопки по нажатию Enter
                    button = menu_buttons[selected_button_index]
                    if button.action == "start":
                        show_menu = False
                        # Получаем имя игрока перед отображением меню выбора сложности
                        player_name = display_name_input()
                        difficulty_buttons = [
                            Button("Easy (90s)", 500, 250, 300, 50, action=0),
                            Button("Medium (60s)", 500, 350, 300, 50, action=1),
                            Button("Hard (30s)", 500, 450, 300, 50, action=2)
                        ]
                        display_menu(difficulty_buttons, music_on, 0)
                    elif button.action == "quit":
                        running = False
                    elif button.action == "music_toggle":
                        music_on = not music_on
                        if music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                        display_menu(menu_buttons, music_on, selected_button_index)
                    elif button.action == "leaderboard":
                        display_leaderboard()  # Отображаем таблицу лидеров
                        pygame.time.delay(3000)  # Задержка перед возвратом в меню
                        show_menu = True
                        display_menu(menu_buttons, music_on, selected_button_index)  # Отображаем меню после таблицы лидеров
    else:
        if not difficulty_selected:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, button in enumerate(difficulty_buttons):
                            if button.is_clicked(pygame.mouse.get_pos()):
                                difficulty = button.action
                                time_remaining = difficulty_time[difficulty]
                                difficulty_selected = True
                                selected_button_index = i
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        show_menu = True
                        difficulty_selected = False
                        time_remaining = 0
                        guess_selected = False
                    elif event.key == pygame.K_UP:  # Перемещение вверх по меню
                        selected_button_index = (selected_button_index - 1) % len(difficulty_buttons)
                    elif event.key == pygame.K_DOWN:  # Перемещение вниз по меню
                        selected_button_index = (selected_button_index + 1) % len(difficulty_buttons)
                    elif event.key == pygame.K_RETURN:  # Выбор кнопки по нажатию Enter
                        button = difficulty_buttons[selected_button_index]
                        difficulty = button.action
                        time_remaining = difficulty_time[difficulty]
                        difficulty_selected = True
            display_menu(difficulty_buttons, music_on, selected_button_index)
            continue

        # Логика игры при выборе сложности
        if time_remaining > 0 or menu_exit_time > 0:
            if menu_exit_time > 0:
                time_remaining = menu_exit_time
                menu_exit_time = 0
            display_game()  # Отображение игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not guess_selected:  # Проверяем, что ставка еще не была сделана
                        if event.key == pygame.K_h:
                            guess = "heads"
                            guess_selected = True
                        elif event.key == pygame.K_t:
                            guess = "tails"
                            guess_selected = True
                    if event.key == pygame.K_SPACE and not flipping and guess_selected:
                        flipping = True
                        current_frame = 0
                        result = flip_coin()
                        previous_result = result
                        guess_selected = False  # Сбрасываем выбор ставки
                        # Сравниваем ставку игрока с результатом
                        if guess == result:
                            score += 1  # Увеличиваем счет, если ставка правильная
                            # Trigger the "+1" animation
                            show_plus_one_animation = True
                            plus_one_sound.play()
                        guess = None  # Сбрасываем переменную ставки
                    elif event.key == pygame.K_q:  # Добавляем обработку нажатия 'q' для выхода в меню
                        # Сохраняем текущее оставшееся время
                        menu_exit_time = time_remaining
                        show_menu = True
                        difficulty_selected = False
                        time_remaining = 0
                        guess_selected = False  # Сбрасываем выбор ставки
        else:
            # Сохраняем счет в файл
            save_score(score, difficulty, player_name)  # Добавляем имя игрока для сохранения
            # Сбрасываем счет
            score = 0
            show_menu = True
            difficulty_selected = False
            time_remaining = 0
            guess_selected = False  # Сбрасываем выбор ставки

        # Уменьшаем оставшееся время
        if time_remaining > 0:
            time_remaining -= dt

        # Handle the "+1" animation
        if show_plus_one_animation:
            plus_one_animation_timer += dt
            if plus_one_animation_timer >= 1.0:  # Display for 1 second
                show_plus_one_animation = False
                plus_one_animation_timer = 0

        if time_remaining <= 0:
            # Время истекло, воспроизводим звук
            finish_sound.play()

        pygame.display.flip()

pygame.quit()
sys.exit()
