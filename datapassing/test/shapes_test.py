import unittest
from typing import List

import numpy as np

import datapassing.hydrusModflowPassing as DataPassing


class HydrusShapesTest(unittest.TestCase):

    @staticmethod
    def test_four_shapes():
        HydrusShapesTest.create_shape_files()
        sample_shape_masks = ["masks/" + base_name for base_name in
                              ["mask1.npy", "mask2.npy", "mask3.npy", "mask4.npy"]]

        sample_hydrus_output = ["hydrus_out/" + base_name for base_name in
                                ["t_level1.out", "t_level2.out", "t_level3.out", "t_level4.out"]]

        shape_info_files = DataPassing.HydrusModflowPassing.create_shape_info_data(list(zip(sample_shape_masks, sample_hydrus_output)))
        shapes = DataPassing.HydrusModflowPassing.read_shapes_from_files(shape_info_files)

        expected = np.array([[-2.7497, -2.7497, -2.8497, -2.8497, -2.8497, 0., 0., 0., 0., 0.],
                             [-2.7497, -2.7497, -2.8497, -2.8497, -2.8497, 0., 0., 0., 0., 0.],
                             [-5.9497, -5.9497, -2.8497, -2.8497, -2.8497, 0., 0., 0., 0., 0.],
                             [-5.9497, -5.9497, -2.8497, -3.1497, -3.1497, 0., 0., 0., 0., 0.],
                             [-5.9497, -5.9497, -3.1497, -3.1497, -3.1497, 0., 0., 0., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]])

        result = DataPassing.HydrusModflowPassing("./simple1", "simple1.nam", shapes)
        np.testing.assert_array_equal(result.update_rch(stress_period=0), expected)

    @staticmethod
    def create_shape_files() -> None:
        HydrusShapesTest.create_shape1()
        HydrusShapesTest.create_shape2()
        HydrusShapesTest.create_shape3()
        HydrusShapesTest.create_shape4()

    @staticmethod
    def create_shape1() -> None:
        np.save("mask1", np.array([[1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))

    @staticmethod
    def create_shape2() -> None:
        np.save("mask2", np.array([[0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                                   [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))

    @staticmethod
    def create_shape3() -> None:
        np.save("mask3", np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))

    @staticmethod
    def create_shape4() -> None:
        np.save("mask4", np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))


if __name__ == '__main__':
    unittest.main()
