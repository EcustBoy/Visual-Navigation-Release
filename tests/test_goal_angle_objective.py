import numpy as np
import tensorflow as tf
tf.enable_eager_execution()

from obstacles.circular_obstacle_map import CircularObstacleMap
from objectives.angle_distance import AngleDistance
from trajectory.trajectory import Trajectory
from utils.fmm_map import FmmMap
from dotmap import DotMap


def create_params():
    p = DotMap()
    # Angle Distance parameters
    p.goal_angle_objective = DotMap(power=1,
                                    angle_cost=25.0)
    return p


def test_goal_angle_distance():
    # Create parameters
    p = create_params()
    
    # Create a circular obstacle map
    map_bounds = [(-2., -2.), (2., 2.)]  # [(min_x, min_y), (max_x, max_y)]
    cs = np.array([[-1.0, -1.0], [1.0, 1.0]])
    rs = np.array([[1.0], [1.0]])
    obstacle_map = CircularObstacleMap(map_bounds, cs, rs)
    
    # Create the occupancy grid
    xx, yy = np.meshgrid(np.linspace(-2., 2., 40), np.linspace(-2., 2., 40), indexing='xy')
    obstacle_occupancy_grid = obstacle_map.create_occupancy_grid(tf.constant(xx, dtype=tf.float32),
                                                                 tf.constant(yy, dtype=tf.float32))
    assert obstacle_occupancy_grid.shape == (40, 40)
    
    # Define a goal position and compute the corresponding fmm map
    fmm_map = FmmMap.create_fmm_map_based_on_goal_position(goal_positions_n2=np.array([[0., 0.]]),
                                                           map_size_2=np.array([40, 40]),
                                                           dx=0.1,
                                                           map_origin_2=np.array([-20., -20.]),
                                                           mask_grid_mn=obstacle_occupancy_grid)
    
    # Define the objective
    objective = AngleDistance(params=p.goal_angle_objective, fmm_map=fmm_map)
    
    # Define a set of positions and evaluate objective
    pos_nk2 = tf.constant([[[-1., 1.], [0.1, 0.1], [-0.1, -0.1]]], dtype=tf.float32)
    trajectory = Trajectory(dt=0.1, n=1, k=3, position_nk2=pos_nk2)

    # Compute the objective
    objective_values_13 = objective.evaluate_objective(trajectory)
    assert objective_values_13.shape == (1, 3)

    # Expected objective values
    expected_angles = np.array([-np.pi/4, -3*np.pi/4, np.pi/4])
    expected_objective = 25. * abs(expected_angles)

    assert np.allclose(objective_values_13.numpy()[0], expected_objective, atol=1e-2)
    

if __name__ == '__main__':
    test_goal_angle_distance()