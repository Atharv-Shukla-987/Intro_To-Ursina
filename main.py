from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

Audio('Assets/sound/bg.mp3',volume=0.5, loop=True, autoplay=True)

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
        

        self.weapons         = [self.hand_pistol, self.hand_gun]
        self.current_weapon  = 0
        self.health_bar      = HealthBar(max_health=100)
        self.hp              = 100
        self.alive           = True
        self.shoot_cooldown  = 0
        self.switch_weapon()
    
    def take_damage(self , amount):
        if not self.alive:
            return
        Audio('Assets/sound/damage', volume=1.2)
        self.hp -= amount
        self.health_bar.set_health(self.hp)
        camera.shake(duration=0.1 , magnitude=3)
        if self.hp <= 0 :
            self.alive = False
            Text('Game Over',parent = camera.ui , origin=(0,0), scale=6, color=color.red)   
            self.controller.enabled = False

    


    def switch_weapon(self):    
        for i, v in enumerate(self.weapons):
            v.visible = (i == self.current_weapon)

    def input(self, key):      
        try:
            self.current_weapon = int(key) - 1
            self.switch_weapon()
        except ValueError:
            pass
        if key == 'scroll up':
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            self.switch_weapon()
        if key == 'scroll down':
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
            self.switch_weapon()
        if key == 'left mouse down' :
            Bullet(
                model = 'sphere',
                color = color.gold ,
                scale=0.2 ,
                position=self.controller.camera_pivot.world_position,
                rotation=self.controller.camera_pivot.world_rotation
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

        super().__init__(
            model = 'cube',
            texture = "./Assets/Img/enemy",
            scale=(1.5,2.5,1)
            , position = (x , 1.5 , z),
            collider='box',
            **kwargs
        )
        self.speed = random.uniform(1, 5)
        self.health = 4
        self.damage = 5
        self.attack_cooldown = 0
    def update(self):
        if not player or not player.alive :
            return
        if not self.enabled:
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
    def take_hit(self):
        
        self.health -= 1
        self.color  = color.orange
        invoke(setattr, self, 'color', color.red, delay=0.1)
        if self.health <= 0:
            self.enabled = False
            destroy(self)
 
class Bullet(Entity):
    def __init__(self, speed=50, lifetime=10, **kwargs):
        super().__init__(**kwargs)
        Audio('Assets/sound/shoot', volume=0.9)
        camera.shake(duration=0.1 , magnitude=1)
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
                    e.take_hit()
                    destroy(self)
                    return
            except:
                continue
        if time.time() - self.start > self.lifetime :
            destroy(self) 
        

app = Ursina()
ground = Entity(model='plane', scale=(100,1,100), texture='grass', texture_scale=(50,50), collider='box')
player = Player(position=(0, 1, 0))

for _ in range(5):
    Enemy()
 

def spawn_enemy():
    Enemy()
    invoke(spawn_enemy, delay=4)
 
invoke(spawn_enemy, delay=4)
 
app.run()

