from panda_robot import Panda
import readchar
def main(args=None):


    panda = Panda('/home/ossama/Desktop/ROBOTICS/panda_ws/src/panda/urdf/panda.urdf')
    panda.run()
    
    x, y, z = 0.307, 0.0, 0.59
    roll, pitch, yaw = 180, 0, -45        # tool pointing down
    panda.move_arm_to(x,y,z,roll,pitch,yaw)
    step = 0.01
    while True:
        try:
            key = readchar.readkey()
            match key:
                case 'w':x += step
                case 's':x -= step
                case 'a':y += step
                case 'd':y -= step
                case 'o':z += step
                case 'l':z -= step
                case 'r':
                    x, y, z = 0.307, 0.0, 0.59
                    roll, pitch, yaw = 180, 0, -45  
                    panda.move_arm_to(x,y,z,roll,pitch,yaw,duration_sec=0)
                    print('reset_finished')
            panda.move_arm_to(x,y,z,roll,pitch,yaw)
        except KeyboardInterrupt:
            break

    panda.destroy()


if __name__ == '__main__':
    main()
