import pygame
from pygame import mixer
import sys
import time

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()


## เซ็ทหน้าจอเกมส์             
screen_width = 1200
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('JHON IS MAN')
bg_img = pygame.image.load('img/cloud_sky.jpg')##โหลดพื้นหลัง Blackground
bullet_image = pygame.image.load('img/bullet.png')
bullet_image = pygame.transform.scale(bullet_image, (10, 5))
#โหลดรูป ItemBox
health_box_img = pygame.image.load('img/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/ammo_box.png').convert_alpha()
item_boxes = {
    'Health' : health_box_img,
    'Ammo'   : ammo_box_img
    }

def draw_bg():  #สร้าง function ไว้เทสีพื้นหลังพร้อมเรียกใช้งาน
    pygame.draw.line(screen,RED,(0,600),(screen_width,600))

tile_size = 50 ## เอาไว้กำหนดขนาดของ block แมพที่จะวาง

clock = pygame.time.Clock() ##เฟรมเรท
FPS = 60

moving_left = False ##ค่าจะเปลี่ยนเป็น True หรือ False ตามการกดแป้นพิมพ์ ให้ตัวละครเคลื่อนที่
moving_right = False

RED = (255,0,0) # เซ็ท ค่าสี
GREEN = (0,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)

GRAVITY = 0.75  ##ค่าแรงโน้มถ่วงที่เอาไว้ดึงตัวละครลงมา ใช้ใน function move ข้างล่าง

#โหลดเสียงเกม
pygame.mixer.set_num_channels(2)

pygame.mixer.music.load('sound/music.wav') #เสียงเพลง
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 2000)
grass_fx = pygame.mixer.Sound('sound/grass.wav') #เสียงเดินบนหญ้า
grass_fx.set_volume(0.3)
jump_fx = pygame.mixer.Sound('sound/jump.wav') #เสียงกระโดด
jump_fx.set_volume(0.1)
shoot_fx = pygame.mixer.Sound('sound/pew.wav') #เสียงยิงปืน
shoot_fx.set_volume(0.1)
heal_fx = pygame.mixer.Sound('sound/heal.wav') #เก็บกล่องยา
heal_fx.set_volume(0.2)
ded_fx = pygame.mixer.Sound('sound/oof.wav') #หมดลมหายใจ
ded_fx.set_volume(0.4)
win_fx = pygame.mixer.Sound('sound/victory.wav') #ชนะ
win_fx.set_volume(0.4)

def draw_grid():   ##ฟังก์ชันใช้วาดเส้นกำหนด block map
    for line in range(0,24): ##ใช้ loop รันตีเส้นตารางบนจอเพื่อให้เห็นระยะ block
        pygame.draw.line(screen,(255,255,255),(0,line*tile_size),(screen_width,line*tile_size))
        pygame.draw.line(screen,(255,255,255),(line*tile_size,0),(line*tile_size,screen_height))

#สร้าง HP
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #อัพเดทค่า HP
        self.health = health
        #คำนวณค่า HP
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK,(self.x - 2, self.y - 2, 154, 24)) # Black Frame
        pygame.draw.rect(screen, RED,(self.x, self.y, 150, 20)) # HP Red
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20)) # HP Green
        ### เพิ่มการแสดงข้อความ "Jhon"
        font = pygame.font.SysFont(None, 30)
        text = font.render("Jhon", True, WHITE)
        screen.blit(text, (self.x + 0, self.y - 0))  # ปรับตำแหน่งตามต้องการ

#สร้าง HP บอท
class BotHealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # อัปเดตค่า HP
        self.health = health
        # คำนวณค่า HP
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))  # Black Frame
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))  # HP Red
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))  # HP Green
        # เพิ่มการแสดงข้อความ "Enemy"
        font = pygame.font.SysFont(None, 30)
        text = font.render("Enemy", True, WHITE)
        screen.blit(text, (self.x + 0, self.y - 0))  # ปรับตำแหน่งตามต้องการ

#สร้าง ItemBox
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        # เช็คการเก็บ item
        if pygame.sprite.collide_rect(self,Jhon):
            if self.item_type == 'Health':
                sound_channel = pygame.mixer.Channel(0)
                sound_channel.play(heal_fx)
                Jhon.health += 25
                if Jhon.health > Jhon.max_health:
                    Jhon.health = Jhon.max_health
            elif self.item_type == 'Ammo':
                sound_channel = pygame.mixer.Channel(0)
                sound_channel.play(heal_fx)
                Jhon.ammo += 15
            self.kill() # ลบทิ้ง
            
##สร้าง Class พิมพ์เขียวของ map
class World():
    def __init__(self,data):

        self.tile_list = []

        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')
        
        row_count = 0 #นับว่ารันไปกี่แถวแล้ว
        for row in data: #ดึง แถว จากแมพ
            col_count = 0 #นับว่ารันไปปกี่คอมลัมแล้ว ในแถว
            for tile in row: #ดึง ทีละตัว ในแถวมา

                if tile == 1:# ถ้าเจอ 1 สร้างบล๊อค ดิน
                    img = pygame.transform.scale(dirt_img,(tile_size,tile_size)) # โหลดรูป บล๊อคมา แล้วปรับขนาด
                    img_rect = img.get_rect() # เอารูปมายัดใส่กรอบ
                    img_rect.x = col_count * tile_size # นำขนาดของ tile_size ที่เซ็ทไว้ด้านบนมา * กับคอลัมที่นับได้ปัจจุบัน เพื่อจะได้กำหนดจุดวาง บล๊อค ในแนวแกน x
                    img_rect.y = row_count * tile_size # ทำเช่นเดี๋ยวกับ แกน x แค่เปลี่ยน เป้็นแกน y
                    tile = (img,img_rect) #นำรูป กับ ขนาด ที่คำนวณมาด้านบน มาเก็บใน tile 
                    self.tile_list.append(tile) #เพิ่ม แต่ละ tile ลงไปใน tile_list

                if tile == 2:# ถ้าเจอ 2 สร้างบล๊อคหญ้า
                    img = pygame.transform.scale(grass_img,(tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1


    def draw_block(self): # สร้าง function ไว้วาด block ลงแมพ 
        for tile in self.tile_list: #ดึง tile_list มา รันอ่าน ค่า tile ที่เก็บอยู่ข้างใน ทีละตัว ซึ่งจะเก็บค่า รูปบล๊อคที่จะวาด กับ ระยะที่ละวางบล๊อค ตามลำดับ 0,1
            screen.blit(tile[0],tile[1])
            #pygame.draw.rect(screen,(255,255,255),tile[1],2)


world_data =[
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
[0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,1,1],
[0,0,0,0,0,0,0,0,0,2,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2],
[0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[2,0,0,0,0,0,2,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,2,2,2,0,0,0,0,0,0,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
[1,1,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,1,1,1,1],
[1,0,0,0,1,0,0,2,2,2,2,2,2,1,2,2,2,2,2,1,0,0,0,1,1,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],

]

World = World(world_data) #ใส่ตาราง 0,1 ข้างบน ลงไปใน Class เพื่อนำไปคำนวณต่อ

    

##สร้างคลาสของ Jhon ตัวละครในเกมส์
class Soldier():
    def __init__(self ,  x , y, speed, ammo ):
        self.img_right = []
        self.img_left = []
        self.index = 0
        self.counter = 0
        self.ammo = ammo
        self.start_ammo = ammo #กระสุนเริ่มต้น
        self.health = 100 #กำหนดค่า HP
        self.max_health = self.health
        for i in range(6):
            img_right = pygame.image.load(f'img/jhon/Run/{i}.png')
            img_right = pygame.transform.scale(img_right,(40,60))
            img_left = pygame.transform.flip(img_right,True,False)
            self.img_right.append(img_right)
            self.img_left.append(img_left)
        self.img = self.img_right[self.index]
        self.rect = self.img.get_rect()
        self.rect.x = x 
        self.rect.y = y
        self.vel_y = 0
        self.jump = False
        self.direction = 0
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.in_air = False

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, bullet_image)
        bullets.append(bullet)
        sound_channel = pygame.mixer.Channel(1)
        sound_channel.play(shoot_fx)
        # เพิ่มตรวจสอบการชนกับบอทเมื่อยิงกระสุน
        # for bot in bots:
        #     if pygame.sprite.collide_rect(bullet, bot):
        #         bot.decrease_health(10)  # ลดเลือดของบอท
        # ตรวจสอบระยะทางระหว่าง Jhon กับบอท
        # for bot in bots:
        #     distance_to_bot = abs(self.rect.x - bot.rect.x)
        #     if distance_to_bot < 500:
        #         bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, bullet_image)
        #         bullets.append(bullet)
            
    # ฟังก์ชันในการลด health
    def decrease_health(self, amount):
        self.health -= amount

    # ฟังก์ชันในการเพิ่ม health
    def increase_health(self, amount):
        self.health += amount
        # ตรวจสอบไม่ให้ health เกิน 100
        if self.health > 100:
            self.health = 100   
        
    def move(self):
        dx = 0 
        dy = 0 
        walk_cooldown = 8
        
        key = pygame.key.get_pressed()
        
        if key[pygame.K_w] and not self.jump:
            jump_fx.play()
            self.vel_y = -11
            self.jump = True
            
        if not key[pygame.K_w]:
            self.jump = False

        if key[pygame.K_a]:
            grass_fx.play()
            dx -= 3
            self.counter += 1
            self.direction = -1

        if key[pygame.K_d]:
            grass_fx.play()
            dx += 3
            self.counter += 1
            self.direction = 1
            
        
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
            
        dy += self.vel_y

        
        if self.jump == True:
            # self.vel_y = -8
            # self.jump = False
            self.in_air = True


        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.img_right):
                self.index = 0
            if self.direction == 1:
                self.img = self.img_right[self.index]
            if self.direction == -1:
                self.img = self.img_left[self.index]

        # เช็คการชน ของ block map กับ ตัวละคร
        for tile in World.tile_list:
            # แกน x 
            if tile[1].colliderect(self.rect.x + dx,self.rect.y,self.width,self.height):
                dx = 0
            # แกน y
            if tile[1].colliderect(self.rect.x,self.rect.y + dy,self.width,self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0 

                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y  = 0
                    
        #Player coord
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0

    def draw(self):
        screen.blit(self.img, self.rect )
        #pygame.draw.rect(screen,(255,255,255),self.rect,2)
        
    
##สร้าตัวคลาสของบอทที่จะอยู่ในเกม
class Bot():
    def __init__(self, x, y):
        self.img_right = []
        self.img_left = []
        self.index = 0
        self.counter = 0
        for i in range(6):
            img_right = pygame.image.load(f'img/bot/Run/{i}.png')
            img_right = pygame.transform.scale(img_right, (40, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.img_right.append(img_right)
            self.img_left.append(img_left)
        self.img = self.img_right[self.index]
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 1
        self.health = 200  # กำหนด HP ของบอทให้เป็น 200
        self.direction = 1
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.bullets = []  # เก็บกระสุนของบอท
        self.distance = 2  # ปรับค่านี้ตามต้องการ
        self.shoot_cooldown = 1000  # ปรับตัวแปรนี้ตามต้องการ (เป็น milliseconds)
        self.last_shot_time = pygame.time.get_ticks()  # เก็บเวลาที่ยิงล่าสุด

    def move(self):
        walk_cooldown = 8
        self.counter += 1

        if self.counter > walk_cooldown:
            self.counter = 1
            self.index += 1
            if self.index >= len(self.img_right):
                self.index = 0
            if self.direction == 1:
                self.img = self.img_right[self.index]
            if self.direction == -1:
                self.img = self.img_left[self.index]

        # ปรับปรุงการตรวจสอบชนกับ block map
        dx = self.distance * self.direction
        for tile in World.tile_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                break  # เพื่อหยุดตรวจสอบทันทีเมื่อพบการชน

        # ทำการเคลื่อนที่ตามทิศทางที่ตั้งไว้
        self.rect.x += dx

        # ปรับส่วนนี้เพื่อให้บอทไม่ยิงกระสุนค้าง
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_cooldown:
            # self.shoot()
            self.last_shot_time = now


    # def shoot(self):
    #     # ปรับส่วนนี้เพื่อไม่ให้บอทยิงกระสุนค้าง
    #     if self.rect.y == Jhon.rect.y and abs(self.rect.x - Jhon.rect.x) < 500:
    #         bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, bullet_image)
    #         self.bullets.append(bullet)

    def update_bullets(self):
        # ทำการอัปเดตและวาดกระสุนทั้งหมด
        for bullet in self.bullets:
            bullet.update()
            screen.blit(bullet.image, bullet.rect)

        # ตรวจสอบการชนกับ Jhon และลดเลือด
        for bullet in self.bullets:
            if pygame.sprite.collide_rect(bullet, Jhon):
                Jhon.decrease_health(25)
                self.bullets.remove(bullet)

        # ตรวจสอบการชนกับ block map และลบกระสุนที่ชน
        self.bullets = [bullet for bullet in self.bullets if not self.check_bullet_collision(bullet)]

    def check_bullet_collision(self, bullet):
        # ตรวจสอบชนกับ block map
        for tile in World.tile_list:
            if tile[1].colliderect(bullet.rect):
                return True  # บอกว่ามีการชน

        # ตรวจสอบชนกับ Jhon
        if pygame.sprite.collide_rect(bullet, Jhon):
            Jhon.decrease_health(10)
            return True  # บอกว่ามีการชน

        return False  # บอกว่าไม่มีการชน

    
    def decrease_health(self, amount):
        self.health -= amount

    # ฟังก์ชันในการเพิ่ม health
    def increase_health(self, amount):
        self.health += amount
        # ตรวจสอบไม่ให้ health เกิน 100
        if self.health > 100:
            self.health = 100
            
    def draw(self):
        screen.blit(self.img, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, bullet_image):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction

    def update(self):
        self.rect.x += 10 * self.direction  # ปรับความเร็วของกระสุนตามต้องการ
        

#สร้าง Group ของ Bot ,health_bar ,Jhon ,bot_health_bars ,bot_health_bars
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
#Item create
item_box = ItemBox('Health', 100, 500)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 500)
item_box_group.add(item_box)

# เพิ่มโค้ดนี้เพื่อสร้างบอท 4 ตัวที่ตำแหน่งต่าง ๆ
bots = [
    Bot(200, 489),
    Bot(800, 489),
    Bot(600, 339),
    Bot(800, 189),
    Bot(800, 39),
]

# ตั้งค่า shoot_cooldown สำหรับแต่ละบอท
bots[0].shoot_cooldown = 300  # ให้บอทที่ 0 ยิงทุก 2 วินาที
bots[1].shoot_cooldown = 300  # ให้บอทที่ 1 ยิงทุก 2 วินาที
bots[2].shoot_cooldown = 300  # ให้บอทที่ 2 ยิงทุก 2 วินาที
bots[3].shoot_cooldown = 300  # ให้บอทที่ 3 ยิงทุก 2 วินาที
bots[4].shoot_cooldown = 300  # ให้บอทที่ 4 ยิงทุก 2 วินาที

bot_health_bars = [BotHealthBar(10, 40, bot.health, bot.health) for bot in bots]


Jhon = Soldier(100,100,5,20)
health_bar = HealthBar(10, 10, Jhon.health, Jhon.health)


bullets = []  # เก็บกระสุนทั้งหมดในเกม

run = True
while run:
    clock.tick(FPS)

    screen.blit(bg_img,(0,0))
    # draw_bg()
    World.draw_block()

    # # กำหนดค่าให้ index_of_bot ในลูป enumerate
    # for index, bot in enumerate(bots):
    #     bot_health_bars[index].draw(bot.health)  # โชว์เเถบเลือดของบอท
    
    Jhon.move()
    Jhon.draw()
    health_bar.draw(Jhon.health)  #โชว์เเถบเลือด

    # bot.move()  # เคลื่อนที่บอท
    # bot.draw()  # วาดบอท

    for index, bot in enumerate(bots):
        bot.move()
        bot.draw()
        bot.update_bullets()
        bot_health_bars[index].draw(bot.health)  # โชว์แถบเลือดของบอท
        # ตรวจสอบทิศทางและตำแหน่งของ Jhon
        # if bot.direction == 1 and Jhon.rect.x > bot.rect.x:
        #     bot.shoot()
        # elif bot.direction == -1 and Jhon.rect.x < bot.rect.x:
        #     bot.shoot()

    #อัพเดทเเละวาด Group
    # bullet_group.update()
    # bullet_group.draw(screen)
    item_box_group.update()
    item_box_group.draw(screen)
    

        
    for bullet in bullets:
        bullet.update()
        screen.blit(bullet.image, bullet.rect)
        
    # ตรวจสอบการชนของกระสุน Jhon กับบอท
    for bullet in bullets:
        for bot in bots:
            if pygame.sprite.collide_rect(bullet, bot):
                bot.decrease_health(10)
                bullets.remove(bullet)
    # bullets = [bullet for bullet in bullets if not pygame.sprite.collide_rect(bullet, bot)]
                
    # ตรวจสอบการชนของบอทกับ Jhon
    if pygame.sprite.collide_rect(Jhon, bot) and Jhon.rect.y == bot.rect.y:
        Jhon.decrease_health(10)   

    # for bot in bots:
    #     for bullet in bot.bullets:
    #         bullet.update()
    #         screen.blit(bullet.image, bullet.rect)
    
            
    for index, bot in enumerate(bots):
        # bot.shoot()
        # ตรวจสอบ shoot_cooldown ของบอท
        now = pygame.time.get_ticks()
        if now - bot.last_shot_time > bot.shoot_cooldown:
            bot.last_shot_time = now
            # สร้างกระสุนใหม่
            bullet = Bullet(bot.rect.centerx, bot.rect.centery, bot.direction, bullet_image)
            bot.bullets.append(bullet)
            
        
    # for bot_health_bar, bot in zip(bot_health_bars, bots):
    #     bot_health_bar.draw(bot.health)
        
    # ทำการยิงกระสุนของบอท
    # for bot in bots:
    #     if bot.rect.y == Jhon.rect.y:
    #         bot.shoot()

    ##การเคลื่อนที่และวาดกระสุนของบอท
    # for bot in bots:
    #     bot.draw()  # วาดบอท
    #     for bullet in bot.bullets:
    #         bullet.update()
    #         screen.blit(bullet.image, bullet.rect)

    ##ตรวจสอบการชนของกระสุนบอทกับ Jhon       
    # for bot in bots:
    #     bot.update_bullets()
    #     for bullet in bot.bullets:
    #         if pygame.sprite.collide_rect(bullet, Jhon):
    #             Jhon.decrease_health(10)
    #             bot.bullets.remove(bullet)
            
    for bot in bots:
        if bot.health <= 0:
            bots.remove(bot)
        # if bot.health == 0 and bot.rect.y == Jhon.rect.y:
        #     new_bot = Bot(bot.rect.x, bot.rect.y)
        #     bots.append(new_bot)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Jhon.shoot()  # ยิงกระสุนเมื่อกด SPACE
            
        if Jhon.health <= 0 or not bots:
            pygame.mixer.music.stop()
            if Jhon.health <= 0:
                print("Game Over! Jhon's health is 0.")
                sound_channel = pygame.mixer.Channel(1)
                sound_channel.play(ded_fx)
                run = False
            elif not bots:
                print("Congratulations! You have defeated all the bots.")
                sound_channel = pygame.mixer.Channel(1)
                sound_channel.play(win_fx)

            ## ถามผู้เล่นว่าต้องการเล่นใหม่หรือออกจากเกม
            print("Press R to restart or Q to quit.")
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            waiting_for_input = False
                            # เริ่มเกมใหม่
                            #run = True
                            Jhon = Soldier(100,100,5,20)
                            bots = [
                                Bot(200, 489),
                                Bot(800, 489),
                                Bot(600, 339),
                                Bot(800, 189),
                                Bot(800, 39),
                            ]
                            # bullets = []
                            health_bar = HealthBar(10, 10, Jhon.health, Jhon.health)
                            bot_health_bars = [BotHealthBar(10, 40, bot.health, bot.health) for bot in bots]

                            item_box_group.empty()
                            # เพิ่ม Item ใหม่
                            item_box = ItemBox('Health', 100, 500)
                            item_box_group.add(item_box)
                            item_box = ItemBox('Ammo', 400, 500)
                            item_box_group.add(item_box)

                            run = True  # เริ่มเกมใหม่
                            # เพิ่มกระสุนใหม่ใน Group ของกระสุน
                            # bullet_group.empty()
                            bullets = []
                            for bot in bots:
                                bot.bullets = []  # รีเซ็ตกระสุนของบอท
                                bullet = Bullet(bot.rect.centerx, bot.rect.centery, bot.direction, bullet_image)
                                bot.bullets.append(bullet)
                                bullet_group.add(bullet)
                            #รีเซ็ต shoot_cooldown และสร้างกระสุนใหม่สำหรับทุกบอท
                            for bot in bots:
                                bot.shoot_cooldown = 500
                                #bot.bullets = []
                        elif event.key == pygame.K_q:
                            run = False
                            waiting_for_input = False
            
    
    pygame.display.update()
    
pygame.quit()
sys.exit()

