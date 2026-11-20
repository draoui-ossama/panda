from panda_controller import PandaController
def main(args=None):


    panda = PandaController()
    

    try:
        # Move arm to a target configuration
        panda.move_arm(
            [0.5, 0.5, 0.2, -1.8, 0.2, 1.5, 0.5],
            duration=5
        )

        # Open gripper
        panda.move_hand(0.00)


    except KeyboardInterrupt:
        pass

    finally:
        panda.destroy()


if __name__ == '__main__':
    main()
