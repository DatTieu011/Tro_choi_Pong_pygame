import pygame, sys, random

#Khởi tạo lớp chắn bóng (khi bóng dội vào tường, vào vật thể)
class Can(pygame.sprite.Sprite):
	def __init__(self,path,x_vt,y_vt):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_vt,y_vt))

#Khởi tạo lớp người chơi với lớp con chắn bóng ở trên
class Ngchoi(Can):
	def __init__(self,path,x_vt,y_vt,tocdo):
		super().__init__(path,x_vt,y_vt)
		self.tocdo = tocdo
		self.dichuyen = 0
	#Hàm thực hiện giới hạn màn hình, tránh việc bóng bị rơi ra khỏi màn hình
	def screen_constrain(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= screen_height:
			self.rect.bottom = screen_height
	#Hàm cập nhật việc di chuyển cho thanh đỡ
	def update(self,banh_group):
		self.rect.y += self.dichuyen
		self.screen_constrain()

#Khởi tạo lớp bóng với lớp con chắn bóng 
class Banh(Can):
	def __init__(self,path,x_vt,y_vt,tocdo_x,tocdo_y,Thanh):
		super().__init__(path,x_vt,y_vt)
		self.tocdo_x = tocdo_x * random.choice((-1,1))
		self.tocdo_y = tocdo_y * random.choice((-1,1))
		self.Thanh = Thanh
		self.active = False
		self.score_time = 0
	#Hàm cập nhật tốc độ banh và quán tính khi banh va chạm vào tường hoặc thanh đỡ
	def update(self):
		if self.active:
			self.rect.x += self.tocdo_x
			self.rect.y += self.tocdo_y
			self.Vacham()
		#Nếu bóng không thấy có sự va chạm thì khởi động lại bộ đếm thời gian	
		else:
			self.restart_counter()
		
	def Vacham(self):
		if self.rect.top <= 0 or self.rect.bottom >= screen_height:
			pygame.mixer.Sound.play(plob_sound)
			self.tocdo_y *= -1

		if pygame.sprite.spritecollide(self,self.Thanh,False):
			pygame.mixer.Sound.play(plob_sound)
			vacham_thanh = pygame.sprite.spritecollide(self,self.Thanh,False)[0].rect
			if abs(self.rect.right - vacham_thanh.left) < 10 and self.tocdo_x > 0:
				self.tocdo_x *= -1
			if abs(self.rect.left - vacham_thanh.right) < 10 and self.tocdo_x < 0:
				self.tocdo_x *= -1
			if abs(self.rect.top - vacham_thanh.bottom) < 10 and self.tocdo_y < 0:
				self.rect.top = vacham_thanh.bottom
				self.tocdo_y *= -1
			if abs(self.rect.bottom - vacham_thanh.top) < 10 and self.tocdo_y > 0:
				self.rect.bottom = vacham_thanh.top
				self.tocdo_y *= -1

	def reset_banh(self):
		self.active = False
		self.tocdo_x *= random.choice((-1,1))
		self.tocdo_y *= random.choice((-1,1))
		self.score_time = pygame.time.get_ticks()
		self.rect.center = (screen_width/2,screen_height/2)
		pygame.mixer.Sound.play(score_sound)
	#Thực hiện khởi động lại thời gian đếm ngược sau khi một bên đã có điểm
	def restart_counter(self):
		tg_hientai = pygame.time.get_ticks()
		countdown_number = 3

		if tg_hientai - self.score_time <= 700:
			countdown_number = 3
		if 700 < tg_hientai - self.score_time <= 1400:
			countdown_number = 2
		if 1400 < tg_hientai - self.score_time <= 2100:
			countdown_number = 1
		if tg_hientai - self.score_time >= 2100:
			self.active = True

		dem_tg = basic_font.render(str(countdown_number),True,accent_color)
		dem_tg_rect = dem_tg.get_rect(center = (screen_width/2,screen_height/2 + 50))
		pygame.draw.rect(screen,bg_color,dem_tg_rect)
		screen.blit(dem_tg,dem_tg_rect)

#Lớp đối thủ với lớp con bên trong thực hiện hành động Cản của thanh đỡ
class Doithu(Can):
	def __init__(self,path,x_vt,y_vt,tocdo):
		super().__init__(path,x_vt,y_vt)
		self.tocdo = tocdo

	def update(self,banh_group):
		if self.rect.top < banh_group.sprite.rect.y:
			self.rect.y += self.tocdo
		if self.rect.bottom > banh_group.sprite.rect.y:
			self.rect.y -= self.tocdo
		self.constrain()

	def constrain(self):
		if self.rect.top <= 0: self.rect.top = 0
		if self.rect.bottom >= screen_height: self.rect.bottom = screen_height

class GameManager:
	def __init__(self,banh_group,thanh_group):
		self.ngchoi_score = 0
		self.doithu_score = 0
		self.banh_group = banh_group
		self.thanh_group = thanh_group

	def chay_game(self):
		# Phác họa các vật thể trong game
		self.thanh_group.draw(screen)
		self.banh_group.draw(screen)

		# Cập nhật các đối tượng trong game
		self.thanh_group.update(self.banh_group)
		self.banh_group.update()
		self.reset_banh()
		self.ve_bang_diem()
	#Thực hiện tạo lại bóng sau khi đã có một bên ghi bàn
	def reset_banh(self):
		if self.banh_group.sprite.rect.right >= screen_width:
			self.doithu_score += 1
			self.banh_group.sprite.reset_banh()
		if self.banh_group.sprite.rect.left <= 0:
			self.ngchoi_score += 1
			self.banh_group.sprite.reset_banh()
	#Thực hiện phác thảo bản điểm trên giao diện chính của trò chơi
	def ve_bang_diem(self):
		ngchoi_score = basic_font.render(str(self.ngchoi_score),True,accent_color)
		doithu_score = basic_font.render(str(self.doithu_score),True,accent_color)

		ngchoi_score_rect = ngchoi_score.get_rect(midleft = (screen_width / 2 + 40,screen_height/2))
		doithu_score_rect = doithu_score.get_rect(midright = (screen_width / 2 - 40,screen_height/2))

		screen.blit(ngchoi_score,ngchoi_score_rect)
		screen.blit(doithu_score,doithu_score_rect)

#Cài đặt game
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock = pygame.time.Clock()

# Màn ảnh chính
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Pong')

#Biến toàn cục
bg_color = pygame.Color('#2F373F')
accent_color = (27,35,43)
basic_font = pygame.font.Font('freesansbold.ttf', 32)
plob_sound = pygame.mixer.Sound("bonk.ogg")
score_sound = pygame.mixer.Sound("win.ogg")
middle_strip = pygame.Rect(screen_width/2 - 2,0,4,screen_height)

#Các đối tượng trong game
ngchoi = Ngchoi('Paddle.png',screen_width - 20,screen_height/2,5)
doithu = Doithu('Paddle.png',20,screen_width/2,5)
thanh_group = pygame.sprite.Group()
thanh_group.add(ngchoi)
thanh_group.add(doithu)

#Chọn hoạt ảnh bóng 
banh = Banh('Ball.png',screen_width/2,screen_height/2,4,4,thanh_group)
banh_sprite = pygame.sprite.GroupSingle()
banh_sprite.add(banh)

game_manager = GameManager(banh_sprite,thanh_group)

#Thực hiện chèn hình ảnh nền
background_image = pygame.image.load("pong_table.jpg").convert()

while True:
	#Gán các phím và thực hiện lệnh tắt cửa sổ game khi click vào phím tắt X
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				ngchoi.dichuyen -= ngchoi.tocdo
			if event.key == pygame.K_DOWN:
				ngchoi.dichuyen += ngchoi.tocdo
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				ngchoi.dichuyen += ngchoi.tocdo
			if event.key == pygame.K_DOWN:
				ngchoi.dichuyen -= ngchoi.tocdo
	

	# Hình nền game
	pygame.draw.rect(screen,accent_color,middle_strip)
	screen.blit(background_image, [0, 0])

	# Chạy game
	game_manager.chay_game()

	# Kết xuất đồ họa và thiết lập tốc độ game 
	pygame.display.flip()
	clock.tick(120)