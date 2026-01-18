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

# 폰트 설정
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 20)
medium_font = pygame.font.Font(None, 28)
bold_font = pygame.font.Font(None, 32)
bold_font.set_bold(True)
large_font = pygame.font.Font(None, 72)

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
ITEM_PLUS_1 = "plus_1"      # 파랑: 공 +1
ITEM_DOUBLE = "double"       # 초록: 공 x2
ITEM_LASER = "laser"         # 노랑: 레이저 모드
ITEM_POWER = "power"         # 빨강: 관통탄 모드
ITEM_MAGNET = "magnet"       # 보라: 아이템 자석 모드

# 아이템 색상 매핑
ITEM_COLORS = {
    ITEM_PLUS_1: BLUE,
    ITEM_DOUBLE: GREEN,
    ITEM_LASER: YELLOW,
    ITEM_POWER: RED,
    ITEM_MAGNET: PURPLE
}

# 아이템 설정
ITEM_DROP_RATE = 0.3  # 30% 확률로 아이템 드롭
ITEM_RADIUS = 18  # 아이템 반지름
ITEM_BASE_SPEED = 3

# 레이저 설정
LASER_WIDTH = 3
LASER_HEIGHT = 20
LASER_SPEED = 15
LASER_COLOR = YELLOW

# 블록 설정
BRICK_ROWS = 15
BRICK_COLS = 10
BRICK_GAP = 3
BRICK_WIDTH = (SCREEN_WIDTH - (BRICK_COLS + 1) * BRICK_GAP) // BRICK_COLS
BRICK_HEIGHT = 25
BRICK_OFFSET_TOP = 50

# 무지개 색상 정의 (15가지)
RAINBOW_COLORS = [
    (255, 0, 0),      # 빨강
    (255, 127, 0),    # 주황
    (255, 255, 0),    # 노랑
    (191, 255, 0),    # 연두
    (0, 255, 0),      # 초록
    (0, 255, 127),    # 청록
    (0, 255, 255),    # 하늘색
    (0, 127, 255),    # 파랑
    (0, 0, 255),      # 남색
    (127, 0, 255),    # 보라
    (255, 0, 255),    # 자홍
    (255, 0, 127),    # 분홍
    (255, 64, 64),    # 연한 빨강
    (255, 165, 0),    # 오렌지
    (255, 192, 203),  # 핑크
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
        # 레이저 빔 효과
        pygame.draw.rect(surface, (255, 255, 200), self.rect.inflate(-1, 0))

class Paddle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        
        # 버프 타이머 (프레임 단위)
        self.laser_timer = 0
        self.power_timer = 0
        self.magnet_timer = 0
        
        # 레이저 발사 쿨다운
        self.laser_cooldown = 0
    
    def update(self, mouse_x):
        # 마우스 X 좌표를 패들 중심에 맞춤
        self.rect.centerx = mouse_x
        
        # 화면 밖으로 나가지 않도록 제한
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # 타이머 감소
        if self.laser_timer > 0:
            self.laser_timer -= 1
        if self.power_timer > 0:
            self.power_timer -= 1
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
    
    def activate_laser(self):
        self.laser_timer = 600  # 10초 (60 FPS * 10)
    
    def activate_power(self):
        self.power_timer = 600  # 10초
    
    def activate_magnet(self):
        self.magnet_timer = 300  # 5초
    
    def can_shoot_laser(self):
        return self.laser_timer > 0 and self.laser_cooldown == 0
    
    def shoot_laser(self):
        if self.can_shoot_laser():
            self.laser_cooldown = 20  # 0.33초 쿨다운
            # 패들 양쪽 끝에서 레이저 발사
            left_laser = Laser(self.rect.left + 5, self.rect.top)
            right_laser = Laser(self.rect.right - 5, self.rect.top)
            return [left_laser, right_laser]
        return []
    
    def draw(self, surface):
        # 버프 상태에 따라 패들 색상 변경
        color = WHITE
        if self.laser_timer > 0:
            color = YELLOW
        elif self.power_timer > 0:
            color = RED
        elif self.magnet_timer > 0:
            color = PURPLE
        
        pygame.draw.rect(surface, color, self.rect)
        
        # 버프 지속시간 표시
        if self.laser_timer > 0:
            timer_text = small_font.render(f"LASER:{self.laser_timer//60}s", True, YELLOW)
            surface.blit(timer_text, (self.rect.centerx - 40, self.rect.top - 20))
        if self.power_timer > 0:
            timer_text = small_font.render(f"POWER:{self.power_timer//60}s", True, RED)
            surface.blit(timer_text, (self.rect.centerx - 40, self.rect.top - 20))
        if self.magnet_timer > 0:
            timer_text = small_font.render(f"MAGNET:{self.magnet_timer//60}s", True, PURPLE)
            surface.blit(timer_text, (self.rect.centerx - 45, self.rect.top - 20))


class Brick:
    def __init__(self, x, y, width, height, color, is_hard=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_hard = is_hard  # 단단한 블록 여부
    
    def draw(self, surface):
        if self.is_hard:
            # 단단한 블록은 회색으로 표시
            pygame.draw.rect(surface, GRAY, self.rect)
            # 테두리 추가
            pygame.draw.rect(surface, WHITE, self.rect, 2)
            # 'H' 표시
            h_text = small_font.render("H", True, WHITE)
            text_rect = h_text.get_rect(center=self.rect.center)
            surface.blit(h_text, text_rect)
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
        
        # 애니메이션 변수
        self.pulse_offset = random.uniform(0, math.pi * 2)  # 랜덤 시작 위상
        self.float_offset = random.uniform(0, math.pi * 2)
        self.frame_count = 0
    
    def update(self, paddle=None):
        self.frame_count += 1
        
        # 자석 효과 적용
        if paddle and paddle.magnet_timer > 0:
            # 패들 중심으로 향하는 벡터 계산
            dx = paddle.rect.centerx - self.x
            dy = paddle.rect.centery - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # 정규화된 방향 벡터
                dx /= dist
                dy /= dist
                
                # 자석 강도 (거리에 반비례)
                magnet_strength = min(8, 800 / max(dist, 50))
                
                self.vx += dx * magnet_strength * 0.4
                self.vy += dy * magnet_strength * 0.4
                
                # 최대 속도 제한
                speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
                max_speed = 15
                if speed > max_speed:
                    self.vx = (self.vx / speed) * max_speed
                    self.vy = (self.vy / speed) * max_speed
        
        # 위치 업데이트
        self.x += self.vx
        self.y += self.vy
        
        # 둥둥 떠다니는 효과 (sin 함수 사용)
        float_amplitude = 2
        self.y += math.sin(self.frame_count * 0.1 + self.float_offset) * 0.3
        
        self.rect.center = (int(self.x), int(self.y))
    
    def is_off_screen(self):
        return self.y - self.radius > SCREEN_HEIGHT
    
    def check_paddle_collision(self, paddle):
        return self.rect.colliderect(paddle.rect)
    
    def draw(self, surface):
        # Pulse 애니메이션 (크기 변화)
        pulse = math.sin(self.frame_count * 0.15 + self.pulse_offset) * 2
        current_radius = self.radius + pulse
        
        color = ITEM_COLORS[self.item_type]
        
        # 아이템 원 그리기
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(current_radius))
        
        # 흰색 테두리
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(current_radius), 2)
        
        # 내부 텍스트
        if self.item_type == ITEM_PLUS_1:
            # 작은 공 그림 + 텍스트
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
    
    def check_wall_collision(self):
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = -self.vx
        
        if self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx
        
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = -self.vy
    
    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            if self.vy > 0:
                hit_pos = (self.x - paddle.rect.left) / paddle.width
                hit_pos = (hit_pos - 0.5) * 2
                
                angle = hit_pos * 60
                angle_rad = math.radians(angle)
                
                speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
                self.vx = speed * math.sin(angle_rad)
                self.vy = -speed * math.cos(angle_rad)
                
                self.y = paddle.rect.top - self.radius
    
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
                
                # 아이템 드롭
                if random.random() < ITEM_DROP_RATE:
                    item_type = self.get_random_item_type()
                    item = Item(brick_center_x, brick_center_y, item_type)
                    items.append(item)
                
                # 블록 제거 준비
                should_remove = True
                should_bounce = True
                
                if power_mode:
                    # 관통탄 모드
                    if brick.is_hard:
                        # 단단한 블록: 튕기면서 파괴
                        should_bounce = True
                        should_remove = True
                    else:
                        # 일반 블록: 관통 (튕기지 않음)
                        should_bounce = False
                        should_remove = True
                else:
                    # 일반 모드
                    if brick.is_hard:
                        # 단단한 블록: 튕기기만 하고 파괴 안 됨
                        should_bounce = True
                        should_remove = False
                    else:
                        # 일반 블록: 튕기면서 파괴
                        should_bounce = True
                        should_remove = True
                
                # 블록 제거
                if should_remove:
                    bricks_to_remove.append(brick)
                
                hit_brick = True
                
                # 반사 처리
                if should_bounce:
                    if abs(dx) > abs(dy):
                        self.vx = -self.vx
                    else:
                        self.vy = -self.vy
                    
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
                    
                    # 관통탄 아닐 때는 한 번만 처리
                    if not power_mode or brick.is_hard:
                        break
        
        # 제거할 블록들 일괄 제거
        for brick in bricks_to_remove:
            if brick in bricks:
                bricks.remove(brick)
        
        return hit_brick
    
    def get_random_item_type(self):
        """아이템 타입을 확률적으로 선택"""
        rand = random.random()
        if rand < 0.6:  # 60%
            return ITEM_PLUS_1
        elif rand < 0.7:  # 10%
            return ITEM_DOUBLE
        elif rand < 0.8:  # 10%
            return ITEM_LASER
        elif rand < 0.9:  # 10%
            return ITEM_POWER
        else:  # 10%
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
        # 관통탄 모드일 때 빨간색
        if power_mode:
            # 외곽선
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

def get_brick_rows_for_level(level):
    if level == 1:
        return 10
    elif level == 2:
        return 12
    elif level == 3:
        return 15
    else:
        return min(15 + (level - 3) * 2, 20)

def create_bricks(brick_rows):
    bricks = []
    for row in range(brick_rows):
        color = RAINBOW_COLORS[row % len(RAINBOW_COLORS)]
        for col in range(BRICK_COLS):
            x = BRICK_GAP + col * (BRICK_WIDTH + BRICK_GAP)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
            
            # 15% 확률로 단단한 블록 생성 (레벨 2 이상부터)
            is_hard = (level >= 2) and (random.random() < 0.15)
            
            brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color, is_hard)
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
    
    # 버프 초기화
    paddle.laser_timer = 0
    paddle.power_timer = 0
    paddle.magnet_timer = 0
    
    brick_rows = get_brick_rows_for_level(level)
    bricks = create_bricks(brick_rows)
    
    print(f"레벨 {level} 시작! 벽돌 {brick_rows}줄, 목숨: {lives}")

# 블록 생성
bricks = create_bricks(get_brick_rows_for_level(level))

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
    
    if not game_over and not stage_clear and len(bricks) == 0:
        stage_clear = True
        clear_start_time = pygame.time.get_ticks()
        print("STAGE CLEAR!")
    
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
        
        # 레이저 자동 발사
        new_lasers = paddle.shoot_laser()
        lasers.extend(new_lasers)
        
        # 레이저 업데이트
        for laser in lasers[:]:
            laser.update()
            
            if laser.is_off_screen():
                lasers.remove(laser)
            elif laser.check_brick_collision(bricks):
                lasers.remove(laser)
        
        # 아이템 업데이트
        for item in items[:]:
            item.update(paddle)
            
            if item.is_off_screen():
                items.remove(item)
            elif item.check_paddle_collision(paddle):
                items.remove(item)
                
                # 아이템 효과 적용
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
        
        # 공 업데이트
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
                print("게임 오버! 모든 목숨을 잃었습니다.")
    
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
        life_lost_text = large_font.render("Life Lost!", True, RED)
        text_rect = life_lost_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(life_lost_text, text_rect)
    
    if stage_clear:
        clear_text = large_font.render("STAGE CLEAR!", True, WHITE)
        text_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(clear_text, text_rect)
    
    if game_over:
        game_over_text = large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(game_over_text, text_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
