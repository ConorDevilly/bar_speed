import matplotlib.pyplot as plt
import argparse
from scipy.interpolate import spline
import numpy as np
import math


class BarGraph():
    """
    Loads data from a log file
    Has ability to display three graphs: Speed, Acceleration and Power
    """

    def load_data(self, path_to_data):
        """Parse necessary data from a file"""
        with open(path_to_data, 'r') as log:
            lines = log.readlines()
            self.distance_data = self._load_distance_data(lines)
            self.cm_multiplier = self._load_cm_multiplier(lines)
            self.fps = self._load_fps(lines)

    def _load_distance_data(self, log):
        """Returns distance data parsed from file"""
        distance_data = []
        for line in log:
            if 'INFO:root:Frame' in line and 'Distance moved' in line:
                distance_data.append(line.split(' ')[-1].strip())
        return distance_data

    def _load_cm_multiplier(self, log):
        """Returns cm multiplier parsed from file"""
        cm_mult = None
        for line in log:
            if 'INFO:root:CM Multiplier:' in line:
                cm_mult = float(line.split(' ')[-1].strip())
        return cm_mult

    def _load_fps(self, log):
        """Returns fps parsed from file"""
        fps = None
        for line in log:
            if 'INFO:root:Video FPS:' in line:
                fps = int(float(line.split(' ')[-1].strip()))
        return fps

    def _transform_to_velocity_data(self, distance_data, cm_multiplier):
        """Turns a list of distance data into velocity data"""
        prev_dist = 0
        velocity_data = []
        for data_point in distance_data:
            curr_dist = int(data_point)
            dist_dif = (curr_dist - prev_dist) * cm_multiplier
            velocity_data.append(dist_dif)
            prev_dist = curr_dist
        return velocity_data

    def _transform_to_speed_data(self, distance_data, cm_multiplier):
        """Turns distance data into speed data"""
        return [abs(data_point) for data_point in self._transform_to_velocity_data(distance_data, cm_multiplier)]

    def _get_total_seconds(self):
        """Return the total seconds, based on FPS"""
        if not self.fps:
            raise Exception("FPS not loaded")
        return(len(self.distance_data) / self.fps)

    def _reduce_points(self, data, interval):
        """Returns intervals of data list"""
        return data[0::interval]

    def _reduce_data_half_second(self, data):
        """Reduce number of points to be one every 0.5 seconds"""
        total_data_points = self._get_total_seconds() * 2
        point_interval = len(self.distance_data) / total_data_points
        return data[0::point_interval]

    def plot_speed_graph(self):
        """Displays a speed graph based on distance_data"""
        _title = 'Speed'
        # Convert data into speed form (absolute value of velocity)
        speed_data = self._transform_to_speed_data(self.distance_data, self.cm_multiplier)
        speed_data = self._reduce_data_half_second(speed_data)
        self.plot_graph(speed_data, _title)

    def plot_velocity_graph(self):
        """Displays a velocity graph based on distance_data"""
        _title = 'Velocity'
        velocity_data = self.distance_data
        velocity_data = self._transform_to_velocity_data(self.distance_data, self.cm_multiplier)
        velocity_data = self._reduce_data_half_second(velocity_data)
        self.plot_graph(velocity_data, _title)

    def plot_acceleration_graph(self):
        """Displays a acceleration graph based on distance_data"""
        _title = 'Acceleration'
        _xlabel = 'Seconds^2'
        speed_data = self._transform_to_speed_data(self.distance_data, self.cm_multiplier)
        speed_data = self._reduce_data_half_second(speed_data)
        acceleration_data = []

        prev_speed = 0
        # Transform speed data into acceleration data
        for curr_speed in speed_data:
            acceleration_data.append(abs(prev_speed - curr_speed))
            prev_speed = curr_speed
        self.plot_graph(acceleration_data, _title, xlabel=_xlabel)

    def plot_graph(self, data, title, ylabel='Centimeters', xlabel='Seconds'):
        """Add data to a graph"""
        total_seconds = len(data) / 2
        # Add an extra data point if there entries left over
        if len(data) % 2 == 1:
            total_seconds += 0.5
        time = np.arange(0, total_seconds, 0.5)
        plt.plot(time, data)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)

    def plot_all_graphs(self):
        """Show all graphs"""
        plt.subplot(221)
        self.plot_speed_graph()
        plt.subplot(222)
        self.plot_velocity_graph()
        plt.subplot(223)
        self.plot_acceleration_graph()

    def show_graph(self):
        """Display any loaded graphs"""
        plt.tight_layout()
        plt.show()


def setup_parser():
    """
    Sets up arguments
    :return: Parser object with path and graph flags
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Displays graphs based on given log file')
    parser.add_argument('-p', '--path', help='Path to log file', required=True)
    parser.add_argument('-g', '--graph', help='Graph to display', required=True,
                        choices=['speed', 'velocity', 'acceleration', 'all'])
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()
    bar_graph = BarGraph()
    bar_graph.load_data(args.path)
    plot_graph = {
        'speed': bar_graph.plot_speed_graph,
        'velocity': bar_graph.plot_velocity_graph,
        'acceleration': bar_graph.plot_acceleration_graph,
        'all': bar_graph.plot_all_graphs
    }.get(args.graph, 'velocity')
    plot_graph()
    bar_graph.show_graph()

if __name__ == '__main__':
    main()
