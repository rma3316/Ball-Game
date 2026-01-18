import pygame
import sys
import math
import random

# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("벽돌 깨기 게임")

# 색상 정의
DARK_NAVY = (26, 26, 46)  # #1a1a2e
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_RED = (200, 0, 0)

# 로컬 폰트 로드 (font.ttf)
def load_font(size, bold=False):
    try:
        font = pygame.font.Font("font.ttf", size)
        if bold:
            font.set_bold(True)
        return font
    except:
        # font.ttf 파일이 없으면 기본 폰트 사용
        font = pygame.font.Font(None, size)
        if bold:
            font.set_bold(True)
        return font

# 폰트 설정
font = load_font(36)
small_font = load_font(20)
medium_font = load_font(28)
bold_font = load_font(32, bold=True)
large_font = load_font(72)

# FPS 설정
FPS = 60
clock = pygame.time.Clock()

# 패들 설정
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 10

# 공 설정
BALL_RADIUS = 10
BALL_SPEED = 5

# 아이템 타입 정의
ITEM_PLUS_1 = "plus_1"
ITEM_DOUBLE = "double"
ITEM_LASER = "laser"
ITEM_POWER = "power"
ITEM_MAGNET = "magnet"

# 아이템 색상 매핑
ITEM_COLORS = {
    ITEM_PLUS_1: BLUE,
    ITEM_DOUBLE: GREEN,
    ITEM_LASER: YELLOW,
    ITEM_POWER: RED,
    ITEM_MAGNET: PURPLE
}

# 아이템 설정
ITEM_DROP_RATE = 0.3
ITEM_RADIUS = 18
ITEM_BASE_SPEED = 3
MAGNET_RANGE = 300  # 자석 효과 거리 제한

# 레이저 설정
LASER_WIDTH = 3
LASER_HEIGHT = 20
LASER_SPEED = 15
LASER_COLOR = YELLOW

# 블록 설정 (빽빽한 스타일)
BRICK_COLS = 20
BRICK_PADDING = 1
BRICK_WIDTH = (SCREEN_WIDTH - (BRICK_COLS + 1) * BRICK_PADDING) // BRICK_COLS
BRICK_HEIGHT = 20
BRICK_OFFSET_TOP = 80

# 무지개 색상 정의 (20가지로 확장)
RAINBOW_COLORS = [
    (255, 0, 0),      # 빨강
    (255, 64, 0),     # 주황빨강
    (255, 127, 0),    # 주황
    (255, 191, 0),    # 황주황
    (255, 255, 0),    # 노랑
    (191, 255, 0),    # 연두
    (127, 255, 0),    # 초록연두
    (0, 255, 0),      # 초록
    (0, 255, 127),    # 청록
    (0, 255, 191),    # 밝은청록
    (0, 255, 255),    # 하늘색
    (0, 191, 255),    # 밝은파랑
    (0, 127, 255),    # 파랑
    (0, 64, 255),     # 진한파랑
    (0, 0, 255),      # 남색
    (64, 0, 255),     # 남보라
    (127, 0, 255),    # 보라
    (191, 0, 255),    # 자주보라
    (255, 0, 255),    # 자홍
    (255, 0, 127),    # 분홍
]

# 레벨 데이터 (텍스트 기반 맵 에디터)
# '#' = 일반 블록, '@' = 단단한 블록, ' ' = 빈 공간
LEVELS = [
    # 레벨 1: 하트 모양
    [
        "                    ",
        "                    ",
        "  ##    ####    ##  ",
        " ####  ######  #### ",
        "####################",
        "####################",
        " ################## ",
        "  ################  ",
        "   ##############   ",
        "    ############    ",
        "     ##########     ",
        "      ########      ",
        "       ######       ",
        "        ####        ",
        "         ##         ",
    ],
    # 레벨 2: 피라미드 with 단단한 블록
    [
        "                    ",
        "         ##         ",
        "        ####        ",
        "       ######       ",
        "      @@@@@@@@      ",
        "     ##########     ",
        "    ############    ",
        "   ##@@@@@@@@@@##   ",
        "  ################  ",
        " ################## ",
        "####################",
        "@@@@@@@@@@@@@@@@@@@@",
        "####################",
        "####################",
        "####################",
    ],
    # 레벨 3: 체스판 패턴
    [
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "@@@@@@@@@@@@@@@@@@@@",
        " # # # # # # # # # #",
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "# # # # # # # # # # ",
        " # # # # # # # # # #",
        "@@@@@@@@@@@@@@@@@@@@",
    ],
    # 레벨 4: 다이아몬드
    [
        "                    ",
        "         ##         ",
        "        ####        ",
        "       ##@@##       ",
        "      ##@@@@##      ",
        "     ##@@@@@@##     ",
        "    ##@@@@@@@@##    ",
        "   ##@@@@@@@@@@##   ",
        "  ##@@@@@@@@@@@@##  ",
        "   ##@@@@@@@@@@##   ",
        "    ##@@@@@@@@##    ",
        "     ##@@@@@@##     ",
        "      ##@@@@##      ",
        "       ##@@##       ",
        "        ####        ",
    ],
]

class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = LASER_WIDTH
        self.height = LASER_HEIGHT
        self.speed = LASER_SPEED
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def is_off_screen(self):
        return self.y + self.height < 0
    
    def check_brick_collision(self, bricks):
        for brick in bricks[:]:
            if self.rect.colliderect(brick.rect):
                bricks.remove(brick)
                return True
        return False
    
    def draw(self, surface):
        pygame.draw.rect(surface, LASER_COLOR, self.rect)
        pygame.draw.rect(surface, (255, 255, 200), self.rect.inflate(-1, 0))

class Paddle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        
        self.laser_timer = 0
        self.power_timer = 0
        self.magnet_timer = 0
        
        self.laser_cooldown = 0
    
    def update(self, mouse_x):
        self.rect.centerx = mouse_x
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        if self.laser_timer > 0:
            self.laser_timer -= 1
        if self.power_timer > 0:
            self.power_timer -= 1
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
    
    def activate_laser(self):
        self.laser_timer = 600
    
    def activate_power(self):
        self.power_timer = 600
    
    def activate_magnet(self):
        self.magnet_timer = 300
    
    def can_shoot_laser(self):
        return self.laser_timer > 0 and self.laser_cooldown == 0
    
    def shoot_laser(self):
        if self.can_shoot_laser():
            self.laser_cooldown = 20
            left_laser = Laser(self.rect.left + 5, self.rect.top)
            right_laser = Laser(self.rect.right - 5, self.rect.top)
            return [left_laser, right_laser]
        return []
    
    def draw(self, surface):
        color = WHITE
        if self.laser_timer > 0:
            color = YELLOW
        elif self.power_timer > 0:
            color = RED
        elif self.magnet_timer > 0:
            color = PURPLE
        
        pygame.draw.rect(surface, color, self.rect)
        
        # 동적 스택 시스템: 활성화된 버프를 위에서부터 쌓아서 표시
        y_offset = 0
        buff_spacing = 22  # 각 버프 텍스트 사이 간격
        
        # 관통탄 효과
        if self.power_timer > 0:
            seconds = self.power_timer / 60
            timer_text = small_font.render(f"POWER {seconds:.1f}초", True, RED)
            text_rect = timer_text.get_rect(center=(self.rect.centerx, self.rect.top - 20 - y_offset))
            surface.blit(timer_text, text_rect)
            y_offset += buff_spacing
        
        # 자석 효과
        if self.magnet_timer > 0:
            seconds = self.magnet_timer / 60
            timer_text = small_font.render(f"MAGNET {seconds:.1f}초", True, PURPLE)
            text_rect = timer_text.get_rect(center=(self.rect.centerx, self.rect.top - 20 - y_offset))
            surface.blit(timer_text, text_rect)
            y_offset += buff_spacing
        
        # 레이저 효과
        if self.laser_timer > 0:
            seconds = self.laser_timer / 60
            timer_text = small_font.render(f"LASER {seconds:.1f}초", True, YELLOW)
            text_rect = timer_text.get_rect(center=(self.rect.centerx, self.rect.top - 20 - y_offset))
            surface.blit(timer_text, text_rect)
            y_offset += buff_spacing


class Brick:
    def __init__(self, x, y, width, height, color, is_hard=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_hard = is_hard
    
    def draw(self, surface):
        if self.is_hard:
            pygame.draw.rect(surface, GRAY, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 1)
        else:
            pygame.draw.rect(surface, self.color, self.rect)


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.radius = ITEM_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.speed = ITEM_BASE_SPEED
        self.vx = 0
        self.vy = ITEM_BASE_SPEED
        
        self.pulse_offset = random.uniform(0, math.pi * 2)
        self.float_offset = random.uniform(0, math.pi * 2)
        self.frame_count = 0
    
    def update(self, paddle=None):
        self.frame_count += 1
        
        # 개선된 자석 효과 (거리 제한 + 부드러운 가속)
        if paddle and paddle.magnet_timer > 0:
            dx = paddle.rect.centerx - self.x
            dy = paddle.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # 300px 이내일 때만 자석 효과 적용
            if dist <= MAGNET_RANGE and dist > 0:
                # 정규화된 방향 벡터
                dx /= dist
                dy /= dist
                
                # 부드러운 가속 (Lerp 스타일)
                # 거리에 따라 가속도 조절 (멀수록 약하게)
                magnet_strength = (MAGNET_RANGE - dist) / MAGNET_RANGE * 0.5
                
                self.vx += dx * magnet_strength
                self.vy += dy * magnet_strength
                
                # 최대 속도 제한 (부드럽게)
                speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
                max_speed = 8
                if speed > max_speed:
                    self.vx = (self.vx / speed) * max_speed
                    self.vy = (self.vy / speed) * max_speed
        
        # 위치 업데이트
        self.x += self.vx
        self.y += self.vy
        
        # 둥둥 떠다니는 효과
        float_amplitude = 1.5
        self.y += math.sin(self.frame_count * 0.1 + self.float_offset) * 0.25
        
        self.rect.center = (int(self.x), int(self.y))
    
    def is_off_screen(self):
        return self.y - self.radius > SCREEN_HEIGHT
    
    def check_paddle_collision(self, paddle):
        return self.rect.colliderect(paddle.rect)
    
    def draw(self, surface):
        # Pulse 애니메이션
        pulse = math.sin(self.frame_count * 0.15 + self.pulse_offset) * 2
        current_radius = self.radius + pulse
        
        color = ITEM_COLORS[self.item_type]
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(current_radius))
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(current_radius), 2)
        
        if self.item_type == ITEM_PLUS_1:
            ball_text = small_font.render("●+1", True, WHITE)
        elif self.item_type == ITEM_DOUBLE:
            ball_text = small_font.render("●x2", True, WHITE)
        elif self.item_type == ITEM_LASER:
            ball_text = bold_font.render("L", True, WHITE)
        elif self.item_type == ITEM_POWER:
            ball_text = bold_font.render("P", True, WHITE)
        elif self.item_type == ITEM_MAGNET:
            ball_text = bold_font.render("M", True, WHITE)
        
        text_rect = ball_text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(ball_text, text_rect)


class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.vx = 0
        self.vy = -speed
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def normalize_velocity(self):
        """속도 벡터를 정규화하여 일정한 속도 유지"""
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed > 0:
            self.vx = (self.vx / current_speed) * self.speed
            self.vy = (self.vy / current_speed) * self.speed
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def check_wall_collision(self):
        # 왼쪽 벽 충돌
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = -self.vx
            # 랜덤 노이즈 추가
            self.vx += random.uniform(-0.5, 0.5)
        
        # 오른쪽 벽 충돌
        if self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx
            # 랜덤 노이즈 추가
            self.vx += random.uniform(-0.5, 0.5)
        
        # 위쪽 벽 충돌
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = -self.vy
            # 랜덤 노이즈 추가
            self.vx += random.uniform(-0.5, 0.5)
        
        # 속도 정규화 (일정한 속도 유지)
        self.normalize_velocity()
    
    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            if self.vy > 0:  # 공이 아래로 떨어지는 중일 때만
                # Relative Intersect 알고리즘
                # 패들과 공의 중심 차이 계산
                offset = self.x - paddle.rect.centerx
                # 정규화된 offset (-1.0 ~ 1.0)
                normalized_offset = offset / (paddle.width / 2)
                
                # 현재 속도의 크기 저장
                current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
                
                # 각도 계산 (-60도 ~ 60도)
                bounce_angle = normalized_offset * 60
                angle_rad = math.radians(bounce_angle)
                
                # 새로운 속도 벡터 계산
                self.vx = current_speed * math.sin(angle_rad)
                self.vy = -current_speed * math.cos(angle_rad)
                
                # 최소 가로 속도 강제 (무한 루프 방지)
                min_horizontal_speed = 2.0
                if abs(self.vx) < min_horizontal_speed:
                    if self.vx == 0:
                        # 완전히 수직이면 랜덤 방향으로
                        self.vx = random.choice([-min_horizontal_speed, min_horizontal_speed])
                    elif self.vx > 0:
                        self.vx = min_horizontal_speed
                    else:
                        self.vx = -min_horizontal_speed
                    
                    # 가로 속도를 강제했으니 속도 정규화
                    self.normalize_velocity()
                
                # 공이 패들 안에 들어가지 않도록 위치 조정
                self.y = paddle.rect.top - self.radius
                self.rect.center = (self.x, self.y)
    
    def check_brick_collision(self, bricks, items, power_mode=False):
        hit_brick = False
        bricks_to_remove = []
        
        for brick in bricks[:]:
            if self.rect.colliderect(brick.rect):
                ball_center_x = self.rect.centerx
                ball_center_y = self.rect.centery
                brick_center_x = brick.rect.centerx
                brick_center_y = brick.rect.centery
                
                dx = ball_center_x - brick_center_x
                dy = ball_center_y - brick_center_y
                
                if random.random() < ITEM_DROP_RATE:
                    item_type = self.get_random_item_type()
                    item = Item(brick_center_x, brick_center_y, item_type)
                    items.append(item)
                
                should_remove = True
                should_bounce = True
                
                if power_mode:
                    if brick.is_hard:
                        should_bounce = True
                        should_remove = True
                    else:
                        should_bounce = False
                        should_remove = True
                else:
                    if brick.is_hard:
                        should_bounce = True
                        should_remove = False
                    else:
                        should_bounce = True
                        should_remove = True
                
                if should_remove:
                    bricks_to_remove.append(brick)
                
                hit_brick = True
                
                if should_bounce:
                    if abs(dx) > abs(dy):
                        self.vx = -self.vx
                        # 랜덤 노이즈 추가
                        self.vx += random.uniform(-0.5, 0.5)
                    else:
                        self.vy = -self.vy
                        # 랜덤 노이즈 추가
                        self.vx += random.uniform(-0.5, 0.5)
                    
                    # 위치 조정
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            self.x = brick.rect.right + self.radius
                        else:
                            self.x = brick.rect.left - self.radius
                    else:
                        if dy > 0:
                            self.y = brick.rect.bottom + self.radius
                        else:
                            self.y = brick.rect.top - self.radius
                    
                    self.rect.center = (self.x, self.y)
                    
                    # 속도 정규화
                    self.normalize_velocity()
                    
                    if not power_mode or brick.is_hard:
                        break
        
        for brick in bricks_to_remove:
            if brick in bricks:
                bricks.remove(brick)
        
        return hit_brick
    
    def get_random_item_type(self):
        rand = random.random()
        if rand < 0.6:
            return ITEM_PLUS_1
        elif rand < 0.7:
            return ITEM_DOUBLE
        elif rand < 0.8:
            return ITEM_LASER
        elif rand < 0.9:
            return ITEM_POWER
        else:
            return ITEM_MAGNET
    
    def clone(self):
        angle = random.uniform(-45, 45)
        angle_rad = math.radians(angle)
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        
        new_ball = Ball(self.x, self.y, self.radius, speed)
        new_ball.vx = speed * math.sin(angle_rad)
        new_ball.vy = -speed * math.cos(angle_rad)
        
        return new_ball
    
    def check_game_over(self):
        if self.y - self.radius > SCREEN_HEIGHT:
            return True
        return False
    
    def draw(self, surface, power_mode=False):
        if power_mode:
            pygame.draw.circle(surface, DARK_RED, (int(self.x), int(self.y)), self.radius + 2)
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        else:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

# 패들 생성
paddle = Paddle(
    SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2,
    SCREEN_HEIGHT - 50,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

# 공 생성
balls = [Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS - 5, BALL_RADIUS, BALL_SPEED)]

# 아이템 및 레이저 리스트
items = []
lasers = []

# 레벨 변수
level = 1
base_ball_speed = BALL_SPEED

# 목숨 시스템 변수
lives = 3
life_lost = False
life_lost_start_time = 0
flash_screen = False
flash_start_time = 0

def create_bricks(level_data):
    """텍스트 기반 맵 데이터로 블록 생성"""
    bricks = []
    for row_idx, row_str in enumerate(level_data):
        color = RAINBOW_COLORS[row_idx % len(RAINBOW_COLORS)]
        for col_idx, char in enumerate(row_str):
            if char == '#':  # 일반 블록
                x = BRICK_PADDING + col_idx * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_OFFSET_TOP + row_idx * (BRICK_HEIGHT + BRICK_PADDING)
                brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color, is_hard=False)
                bricks.append(brick)
            elif char == '@':  # 단단한 블록
                x = BRICK_PADDING + col_idx * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_OFFSET_TOP + row_idx * (BRICK_HEIGHT + BRICK_PADDING)
                brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, GRAY, is_hard=True)
                bricks.append(brick)
    return bricks

def reset_ball():
    global balls
    balls = [Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS - 5, BALL_RADIUS, base_ball_speed)]

def next_level():
    global level, balls, bricks, items, lasers, base_ball_speed, lives
    
    level += 1
    base_ball_speed += 0.3
    lives = 3
    
    reset_ball()
    
    items = []
    lasers = []
    
    paddle.laser_timer = 0
    paddle.power_timer = 0
    paddle.magnet_timer = 0
    
    # 레벨 인덱스 계산 (순환)
    level_index = (level - 1) % len(LEVELS)
    bricks = create_bricks(LEVELS[level_index])
    
    print(f"레벨 {level} 시작! 목숨: {lives}")

# 블록 생성
bricks = create_bricks(LEVELS[0])

# 게임 상태 변수
running = True
game_over = False
stage_clear = False
clear_start_time = 0

# 게임 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and stage_clear:
            stage_clear = False
            next_level()
    
    if not game_over and not stage_clear:
        # 스테이지 클리어 조건: 일반 블록(is_hard=False)이 모두 사라졌는지 확인
        normal_bricks = [brick for brick in bricks if not brick.is_hard]
        if len(normal_bricks) == 0:
            stage_clear = True
            clear_start_time = pygame.time.get_ticks()
            print("스테이지 클리어!")
    
    if stage_clear:
        current_time = pygame.time.get_ticks()
        if current_time - clear_start_time >= 2000:
            stage_clear = False
            next_level()
    
    if life_lost:
        current_time = pygame.time.get_ticks()
        if current_time - life_lost_start_time >= 1500:
            life_lost = False
    
    if flash_screen:
        current_time = pygame.time.get_ticks()
        if current_time - flash_start_time >= 300:
            flash_screen = False
    
    if not game_over and not stage_clear:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        paddle.update(mouse_x)
        
        new_lasers = paddle.shoot_laser()
        lasers.extend(new_lasers)
        
        for laser in lasers[:]:
            laser.update()
            
            if laser.is_off_screen():
                lasers.remove(laser)
            elif laser.check_brick_collision(bricks):
                lasers.remove(laser)
        
        for item in items[:]:
            item.update(paddle)
            
            if item.is_off_screen():
                items.remove(item)
            elif item.check_paddle_collision(paddle):
                items.remove(item)
                
                if item.item_type == ITEM_PLUS_1:
                    if len(balls) > 0:
                        new_ball = balls[0].clone()
                        balls.append(new_ball)
                    print("공 +1!")
                
                elif item.item_type == ITEM_DOUBLE:
                    new_balls = []
                    for ball in balls:
                        new_ball = ball.clone()
                        new_balls.append(new_ball)
                    balls.extend(new_balls)
                    print("공 x2!")
                
                elif item.item_type == ITEM_LASER:
                    paddle.activate_laser()
                    print("레이저 모드 활성화!")
                
                elif item.item_type == ITEM_POWER:
                    paddle.activate_power()
                    print("관통탄 모드 활성화!")
                
                elif item.item_type == ITEM_MAGNET:
                    paddle.activate_magnet()
                    print("자석 모드 활성화!")
        
        balls_to_remove = []
        for ball in balls:
            ball.update()
            ball.check_wall_collision()
            ball.check_brick_collision(bricks, items, paddle.power_timer > 0)
            ball.check_paddle_collision(paddle)
            
            if ball.check_game_over():
                balls_to_remove.append(ball)
        
        for ball in balls_to_remove:
            balls.remove(ball)
        
        if len(balls) == 0:
            if lives > 1:
                lives -= 1
                reset_ball()
                life_lost = True
                life_lost_start_time = pygame.time.get_ticks()
                flash_screen = True
                flash_start_time = pygame.time.get_ticks()
                print(f"목숨 소실! 남은 목숨: {lives}")
            else:
                game_over = True
                print("게임 오버!")
    
    # 화면 그리기
    if flash_screen:
        SCREEN.fill(RED)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(DARK_NAVY)
        SCREEN.blit(overlay, (0, 0))
    else:
        SCREEN.fill(DARK_NAVY)
    
    for brick in bricks:
        brick.draw(SCREEN)
    
    for laser in lasers:
        laser.draw(SCREEN)
    
    for item in items:
        item.draw(SCREEN)
    
    for ball in balls:
        ball.draw(SCREEN, paddle.power_timer > 0)
    
    paddle.draw(SCREEN)
    
    ball_count_text = font.render(f"공: {len(balls)}개", True, WHITE)
    SCREEN.blit(ball_count_text, (10, 10))
    
    level_text = font.render(f"레벨: {level}", True, WHITE)
    SCREEN.blit(level_text, (10, 50))
    
    lives_text = font.render(f"목숨: {lives}", True, WHITE)
    SCREEN.blit(lives_text, (10, 90))
    
    if life_lost:
        life_lost_text = large_font.render("목숨 소실!", True, RED)
        text_rect = life_lost_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(life_lost_text, text_rect)
    
    if stage_clear:
        clear_text = large_font.render("스테이지 클리어!", True, WHITE)
        text_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(clear_text, text_rect)
    
    if game_over:
        game_over_text = large_font.render("게임 오버", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(game_over_text, text_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
