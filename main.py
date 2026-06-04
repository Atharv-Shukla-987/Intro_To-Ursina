import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import sys
import os

app = Ursina()

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

Audio('Assets/sound/bg.mp3',volume=0.5, loop=True, autoplay=True)

TEXTURES = {
    't1': "./Assets/Img/fast_enemy.png",
    't2': "./Assets/Img/tank_enemy.png",
    't3': "./Assets/Img/normal_enemy.png"
}

ENEMY_TYPES = [
    {
        "name" : "fast",
        "texture" : TEXTURES['t1'],
        "speed" : (4,7),
        "health" : 2,
        "damage" : 3,
        "scale" : (1,2,1),
        "y":1.5
    },
    {
        "name" : "strong",
        "texture" : TEXTURES['t2'],
        "speed" : (0.5 , 1.5),
        "health" : 5,
        "damage" : 5,
        "scale" : (2,2.5,0.8),
        "y":1
    },
    {
        "name" : "normal",
        "texture" : TEXTURES['t3'],
        "speed" : (1,3),
        "health" : 1,
        "damage" : 2,
        "scale" : (1.25,2,0.8),
        "y":1
    }
]

class Menu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.enabled = True
        self.game_started = False

        self.bg = Entity(
            parent= camera.ui,
            model='quad',
            color = color.black66,
            scale=(2,1),
            z=1
        )
 
        self.tittle = Text(
            text = 'THE DEATH TRAP',
            parent = camera.ui,
            origin=(0,0),
            scale= 1.5 ,
            position = (0,0.25),
        )
        self.subtitle = Text(
            text = 'ITS NOT A GAME, ITS REAL LIFE WHERE YOU ALWAYS LOSS'
            ,parent = camera.ui,
            origin=(0,0),
            scale = 1.5,
            color = color.gray,
            position = (0,0.15)
        ) 

        self.btnstart = Button(
            text = 'Start Game',
            parent = camera.ui ,
            scale = (0.3,0.07),
            position =  (0,0),
            color = color.dark_gray,
            on_click = self.sg
        ) 
        self.btnquit = Button(
            text='Quit',
            parent=camera.ui,
            position=(0, -0.12),
            scale=(0.3 , 0.07),
            color = color.dark_gray,
            on_click = application.quit
        )

    def sg(self):
        self.bg.enabled= False 
        self.tittle.enabled= False 
        self.subtitle.enabled= False 
        self.btnquit.enabled= False
        self.btnstart.enabled= False
        self.enabled = False

        player.controller.enabled= True
        mouse.locked = True  
        for _ in range(8):
          Enemy()
        invoke(spawn_enemy, delay=4)





    def tp(self):
        paused  = not self.enabled
        self.enabled = not paused
        self.bg.enabled = not paused
        self.tittle.enabled = not paused
        self.subtitle.enabled = not paused
        self.btnquit.enabled = not paused
        self.btnstart.enabled = not paused
        player.controller.enabled = paused
        mouse.locked = paused
        if not self.game_started:
            return
        


class HealthBar(Entity):
    def __init__(self , max_health = 100):
        super().__init__(parent=camera.ui)

        self.max_health = max_health  
        self.max_health  = max_health

        self.fill = Entity(
            parent  = camera.ui ,
            model = 'quad',
            color = color.green,
            scale=(0.4,0.04),
            position = (-0.3 , -0.45),
            origin = (-0.5,0)
        )
    
        self.label = Text(
            text = 'HP: 100',
            parent = camera.ui ,
            position = (-0.48 ,- 0.43),
            scale = 1.2 ,
            color = color.white

        )

    def set_health(self , value):
        self.health = clamp(value , 0 , self.max_health)
        ratio = self.health / self.max_health
        self.fill.scale_x = 0.4 * ratio
        self.fill.color = color.green if ratio > 0.5 else color.orange if ratio > 0.25 else color.red
        self.label.text = f'HP: {int(self.health)}'
class Player(Entity):
    def __init__(self, **kwargs):
        self.controller = FirstPersonController(**kwargs)
        super().__init__(parent=self.controller)
        self.controller.enabled = False
        self.controller.escape_to_exit = False
        self.knife = Entity(
            parent = self.controller.camera_pivot ,
            model = 'quad',
            texture='./Assets/Img/knife',
            visible = False,
            scale = 1 ,
            z=1.5, y=-0.6, x=0.6
        )
        self.hand_pistol = Entity(
            parent=self.controller.camera_pivot,
            model='quad',
            texture='./Assets/Img/pistol', 
            visible=False,   
            scale=1,
            z=1.5, y=-0.4, x=0.6
        )
        self.hand_gun = Entity(
            parent=self.controller.camera_pivot,
            model='quad',
            texture='./Assets/Img/gun', 
            visible=False,
            scale=1,
           
            z=1.5, y=-0.5, x=1
        )
        self.unlocked        = [True, False, False]  
        self.unlock_kills    = [0, 8, 20]    
        self.weapon_damage = [1, 2, 4]         
        self.kills = 0
        self.kill_label      = Text(
            text='Kills: 0',
            parent=camera.ui,
            position=(0.6, 0.45),
            scale=1.2,
            color=color.white
      )
        self.weapons         = [self.knife ,self.hand_pistol, self.hand_gun]
        self.current_weapon  = 0
        self.health_bar      = HealthBar(max_health=100)
        self.hp              = 100
        self.alive           = True
        self.shoot_cooldown  = 0
        self.switch_weapon()
    def add_kill(self):
        self.kills += 1
        self.kill_label.text = f'Kills: {self.kills}'

        for i, needed in enumerate(self.unlock_kills):
            if not self.unlocked[i] and self.kills >= needed:
                self.unlocked[i] = True
                names = ['Knife' , 'Pistol' , 'Gun']
                level_names = ['Novice' , 'Sharpshooter' , 'Elite']
                t = Text(
                    text=f'New Level {level_names[i]} unlocked! your new weapon is {names[i]}',
                    parent = camera.ui , 
                    origin = (0,0) ,
                    scale = 2 ,
                    color = color.red
                )
                destroy(t,delay=2)
    def take_damage(self , amount):
        if not self.alive:
            return
        Audio('Assets/sound/damage', volume=0.8)
        self.hp -= amount
        self.health_bar.set_health(self.hp)
        camera.shake(duration=0.1 , magnitude=3)
        if self.hp <= 0 :
            self.alive = False
            Text('Game Over',parent = camera.ui , origin=(0,0), scale=6, color=color.red)   
            self.controller.enabled = False
    def knife_attack(self):
   
      self.knife.texture = './Assets/Img/slash'
    
      invoke(lambda: setattr(self.knife, 'texture', './Assets/Img/knife'), delay=0.5)
      for e in scene.entities :
        if getattr(e, 'is_enemy', False) and e.enabled:
            diff = e.world_position - self.controller.world_position
            if diff.length() < 4:
                e.take_hit(self.weapon_damage[self.current_weapon]) 
        if isinstance(e , Grass):
            diff = e.world_position - self.controller.world_position
            if diff.length() < 4:
                destroy(e)


    def switch_weapon(self):   
        if not self.unlocked[self.current_weapon]:
            return 
        for i, v in enumerate(self.weapons):
            v.visible = (i == self.current_weapon)

    def input(self, key):   
        if menu.enabled or not self.alive:
            return   
       
        
         
        try:
            self.current_weapon = int(key) - 1
            self.switch_weapon()
        except ValueError:
            pass
        if key == 'scroll up':
            for _ in range(len(self.weapons)):
              self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
              if self.unlocked[self.current_weapon]:
               break
            self.switch_weapon()
        if key == 'scroll down':
            for _ in range(len(self.weapons)):
                self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
                if self.unlocked[self.current_weapon]:
                     break
            self.switch_weapon()
        if key == 'left mouse down' :
            if self.current_weapon == 0 :
                 Audio('Assets/sound/knife', volume=0.9)
                 self.knife_attack()
          
            else:
                Bullet(
                model = 'sphere',
                color = color.gold ,
                scale=0.2 ,
                position=self.controller.camera_pivot.world_position,
                rotation=self.controller.camera_pivot.world_rotation,
                damage = self.weapon_damage[self.current_weapon]
            )
        
    def update(self):
        self.controller.camera_pivot.y = 2 - held_keys['shift']
        if held_keys['shift'] and self.alive:
            self.hp = min(self.hp + 0.03,100)        
            self.health_bar.set_health(self.hp)

            
           

class Enemy(Entity):
    def __init__(self, **kwargs):
        angle = random.uniform(0, 360)
        distance = random.uniform(5, 40)
        x = math.cos(math.radians(angle)) * distance
        z = math.sin(math.radians(angle)) * distance
        ran = random.randint(0, 2)
        super().__init__(
            model = 'cube',
            texture = ENEMY_TYPES[ran]['texture'],
            scale=ENEMY_TYPES[ran]['scale'],
            position = (x , ENEMY_TYPES[ran]['y'] , z),
            collider='box',
            **kwargs
        )
        self.is_enemy = True
        self.speed = random.uniform(*ENEMY_TYPES[ran]['speed'])
        self.health = ENEMY_TYPES[ran]['health']
        self.damage = ENEMY_TYPES[ran]['damage']
        self.attack_cooldown = 0
    def update(self):
        if not player or not player.alive :
            return
        if not self.enabled :
            return
        

        px , py , pz = player.controller.world_position
        ex , ey , ez = self.world_position
        dx = px-ex
        dz = pz -ez
        dist = math.sqrt(dx*dx + dz*dz)

        if dist > 1.8 :
            self.x += ((dx/dist)*self.speed* time.dt)/2
            self.z += ((dz / dist) * self.speed * time.dt)/2 

            self.rotation_y = math.degrees(math.atan2(dx,dz))

        self.attack_cooldown -= time.dt 
        if dist < 2 and self.attack_cooldown <= 0 :
            player.take_damage(self.damage)
            self.attack_cooldown = 1.5
    def take_hit(self , damage=1):
        
        self.health -= damage
        self.color  = color.orange
        invoke(setattr, self, 'color', color.red, delay=0.1)
        if self.health <= 0:
            self.enabled = False
            destroy(self)
            player.add_kill()
class Bullet(Entity):
    def __init__(self, speed=50, lifetime=10, **kwargs):
        super().__init__(**kwargs)
        Audio('Assets/sound/shoot', volume=0.9)
        camera.shake(duration=0.1 , magnitude=1)
        if player.current_weapon == 1 :
            damage = player.weapon_damage[1]
        if player.current_weapon == 2 :
            damage = player.weapon_damage[2]
        self.speed = speed
        self.lifetime = lifetime
        self.start = time.time()
    def update(self):
        self.position += self.forward * self.speed * time.dt 
        enemies = [e for e in scene.entities if isinstance(e,Enemy) and e.enabled]
        for e in enemies:
            try:
                diff = e.world_position - self.world_position 
                if diff.length() < 1.2 :
                    e.take_hit(self.damage)
                    destroy(self)
                    return
            except:
                continue
        if isinstance(e , Grass):
            diff = e.world_position - self.controller.world_position
            if diff.length() < 4:
                destroy(e)
        if time.time() - self.start > self.lifetime :
            destroy(self) 

class Grass(Entity):
    def __init__(self, **kwargs):
        x = random.uniform(-70, 70)        
        z = random.uniform(-70, 70)
        super().__init__(
            position=(x, 0.5, z),
            model='cube',
            texture='./Assets/Img/minelonggrass',
            scale=(1,2, 1),
            collider='box',
              **kwargs)
        
class Rock(Entity):
    def __init__(self, **kwargs):
        x = random.uniform(-70, 70)        
        z = random.uniform(-70, 70)
        super().__init__(
            position=(x, 0.5, z),
            model='sphere',
            texture='./Assets/Img/rock',
            scale=(0.5,0.5, 0.5),
            collider='box',
              **kwargs)
    
class Tree(Entity):
    def __init__(self, **kwargs):
        x = random.uniform(-70, 70)        
        z = random.uniform(-70, 70)
        h = random.uniform(0.5, 1.5)
        super().__init__(
            position=(x, 5.5, z),
            model='cube',
            texture='./Assets/Img/tree',
            scale=(h,10, h),
            collider='box',
              **kwargs)
        self.leave = Entity(
            position = (x , 10.5 , z),
            scale= (4,5,4),
            model='cube',
            texture='./Assets/Img/leave'
        )
   
ground = Entity(
        model='plane',
        scale=(150,1,150),
        texture='grass',
        texture_scale=(50,50),
        collider='mesh')

sky = Entity(
    model='sphere',
    texture='sky_sunset', 
    scale=500,
    double_sided=True       
)

DirectionalLight(y=4, z=-3, shadows=True)
player = Player(position=(0, 1, 0))
player.controller.enabled = False

mouse.locked = False
menu = Menu() 

for _ in range(20):
    Rock()
    Grass()

for _ in range(12):
    Tree()

def spawn_enemy():
    Enemy()
    invoke(spawn_enemy, delay=4)

def input(key):
 if key == 'escape' or key == 'esc':
        if 'menu' in globals():
            menu.tp()
            mouse.locked = not menu.enabled


app.run()

