import argparse
import math
import random
from statistics import mean
from tkinter import *
import numpy as np
import time

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
    NUM = 1
    smartCount = 1
    RADIAN = 3
    SPEED = 4
    ACCUP = 0.1
    srcSquare = [25, 325, 125, 425]
    desSquare = [875, 325, 975, 425]

    des = np.array([(desSquare[0]+desSquare[2])/2, (desSquare[1]+desSquare[3])/2])



    ## parameters
    r = [1] * 10
    r[0] = 0.25     # cohesion coefficient
    r[1] = 0.25     # separation coefficient
    r[2] = 0.2     # alignment coefficient
    r[3] = 0.25        # intelligent coefficient
    #r[4]           # acceleration noise
    center_pull = 30
    view = 50



    deviation=[]
    aveVelocity=[]
    measurement=[[]for i in range(5)]
    measurement={
        'deviation':[],
        'avevel':[],                # average velocity
        'aveprovel':[],     # average velocity projected to the direction to the destination
        'allarrival':[]
    }
    # 생성자
    def __init__(self, args):

        self.pos = np.random.rand(2)*50+np.array([50, 350])
        #self.poss=[]
        self.v = np.zeros(2)

        # self.r=[0]*10
        # self.r[0] = args.r0
        # self.r[1] = args.r1
        # self.r[2] = args.r2
        # self.r[3] = args.r3
        # self.center_pull = args.center_pull
        # self.view = args.view

        self.neighbors = []
        self.acceleration = 0
        self.smartFlag=0

        self.arriveFlag=0
        self.vf = [np.zeros(2)]*10

    @classmethod
    def neighbors(clc):
        disTable=np.ones([clc.NUM,clc.NUM])*(clc.view+1)
        for i,first in enumerate(Bird.birds):
            for j,second in enumerate(Bird.birds[i+1:]):
                j += i+1
                disTable[i,j]=disTable[j,i]=np.linalg.norm(first.pos-second.pos)
            for i,val in enumerate(disTable[i,:]):
                if val<clc.view:
                    first.neighbors.append(clc.birds[i])


    @classmethod
    def measure(clc):
        poss= [clc.birds[i].pos for i in range(clc.NUM)]    #record all birds' position
        dev=np.std(poss)
        clc.measurement['deviation'].append(dev)

        vels=[clc.birds[i].v for i in range(clc.NUM)]
        velsnorm=np.linalg.norm(vels,axis=1)
        velsnormave=np.average(velsnorm)
        clc.measurement['avevel'].append(velsnormave)

        #provels = [clc.birds[i].v for i in range(clc.NUM)]
        vec2des=poss-clc.des
        vec2desnorm=np.linalg.norm(vec2des,axis=1)

        # projection velocity
        projvels=[np.dot(vels[i],vec2des[i])/vec2desnorm[i]**2*vec2des[i] for i in range(clc.NUM)]
        projvelsnorm=np.linalg.norm(projvels,axis=1)
        projvelsnormave=np.average(projvelsnorm)
        clc.measurement['avevel'].append(projvelsnormave)

    def dummtest(self):
        print(1)

    def find_neighbors(self):
        self.neighbors = [agent for agent in self.birds if agent is not self and self.calc_distance(agent) <= self.view]

    def calc_distance(self, target):
        #return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
        return np.linalg.norm(target.pos-self.pos)

    def cohesion(self):

        self.vf[0] = np.mean([agent.pos for agent in self.neighbors if agent is not self],axis=0)
        self.vf[0] = (self.vf[0]-self.pos)#/self.center_pull
        self.vf[0]=self.normalization(self.vf[0])

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
                #self.vf[1] = self.vf[1] - (bird.pos-self.pos)
                dirndis=bird.pos - self.pos
                dir=self.normalization(dirndis)
                dis=np.linalg.norm(dirndis)
                newdis=1/(dis/personal_space)
                self.vf[1] -= dir*newdis
                #self.vf[1]=self.normalization(self.vf[1])


    def alignment(self):

        self.vf[2] = np.mean([agent.v for agent in self.neighbors if agent is not self],axis=0)
        self.vf[2]=(self.vf[2] - self.v)
        self.vf[2]=self.normalization(self.vf[2])

    def noise(self):
        self.vf[4]=np.zeros([2])*0.05*self.ACCUP

    def normalization(self, direct, scaleValue=1):
        # print(1)
        # k = pow(dx, 2) + pow(dy, 2) + 0.000001
        # b = math.sqrt(k / self.ACCUP)
        # dx_2 = dx / b
        # dy_2 = dy / b
        norm=np.linalg.norm(direct) + 0.00000000001     #   don't be 0
        return direct/norm*scaleValue



    def smartDirection(self):
        if Bird.desSquare[:2]<list(self.pos)<Bird.desSquare[2:]:
            direction=-self.v
        else:
            direction = Bird.des-self.pos
        self.vf[3]=self.normalization(direction)

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
        self.noise()
        if self.smartFlag == 1:
            self.smartDirection()
        if not self.neighbors:          # following cal neighbors required
            return
        self.cohesion()
        self.separation()
        self.alignment()
        print(1)


    def update(self):

        d_pos=self.ACCUP*sum([self.r[i] * self.vf[i] for i in range(10) ])
        if np.linalg.norm(d_pos)>self.ACCUP:
            d_pos1=self.normalization( d_pos, self.ACCUP)
            self.v = self.v+d_pos1
        else:
            self.v = self.v +d_pos

        velocitynorm=np.linalg.norm(self.v)
        if velocitynorm > self.SPEED:
            self.v = self.SPEED / velocitynorm * self.v
        self.pos = self.pos+self.v
        if Bird.desSquare[:2] < list(self.pos) < Bird.desSquare[2:]:
            self.arriveFlag=1

        self._collision_detection()


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

    def animate():
        canvas.delete("all")
        canvas.create_rectangle(Bird.srcSquare, outline='red')
        canvas.create_rectangle(Bird.desSquare, outline='blue')
        #c = time.time()
        #Bird.birds[1].dummtest()
        # Bird.neighbors()
        # print(time.time() - c)
        for i,bird in enumerate(Bird.birds):
            # c = time.time()
            bird.find_neighbors()
            # b += time.time()-c
            bird.draw(canvas)

        Bird.measure()
        #print(time.time()-c)
        root.after(20, animate)

    Bird.birds = [Bird(args) for _ in range(Bird.NUM)]
    for i in range(Bird.smartCount):
        Bird.birds[i].smartFlag=1        # mark the intelligient birds
    j=1

    root = Tk()
    j=j+1
    print(j)
    canvas = Canvas(root, width=Field.WIDTH, height=Field.HEIGHT)
    canvas.pack()
    # while 1:
    #     animate()
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

    