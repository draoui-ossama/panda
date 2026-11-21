import numpy as np
from nodes.joint_reader import JointReader
import rclpy
class Homogene:
    def __init__(self,q,alpha,a,d):
        ca = np.cos(alpha)
        sa = np.sin(alpha)
        cq = np.cos(q)
        sq = np.sin(q)
        self.T = np.matrix([
            [cq,    -sq,     0,     a],
            [ca*sq, ca*cq, -sa, -d*sa],
            [sa*sq, sa*cq,  ca,  d*ca],
            [0,     0,       0,     1]
        ])
    def __matmul__(self,other):
        H = Homogene(0,0,0,0)
        H.T = self.T @ other.T
        return H
    @property
    def R(self):
        return self.T[:3,:3][:]

    @property
    def P(self):
        return self.T[:3,-1][:]
    def __repr__(self):
        H = (
            f"{self.T[0,0]:.3f} {self.T[0,1]:.3f} {self.T[0,2]:.3f} | {self.T[0,3]:.3f}\n"
            f"{self.T[1,0]:.3f} {self.T[1,1]:.3f} {self.T[1,2]:.3f} | {self.T[1,3]:.3f}\n"
            f"{self.T[2,0]:.3f} {self.T[2,1]:.3f} {self.T[2,2]:.3f} | {self.T[2,3]:.3f}\n"
            "-----------------------------\n"
            f"{self.T[3,0]:.3f} {self.T[3,1]:.3f} {self.T[3,2]:.3f} | {self.T[3,3]:.3f}\n"
            )
        return H

class Jacobien:
    def __init__(self,q1,q2,q3,q4,q5,q6,q7):
        T1 = Homogene(q1,0,0,0.333)
        T2 = Homogene(q2,-np.pi/2,0,0)
        T3 = Homogene(q3,np.pi/2,0,0.316)
        T4 = Homogene(q4,np.pi/2,0.0825,0)
        T5 = Homogene(q5,-np.pi/2,-0.0825,0.384)
        T6 = Homogene(q6,np.pi/2,0,0)
        T7 = Homogene(q7,np.pi/2,0.088,0.0)
        T8 = Homogene(0,0,0.0,0.107)
        self.T = T1@T2@T3@T4@T5@T6@T7
    def __repr__(self):
        return self.T.__repr__()








def main():
    rclpy.init()
    jr = JointReader()
    rclpy.spin_once(jr,timeout_sec=1)
    q = jr.q[2:]
    J = Jacobien(*q)
    print(J)




if __name__ == "__main__":
    main()