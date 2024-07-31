import argparse
import math
from itertools import combinations

max_drive_mins = 12 * 60
depot_coords = (0,0)

def euclidean_distance(origin, dest):
    origin_x = origin[0]
    origin_y = origin[1]
    dest_x = dest[0]
    dest_y = dest[1]
    return math.sqrt((dest_x - origin_x)**2 + (dest_y - origin_y)**2)

def calculate_route_distance(route):
    total_distance = 0
    current = depot_coords
    for _, pickup, dropoff in route:
        total_distance += euclidean_distance(current, pickup)
        total_distance += euclidean_distance(pickup, dropoff)
        current = dropoff

    total_distance += euclidean_distance(current, depot_coords)

    return total_distance

def compute_savings(loads):
    savings = []
    for (route_one_idx, route1), (route_two_idx, route2) in combinations(enumerate(loads), 2):
        
        route_one_pickup = route1[1]
        route_one_dropoff = route1[2]
        route_two_pickup = route2[1]
        route_two_dropoff = route2[2]
        
        route_one_dist = (
            euclidean_distance(depot_coords, route_one_pickup) +
            euclidean_distance(route_one_dropoff, depot_coords)
        )

        route_two_dist = (
            euclidean_distance(depot_coords, route_two_pickup) +
            euclidean_distance(route_two_dropoff, depot_coords)
        )
        individual_route_total_dist = route_one_dist + route_two_dist

        combined_routes_total_dist = (
            euclidean_distance(route_one_dropoff, route_two_pickup) -
            euclidean_distance(route_one_pickup, route_two_dropoff)
        )

        potential_savings = individual_route_total_dist - combined_routes_total_dist
        
        savings.append((potential_savings, route_one_idx, route_two_idx))
    
    return sorted(savings, reverse=True)

def optimize_routes_by_savings(loads, savings):
    routes = [[load] for load in loads]
    for savings, route_one_idx, route_two_idx in savings:

        route_one = next((route for route in routes if loads[route_one_idx] in route), None)
        route_two = next((route for route in routes if loads[route_two_idx] in route), None)
        
        if route_one != route_two: # avoid combining a route with itself
            combined_route = route_one + route_two
            combined_route_distance = calculate_route_distance(combined_route)

            if combined_route_distance <= max_drive_mins:
                routes.remove(route_one)
                routes.remove(route_two)
                routes.append(combined_route)
    
    return routes

def assign_drivers(loads):
    drivers = []
    combined_route_savings = compute_savings(loads)

    routes = optimize_routes_by_savings(loads, combined_route_savings)
    
    for route in routes:
        drivers.append(route)
    return drivers

def parse_coordinates(coord_str):
    coord_str = coord_str.strip("()")
    x, y = map(float, coord_str.split(","))
    return (x, y)

def parse_loads(path):
    loads = []
    with open(path, 'r') as tsv:
        lines = tsv.readlines()
        for line in lines[1:]:
            parts = line.split()

            load_number = int(parts[0])
            pickup = parse_coordinates(parts[1])
            dropoff = parse_coordinates(parts[2])

            loads.append((load_number, pickup, dropoff))
    return loads
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("problemDir", help="Path to folder containing problems")
    args=parser.parse_args()

    problem_file_path = args.problemDir
    total_loads = parse_loads(problem_file_path)

    drivers = assign_drivers(total_loads)
 
    for i, driver_route in enumerate(drivers):
        print([id for id, pickup, dropoff in driver_route])   
