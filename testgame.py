
# 모듈 불러오기
import pygame
from pygame.locals import *
import random # 기둥 간격 랜덤


pygame.init()

clock = pygame.time.Clock()
fps = 60 # 초당프레임

# 해상도
screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Delicious Chicken') # 파일 이름

font = pygame.font.SysFont('Bauhaus 93', 60) # 폰트

white = (255, 255, 255) # 폰트 색상

ground_scroll = 0
scroll_speed = 7 # 게임 스피드
flying = False
game_over = False
pipe_gap = 200 # 파이프 위아래 간격
pipe_frequency = 1500 # 밀리세컨드 1.5초, 파이프 생성 간격
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


# 사진 불러오기
bg = pygame.image.load('bg.png') # 배경사진
ground = pygame.image.load('ground.png') # 땅 사진
button_img = pygame.image.load('restart.png') # 다시하기 사진

# 점수
def draw_text(text, font, text_coL, x, y):
	img = font.render(text, True, text_coL)
	screen.blit(img, (x, y))

def reset_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0 # 점수 초기화
	return score 


class Bird(pygame.sprite.Sprite): # sprite를 사용하면 이미지, 위치, 충돌을 통합해서 처리

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range(1,4):
			img = pygame.image.load(f'bird{num}.png') # 새 이미지
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False

	def update(self):

		if flying == True:
			self.vel += 0.5     # 점프 회복
			if(self.vel) > 8:   # 중력
				self.vel = 8
			if self.rect.bottom < 768:       # 닭이 어디까지 떨어지는지
				self.rect.y += int(self.vel)

		if game_over == False:

			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.vel = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

# 닭 사진이 바뀌는 빠르기(날개)
			self.counter += 1  
			flap_cooldown = 8

			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
			self.image = self.images[self.index]

			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2) # 점프할 때 기울어지는 정도
		else:
			self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):

	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('pipe.png') # kfc 기둥 이미지
		self.rect = self.image.get_rect()
# 기둥 위아래
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		if position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()

# 다시하기
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):

		action = False

		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True


		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action




bird_group = pygame.sprite.Group() # 닭
pipe_group = pygame.sprite.Group() # kfc

flappy = Bird(100, int(screen_height / 2)) # 시작 위치

bird_group.add(flappy)

button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img) #다시하기 위치


run = True
while run:

	clock.tick(fps)

	screen.blit(bg, (0,0))

	bird_group.draw(screen)
	bird_group.update()
	pipe_group.draw(screen)

	screen.blit(ground, (ground_scroll, 768))
# 점수 측정 방식
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1  # 점수
				pass_pipe = False

			
	draw_text(str(score), font, white, int(screen_width / 2), 20) # 점수 위치

	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True


	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False

	if game_over == False and flying == True:

		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100) # 파이프 생성
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

# 땅 왼쪽으로 이동
		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0

		pipe_group.update()

	if game_over == True:
		if button.draw() == True:
			game_over = False
			score = reset_game()


	

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False 
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

pygame.quit()