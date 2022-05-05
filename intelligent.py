import argparse
import math
import random
from statistics import mean
from tkinter import *
import numpy as np

class Field:
    WIDTH = 1000
    HEIGHT = 750


# class Coordinate():
#     def __init__(self):
#         self.reset()
#
#     def reset(self):
#         self.pos=np.array([0,0])


class Bird():
    NUM = 40 
    RADIAN = 3
    SPEED = 4
    ACCUP = 1
    srcSquare = [25, 325, 125, 425]
    desSquare = [875, 325, 975, 425]
    smartCount = 20
    des = np.array([(desSquare[0]+desSquare[2])/2, (desSquare[1]+desSquare[3])/2])
    # 생성자
    def __init__(self, args):
        # self.x = random.randint(50, 100) #start position
        # self.y = random.randint(350, 400)
        self.pos = np.random.rand(1)*50+np.array([50, 350])
#        self.vx = random.randint(-self.SPEED, self.SPEED)
#        self.vy = random.randint(-self.SPEED, self.SPEED)
#         self.vx = 0
#         self.vy = 0
        self.v = np.zeros(2)

        self.r=[0]*10
        self.r[0] = args.r0
        self.r[1] = args.r1
        self.r[2] = args.r2
        self.r[3] = args.r3
        self.center_pull = args.center_pull
        self.view = args.view
        self.neighbors = None
        self.acceleration = 0
        self.smartFlag=0

        self.vf = [np.zeros(2)]*10


    def find_neighbors(self):
        self.neighbors = [agent for agent in self.birds if agent is not self and self.calc_distance(agent) <= self.view]

    def calc_distance(self, target):
        #return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
        return np.linalg.norm(target.pos-self.pos)

    def cohesion(self):
        if not self.neighbors:
            return
        #self.v1.x = mean([agent.x for agent in self.neighbors if agent is not self])
        #self.v1.y = mean([agent.y for agent in self.neighbors if agent is not self])

        self.vf[0] = np.mean([agent.pos for agent in self.neighbors if agent is not self],axis=0)

        # self.v1.x = (self.v1.x - self.x) / self.center_pull
        # self.v1.y = (self.v1.y - self.y) / self.center_pull
        self.vf[0] = (self.vf[0]-self.pos)/self.center_pull

    def separation(self):
        personal_space = 10
        self.vf[1]=np.zeros(2)
        for bird in self.neighbors:
            if bird == self:
                continue
            dist = self.calc_distance(bird)
            if dist == 0:
                continue
            if dist < personal_space:
                # self.v2.x -= (bird.x - self.x) / 2
                # self.v2.y -= (bird.y - self.y) / 2
                self.vf[1] = self.vf[1] - (bird.pos-self.pos)/2


    def alignment(self):
        if not self.neighbors:
            return

        # self.v3.x = mean([agent.vx for agent in self.neighbors if agent is not self])
        # self.v3.y = mean([agent.vy for agent in self.neighbors if agent is not self])
        self.vf[2] = np.mean([agent.v for agent in self.neighbors if agent is not self],axis=0)

        # self.v3.x = (self.v3.x - self.vx) / 2
        # self.v3.y = (self.v3.y - self.vy) / 2
        self.vf[2]=(self.vf[2] - self.v) / 2
    def normalization(self, direct, scaleValue):
        # print(1)
        # k = pow(dx, 2) + pow(dy, 2) + 0.000001
        # b = math.sqrt(k / self.ACCUP)
        # dx_2 = dx / b
        # dy_2 = dy / b
        norm=np.linalg.norm(direct) + 0.00000001     #   don't be 0
        return direct/norm*scaleValue



    def smartDirection(self):
        
        # self.vf[3]=np.array([1,0])
        direction = Bird.des-self.pos
        norm = np.linalg.norm(direction)
        self.vf[3] = direction/norm
        # self.v4.x,self.v4.y=self.des_direction(self,[self.x,self.y],self.des)

    def _collision_detection(self):
        # if self.x - Bird.RADIAN < 0:
        #     self.vx *= -1
        #     self.x = Bird.RADIAN
        # if self.x + Bird.RADIAN > Field.WIDTH:
        #     self.vx *= -1
        #     self.x = Field.WIDTH - Bird.RADIAN
        #
        # if self.y - Bird.RADIAN < 0:
        #     self.vy *= -1
        #     self.y = Bird.RADIAN
        # if self.y + Bird.RADIAN > Field.HEIGHT:
        #     self.vy *= -1
        #     self.y = Field.HEIGHT - Bird.RADIAN
        if self.pos[0] - Bird.RADIAN < 0:
            self.v[0] *= -1
            self.pos[0] = Bird.RADIAN
        if self.pos[0] + Bird.RADIAN > Field.WIDTH:
            self.v[0] *= -1
            self.pos[0] = Field.WIDTH - Bird.RADIAN

        if self.pos[1] - Bird.RADIAN < 0:
            self.v[1] *= -1
            self.pos[1] = Bird.RADIAN
        if self.pos[1] + Bird.RADIAN > Field.HEIGHT:
            self.v[1] *= -1
            self.pos[1] = Field.HEIGHT - Bird.RADIAN


    def step(self):
        self.cohesion()
        self.separation()
        self.alignment()
        if self.smartFlag==1:
            self.smartDirection()

    

    def update(self):
        # dx = self.r1 * self.v1.x + self.r2 * self.v2.x + self.r3 * self.v3.x+ self.r4 * self.v4.x
        # dy = self.r1 * self.v1.y + self.r2 * self.v2.y + self.r3 * self.v3.y+ self.r4 * self.v4.y

        # d_pos = self.r1 * self.vf[0] + \
        #        self.r2 * self.vf[1] + \
        #        self.r3 * self.vf[2] + \
        #        self.r4 * self.vf[3]
        d_pos=sum([self.r[i] * self.vf[i] for i in range(10) ])

        d_pos1=self.normalization( d_pos, self.ACCUP)
        self.v = self.v+d_pos1

        velocitynorm=np.linalg.norm(self.v)
        if velocitynorm > self.SPEED:
            # self.vx = (self.vx / distance) * self.SPEED
            # self.vy = (self.vy / distance) * self.SPEED
            self.v = self.SPEED / velocitynorm * self.v

        # self.x += self.vx
        # self.y += self.vy

        self.pos = self.pos+self.v

        self._collision_detection()

    # def clear_movement(self):
    #     self.v1.reset()
    #     self.v2.reset()
    #     self.v3.reset()

    def draw(self, drawer):
        #self.clear_movement()
        self.step()
        self.update()
        if self.smartFlag==1:
            drawer.create_oval(self.pos[0] - Bird.RADIAN,
                               self.pos[1] - Bird.RADIAN,
                               self.pos[0] + Bird.RADIAN,
                               self.pos[1] + Bird.RADIAN,
                               fill="red")
        else:
            drawer.create_oval(self.pos[0] - Bird.RADIAN,
                               self.pos[1] - Bird.RADIAN,
                               self.pos[0] + Bird.RADIAN,
                               self.pos[1] + Bird.RADIAN)
        drawer.create_line(self.pos[0],
                           self.pos[1],
                           self.pos[0] +
                           self.v[0] * 3,
                           self.pos[1] + self.v[1] * 3)



def main(args):
    Bird.birds = [Bird(args) for _ in range(Bird.NUM)]
    for i in range(Bird.smartCount):
        Bird.birds[i].smartFlag=1        # mark the intelligient birds
    root = Tk()

    canvas = Canvas(root, width=Field.WIDTH, height=Field.HEIGHT)
    canvas.pack()

    # birds[0].x = 50
    # birds[0].y = 350
    Bird.birds[0].pos=np.array([50,350])

#   Bird.birds[1].x = 1
#   Bird.birds[1].y = 100

#   Bird.birds[2].x = 100
#   Bird.birds[2].y = 1

#    Bird.birds[3].x = 100
#    Bird.birds[3].y = 100

    def animate():
        canvas.delete("all")
        canvas.create_rectangle(Bird.srcSquare, outline='red')
        canvas.create_rectangle(Bird.desSquare, outline='blue')

  
        for i,bird in enumerate(Bird.birds):
            bird.find_neighbors()
            bird.draw(canvas)
        
        # Bird.birds[0].intelligentdraw(canvas)
        # Bird.birds[1].intelligentdraw(canvas)
        # Bird.birds[2].intelligentdraw(canvas)
        # Bird.birds[3].intelligentdraw(canvas)
        # Bird.birds[4].intelligentdraw(canvas)
        root.after(20, animate)

    animate()
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boids Model parameters')
    parser.add_argument('--r0', type=float, default=2.0, help='cohesion coefficient') #원래는 1.0
    parser.add_argument('--r1', type=float, default=0.8, help='separation coefficient')
    parser.add_argument('--r2', type=float, default=0.3, help='alignment coefficient')
    parser.add_argument('--r3', type=float, default=2, help='intelligent coefficient')
    parser.add_argument('--center-pull', type=int, default=30, 
                        help='center pull coefficient for means of neighbors coordinante') #300
    parser.add_argument('--view', type=int, default=50, help='view of each birds') #150
    args = parser.parse_args()
    main(args)

    