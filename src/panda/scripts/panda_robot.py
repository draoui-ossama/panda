from nodes.panda_controller import PandaController
from nodes.joint_reader import JointReader
from spatialmath import SE3
from rclpy.executors import MultiThreadedExecutor
import roboticstoolbox as rtb
import rclpy
import threading
import time

class Panda:
    def __init__(self,urdf):
        rclpy.init()
        self.robot = rtb.Robot.URDF(urdf)
        self.controller = PandaController()
        self.reader = JointReader()
        self.logger = self.controller.get_logger()
        self.ex = MultiThreadedExecutor()
        self.ets = self.robot.ets("panda_link0", "panda_link8")
    
    def move_arm_to(self,x,y,z,roll,pitch,yaw,duration_sec=0,duration_ms=100):
        T = SE3(x,y,z)*SE3.RPY([roll,pitch,yaw],unit='deg')
        print(self.reader.q)
        sol = self.ets.ikine_LM(T,q0=self.reader.th)
        if sol.success:
            self.controller.move_arm(list(sol.q)[:7],duration_sec,duration_ms)
        else:
            self.logger.error(f"FAILED TO GO TO [{x},{y},{z}][{roll},{pitch},{yaw}] \n {sol.reason}")

    
            
    def run(self):
        
        self.ex.add_node(self.controller)
        self.ex.add_node(self.reader)
        threading.Thread(target=self.ex.spin,daemon=True).start()
        while self.reader.q is None:           # wait for the first joint message
            time.sleep(0.05)
    def destroy(self):
        self.controller.destroy_node()
        self.reader.destroy_node()
        self.ex.shutdown()
        rclpy.shutdown()