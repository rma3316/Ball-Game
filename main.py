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

# 폰트 설정
font = pygame.font.Font(None, 36)
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

# 아이템 설정
ITEM_DROP_RATE = 0.3  # 30% 확률로 아이템 드롭
ITEM_SIZE = 15
ITEM_SPEED = 3
ITEM_COLOR = (0, 255, 255)  # 청록색

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

class Paddle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
    
    def update(self, mouse_x):
        # 마우스 X 좌표를 패들 중심에 맞춤
        self.rect.centerx = mouse_x
        
        # 화면 밖으로 나가지 않도록 제한
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
    
    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = ITEM_SIZE
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.speed = ITEM_SPEED
    
    def update(self):
        # 아래로 떨어짐
        self.y += self.speed
        self.rect.center = (self.x, self.y)
    
    def is_off_screen(self):
        # 화면 아래로 떨어졌는지 확인
        return self.y > SCREEN_HEIGHT
    
    def check_paddle_collision(self, paddle):
        # 패들과 충돌 체크
        return self.rect.colliderect(paddle.rect)
    
    def draw(self, surface):
        pygame.draw.circle(surface, ITEM_COLOR, (int(self.x), int(self.y)), self.size // 2)


class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        # 위쪽으로 발사 (y는 음수, x는 0으로 시작)
        self.vx = 0
        self.vy = -speed
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    
    def update(self):
        # 공 이동
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def check_wall_collision(self):
        # 왼쪽 벽 충돌
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = -self.vx
        
        # 오른쪽 벽 충돌
        if self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -self.vx
        
        # 위쪽 벽 충돌
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = -self.vy
    
    def check_paddle_collision(self, paddle):
        # 패들과 충돌 체크
        if self.rect.colliderect(paddle.rect):
            # 공이 패들의 위쪽에 있는지 확인 (밑에서 위로 튕기도록)
            if self.vy > 0:
                # 패들의 어느 부분에 닿았는지 계산 (0.0 ~ 1.0, 왼쪽 끝이 0, 오른쪽 끝이 1)
                hit_pos = (self.x - paddle.rect.left) / paddle.width
                # 패들 중앙을 기준으로 -1 ~ 1 사이의 값으로 변환
                hit_pos = (hit_pos - 0.5) * 2
                
                # 패들 끝에 가까울수록 각도가 커지도록 (-60도 ~ 60도 범위)
                angle = hit_pos * 60
                angle_rad = math.radians(angle)
                
                # 속도 벡터 업데이트
                speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
                self.vx = speed * math.sin(angle_rad)
                self.vy = -speed * math.cos(angle_rad)
                
                # 공이 패들 안에 들어가지 않도록 위치 조정
                self.y = paddle.rect.top - self.radius
    
    def check_brick_collision(self, bricks, items):
        # 공과 블록의 충돌 체크
        for brick in bricks[:]:  # 리스트 복사본으로 반복 (삭제를 위해)
            if self.rect.colliderect(brick.rect):
                # 충돌 방향 계산
                ball_center_x = self.rect.centerx
                ball_center_y = self.rect.centery
                brick_center_x = brick.rect.centerx
                brick_center_y = brick.rect.centery
                
                # 충돌 지점으로부터의 거리 계산
                dx = ball_center_x - brick_center_x
                dy = ball_center_y - brick_center_y
                
                # 아이템 드롭 확률 체크
                if random.random() < ITEM_DROP_RATE:
                    item = Item(brick_center_x, brick_center_y)
                    items.append(item)
                
                # 블록 제거
                bricks.remove(brick)
                
                # 충돌 방향에 따라 반사
                # X 방향 충돌인지 Y 방향 충돌인지 판단
                if abs(dx) > abs(dy):
                    # X 방향 충돌 (좌우)
                    self.vx = -self.vx
                else:
                    # Y 방향 충돌 (상하)
                    self.vy = -self.vy
                
                # 공이 블록 안에 들어가지 않도록 위치 조정
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
                return True
        return False
    
    def clone(self):
        # 공을 복제 (새로운 각도로)
        angle = random.uniform(-45, 45)  # -45도 ~ 45도 사이의 각도
        angle_rad = math.radians(angle)
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        
        new_ball = Ball(self.x, self.y, self.radius, speed)
        new_ball.vx = speed * math.sin(angle_rad)
        new_ball.vy = -speed * math.cos(angle_rad)  # 위쪽 방향
        
        return new_ball
    
    def check_game_over(self):
        # 공이 화면 아래로 떨어졌는지 확인
        if self.y - self.radius > SCREEN_HEIGHT:
            return True
        return False
    
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

# 패들 생성 (화면 하단 중앙)
paddle = Paddle(
    SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2,
    SCREEN_HEIGHT - 50,
    PADDLE_WIDTH,
    PADDLE_HEIGHT
)

# 공 생성 (패들 위에 배치) - 리스트로 관리
balls = [Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS - 5, BALL_RADIUS, BALL_SPEED)]

# 아이템 리스트
items = []

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
    """레벨에 따라 벽돌 줄 수 반환"""
    # 1레벨: 10줄, 2레벨: 12줄, 3레벨: 15줄, 이후는 2줄씩 증가
    if level == 1:
        return 10
    elif level == 2:
        return 12
    elif level == 3:
        return 15
    else:
        return min(15 + (level - 3) * 2, 20)  # 최대 20줄로 제한

def create_bricks(brick_rows):
    """벽돌 생성 함수"""
    bricks = []
    for row in range(brick_rows):
        color = RAINBOW_COLORS[row % len(RAINBOW_COLORS)]
        for col in range(BRICK_COLS):
            x = BRICK_GAP + col * (BRICK_WIDTH + BRICK_GAP)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
            brick = Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color)
            bricks.append(brick)
    return bricks

def reset_ball():
    """공을 패들 위에 다시 생성"""
    global balls
    balls = [Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS - 5, BALL_RADIUS, base_ball_speed)]

def next_level():
    """다음 레벨로 이동하는 함수"""
    global level, balls, bricks, items, base_ball_speed, lives
    
    # 레벨 증가
    level += 1
    
    # 공 속도 증가 (매 레벨마다 0.3씩 증가)
    base_ball_speed += 0.3
    
    # 목숨 초기화 (새 스테이지는 새 마음으로!)
    lives = 3
    
    # 공 초기화 (1개, 패들 위에 배치)
    reset_ball()
    
    # 아이템 리스트 초기화
    items = []
    
    # 벽돌 재생성 (레벨에 따라 줄 수 증가)
    brick_rows = get_brick_rows_for_level(level)
    bricks = create_bricks(brick_rows)
    
    print(f"레벨 {level} 시작! 벽돌 {brick_rows}줄, 목숨: {lives}")

# 블록 생성 (초기 레벨)
bricks = create_bricks(get_brick_rows_for_level(level))

# 게임 상태 변수
running = True
game_over = False
stage_clear = False
clear_start_time = 0

# 게임 루프
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 스테이지 클리어 중일 때 클릭으로 다음 레벨 이동
        if event.type == pygame.MOUSEBUTTONDOWN and stage_clear:
            stage_clear = False
            next_level()
    
    # 스테이지 클리어 체크 (매 프레임 확인)
    if not game_over and not stage_clear and len(bricks) == 0:
        stage_clear = True
        clear_start_time = pygame.time.get_ticks()
        print("STAGE CLEAR!")
    
    # 스테이지 클리어 중 처리
    if stage_clear:
        current_time = pygame.time.get_ticks()
        # 2초 경과 시 자동으로 다음 레벨로
        if current_time - clear_start_time >= 2000:
            stage_clear = False
            next_level()
    
    # Life Lost 메시지 타이머
    if life_lost:
        current_time = pygame.time.get_ticks()
        if current_time - life_lost_start_time >= 1500:  # 1.5초 후 메시지 제거
            life_lost = False
    
    # 화면 깜빡임 효과 타이머
    if flash_screen:
        current_time = pygame.time.get_ticks()
        if current_time - flash_start_time >= 300:  # 0.3초 동안 깜빡임
            flash_screen = False
    
    # 게임 오버 체크
    if not game_over and not stage_clear:
        # 마우스 위치 가져오기
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # 패들 업데이트
        paddle.update(mouse_x)
        
        # 아이템 업데이트
        for item in items[:]:
            item.update()
            
            # 화면 밖으로 나간 아이템 제거
            if item.is_off_screen():
                items.remove(item)
            
            # 패들과 충돌 체크
            elif item.check_paddle_collision(paddle):
                items.remove(item)
                # 공 분열: 현재 화면에 있는 모든 공을 각각 1개씩 복제
                new_balls = []
                for ball in balls:
                    new_ball = ball.clone()
                    new_balls.append(new_ball)
                balls.extend(new_balls)
        
        # 공 업데이트
        balls_to_remove = []
        for ball in balls:
            ball.update()
            
            # 벽 충돌 체크
            ball.check_wall_collision()
            
            # 블록 충돌 체크 (아이템 드롭 포함)
            ball.check_brick_collision(bricks, items)
            
            # 패들 충돌 체크
            ball.check_paddle_collision(paddle)
            
            # 화면 아래로 떨어진 공 제거
            if ball.check_game_over():
                balls_to_remove.append(ball)
        
        # 화면 아래로 떨어진 공 제거
        for ball in balls_to_remove:
            balls.remove(ball)
        
        # 모든 공이 떨어졌을 때 처리
        if len(balls) == 0:
            if lives > 1:
                # 목숨이 남아있으면 목숨 감소 및 공 재생성
                lives -= 1
                reset_ball()
                life_lost = True
                life_lost_start_time = pygame.time.get_ticks()
                flash_screen = True
                flash_start_time = pygame.time.get_ticks()
                print(f"목숨 소실! 남은 목숨: {lives}")
            else:
                # 목숨이 없으면 게임 오버
                game_over = True
                print("게임 오버! 모든 목숨을 잃었습니다.")
    
    # 화면 그리기
    if flash_screen:
        # 빨간색 깜빡임 효과
        SCREEN.fill(RED)
        # 깜빡임 중에도 반투명하게 게임 요소 표시
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(DARK_NAVY)
        SCREEN.blit(overlay, (0, 0))
    else:
        SCREEN.fill(DARK_NAVY)
    
    # 블록 그리기
    for brick in bricks:
        brick.draw(SCREEN)
    
    # 아이템 그리기
    for item in items:
        item.draw(SCREEN)
    
    # 공 그리기
    for ball in balls:
        ball.draw(SCREEN)
    
    paddle.draw(SCREEN)
    
    # 공 개수 표시 (왼쪽 위)
    ball_count_text = font.render(f"공: {len(balls)}개", True, WHITE)
    SCREEN.blit(ball_count_text, (10, 10))
    
    # 레벨 표시 (왼쪽 위, 공 개수 아래)
    level_text = font.render(f"레벨: {level}", True, WHITE)
    SCREEN.blit(level_text, (10, 50))
    
    # 목숨 표시 (왼쪽 위, 레벨 아래)
    lives_text = font.render(f"목숨: {lives}", True, WHITE)
    SCREEN.blit(lives_text, (10, 90))
    
    # Life Lost 메시지 표시
    if life_lost:
        life_lost_text = large_font.render("Life Lost!", True, RED)
        text_rect = life_lost_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(life_lost_text, text_rect)
    
    # 스테이지 클리어 메시지 표시
    if stage_clear:
        clear_text = large_font.render("STAGE CLEAR!", True, WHITE)
        text_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(clear_text, text_rect)
    
    # 게임 오버 메시지 표시
    if game_over:
        game_over_text = large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(game_over_text, text_rect)
    
    # 화면 업데이트
    pygame.display.flip()
    
    # FPS 제한
    clock.tick(FPS)

# 게임 종료
pygame.quit()
sys.exit()
