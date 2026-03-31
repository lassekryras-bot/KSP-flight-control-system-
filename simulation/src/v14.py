import math

G=9.81
DT=0.02
LOG_INTERVAL=5.0
Kp=0.4
Kd=0.3

class Engine:
    def __init__(self, thrust, burn_time, throttleable):
        self.thrust=thrust
        self.burn_time=burn_time
        self.throttleable=throttleable

class Vehicle:
    def __init__(self, mass, fuel_mass, engine, parachute=True):
        self.mass=mass
        self.fuel_mass=fuel_mass
        self.engine=engine
        self.parachute=parachute

class FlightController:
    def __init__(self, vehicle):
        self.v=vehicle
        self.mode=None
        self.time=0
        self.alt=0
        self.vel=0
        self.fuel=1.0
        self.throttle=0.0
        self.prev_throttle=0.0
        self.chute_state="inactive"
        self.transitions=[]
        self.last_log_time=-LOG_INTERVAL

    def set_mode(self,new_mode):
        if self.mode!=new_mode:
            print(f"[t={self.time:5.1f}] {self.mode} → {new_mode}")
            self.transitions.append((round(self.time,2),self.mode,new_mode))
            self.mode=new_mode

    def compute_throttle(self,target_v):
        if not self.v.engine.throttleable or self.fuel<=0:
            return 0.0
        error=target_v-self.vel
        hover=(self.v.mass*G)/self.v.engine.thrust
        raw=hover+(Kp*error)-(Kd*self.vel)
        raw=max(0.0,min(1.0,raw))
        return self.prev_throttle+(raw-self.prev_throttle)*0.2

    def can_land(self):
        if not self.v.engine.throttleable or self.fuel<=0:
            return False
        max_acc=(self.v.engine.thrust/self.v.mass)-G
        if max_acc<=0:
            return False
        t=abs(self.vel)/max_acc
        d=abs(self.vel)*t*0.5
        return d<self.alt

    def update_control(self):
        if self.mode=="ground":
            self.set_mode("takeoff")
        elif self.mode=="takeoff":
            self.throttle=1.0
            if self.alt>200:
                self.set_mode("flying")
        elif self.mode=="flying":
            self.throttle=0.0
            if self.vel<0:
                self.set_mode("descent")
        elif self.mode=="descent":
            self.throttle=0.0
            if self.v.parachute:
                if self.chute_state=="inactive" and self.vel<-20 and self.alt<2000:
                    self.chute_state="semi"
                if self.chute_state=="semi" and self.alt<1000:
                    self.chute_state="full"
            if self.alt<100:
                if self.v.parachute and self.chute_state=="full":
                    self.set_mode("landing")
                elif self.can_land():
                    self.set_mode("landing")
                else:
                    self.set_mode("free_fall")
        elif self.mode=="landing":
            target_v=-2 if self.alt>10 else -0.5
            self.throttle=self.compute_throttle(target_v)
        elif self.mode=="free_fall":
            self.throttle=0.0
        self.prev_throttle=self.throttle

    def update_physics(self):
        thrust=0
        if self.fuel>0:
            if self.v.engine.throttleable:
                thrust=self.v.engine.thrust*self.throttle
                self.fuel-=DT/self.v.engine.burn_time
            else:
                thrust=self.v.engine.thrust
                self.fuel-=DT/self.v.engine.burn_time
        self.fuel=max(0,self.fuel)
        drag=0.0
        if self.chute_state=="semi":
            drag=5*self.vel*abs(self.vel)
        elif self.chute_state=="full":
            drag=500*self.vel*abs(self.vel)
        acc=(thrust-self.v.mass*G-drag)/self.v.mass
        self.vel+=acc*DT
        self.alt+=self.vel*DT
        if self.alt<=0:
            self.alt=0

    def log(self):
        if self.time>=self.last_log_time+LOG_INTERVAL:
            self.last_log_time=self.time
            print(f"[t={self.time:5.1f}] {self.mode:9} | alt={self.alt:6.0f} | vel={self.vel:7.1f} | thr={self.throttle:.2f} | fuel={self.fuel:.2f} | chute={self.chute_state}")

    def run(self,max_time=300):
        self.set_mode("ground")
        while self.time<max_time:
            self.update_control()
            self.update_physics()
            self.log()
            self.time+=DT
            if self.alt<=0 and self.time>1:
                break
        print("\nTouchdown Velocity:",round(self.vel,2))
