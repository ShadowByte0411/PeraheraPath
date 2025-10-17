import json
import math
import heapq
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# REAL-WORLD COST PARAMETERS
FUEL_PRICE_PER_LITER_LKR = 375.00
AVG_VEHICLE_EFFICIENCY_KMPL = 12.0
AVG_SPEED_NORMAL_KMH = 60.0
AVG_SPEED_MEDIUM_KMH = 40.0
AVG_SPEED_HIGH_KMH = 20.0
AVG_SPEED_VERY_HIGH_KMH = 10.0
ROAD_CLOSURE_PENALTY_HOURS = 100.0

# FLASK APP INITIALIZATION
app = Flask(__name__)

# DATA LOADING
with open('data.json', 'r', encoding='utf-8') as f:
    DB = json.load(f)

# Pre-process connections into a graph for fast lookups.
GRAPH = {}
for conn in DB['connections']:
    if conn['from'] not in GRAPH: GRAPH[conn['from']] = []
    GRAPH[conn['from']].append(conn)
    if conn['to'] not in GRAPH: GRAPH[conn['to']] = []
    reverse_conn = {**conn, 'from': conn['to'], 'to': conn['from']}
    GRAPH[conn['to']].append(reverse_conn)

# HELPER FUNCTIONS
def get_speed(congestion_level):
    if congestion_level == 'very_high': return AVG_SPEED_VERY_HIGH_KMH
    if congestion_level == 'high': return AVG_SPEED_HIGH_KMH
    if congestion_level == 'medium': return AVG_SPEED_MEDIUM_KMH
    return AVG_SPEED_NORMAL_KMH

def parse_datetime_str(datetime_obj):
    try:
        return datetime_obj.strftime('%B').lower(), datetime_obj.day, datetime_obj.strftime('%H:%M')
    except (ValueError, AttributeError):
        return None, None, None


def get_city_event(city, month, day):
    for festival in DB['festivals']:
        date_range = festival.get('date_range', '0-0').split('-')
        if (festival['city'] == city and
                festival['month'] == month and
                int(date_range[0]) <= day <= int(date_range[1])):
            return festival
    return None

def is_city_closed(city, event_name, time_str):
    if not event_name: return False
    for closure in DB.get('road_closures', []):
        closure_city = DB['road_to_city_mapping'].get(closure['road'])
        if closure_city == city and closure['event'] == event_name:
            start_time, end_time = [datetime.strptime(t, '%H:%M').time() for t in closure['time'].split('-')]
            current_time = datetime.strptime(time_str, '%H:%M').time()
            if start_time <= current_time <= (datetime.strptime('23:59', '%H:%M').time() if end_time.hour == 0 else end_time):
                return True
    return False

# CORE A* PATHFINDING LOGIC
def heuristic(city_a, city_b):
    coords_a, coords_b = DB['coordinates'].get(city_a), DB['coordinates'].get(city_b)
    if not coords_a or not coords_b: return 1.0
    distance_km = math.sqrt((coords_b[0] - coords_a[0])**2 + (coords_b[1] - coords_a[1])**2) * 111
    return distance_km / AVG_SPEED_NORMAL_KMH

def a_star_search(start, goal, travel_datetime_obj):
    month, day, time_str = parse_datetime_str(travel_datetime_obj)
    if not month: return None, {"displayName": "Invalid date/time object."}

    active_event_obj = get_city_event(goal, month, day)
    active_event_name = active_event_obj['name'] if active_event_obj else None
    
    open_set, closed_set = [(heuristic(start, goal), 0.0, start, [start])], set()

    while open_set:
        _f, g_cost_time, current_city, path = heapq.heappop(open_set)
        if current_city == goal: return path, active_event_obj
        if current_city in closed_set: continue
        closed_set.add(current_city)

        for conn in GRAPH.get(current_city, []):
            neighbor_city = conn['to']
            if neighbor_city in closed_set: continue
            
            congestion = conn['normal_congestion']
            if active_event_name and any(f['name'] == active_event_name and f['impact'] == 'high' and f['city'] in [current_city, neighbor_city] for f in DB['festivals']):
                congestion = conn.get('festival_congestion', congestion)
            
            speed_kmh = get_speed(congestion)
            step_time_hours = conn['distance'] / speed_kmh
            
            if is_city_closed(current_city, active_event_name, time_str) or is_city_closed(neighbor_city, active_event_name, time_str):
                step_time_hours += ROAD_CLOSURE_PENALTY_HOURS
            
            new_g_cost_time = g_cost_time + step_time_hours
            heapq.heappush(open_set, (new_g_cost_time + heuristic(neighbor_city, goal), new_g_cost_time, neighbor_city, path + [neighbor_city]))
    return None, None

# WARNING & COST FUNCTIONS
def get_route_warnings(path, event_obj, travel_datetime_obj):
    warnings = []
    if not event_obj: return warnings
    month, day, time_str = parse_datetime_str(travel_datetime_obj)
    event_name = event_obj['name']
    for city in set(path):
        if is_city_closed(city, event_name, time_str):
            warnings.append(f"Warning: Road closures expected in {city.title()} for the {event_obj['displayName']}.")
    return warnings

def calculate_final_costs(path, event_obj):
    total_distance_km, total_time_hours = 0, 0
    active_event_name = event_obj['name'] if event_obj else None

    for i in range(len(path) - 1):
        city_a, city_b = path[i], path[i+1]
        conn = next((c for c in GRAPH.get(city_a, []) if c['to'] == city_b), None)
        if not conn: continue

        total_distance_km += conn['distance']
    
        congestion = conn['normal_congestion']
        if active_event_name and any(f['name'] == active_event_name and f['impact'] == 'high' and f['city'] in [city_a, city_b] for f in DB['festivals']):
            congestion = conn.get('festival_congestion', congestion)
        
        speed = get_speed(congestion)
        total_time_hours += conn['distance'] / speed
        
    fuel_cost_lkr = (total_distance_km / AVG_VEHICLE_EFFICIENCY_KMPL) * FUEL_PRICE_PER_LITER_LKR
    return total_time_hours, total_distance_km, fuel_cost_lkr

# API ENDPOINTS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cities')
def get_cities():
    return jsonify(sorted(list(DB['coordinates'].keys())))

@app.route('/api/route', methods=['POST'])
def find_route():
    data = request.json
    start_city = data.get('start', '').lower()
    goal_city = data.get('goal', '').lower()
    datetime_str_raw = data.get('datetime', '') 
    if not all([start_city, goal_city, datetime_str_raw]):
        return jsonify({'error': "Missing start, goal, or date."}), 400
    if start_city not in DB['coordinates'] or goal_city not in DB['coordinates']:
        return jsonify({'error': "One of the cities is not recognized."}), 400

    try:
        dt_obj = datetime.strptime(datetime_str_raw, '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({'error': "Invalid date format received. Expected YYYY-MM-DD HH:MM."}), 400
       
    path, event_obj = a_star_search(start_city, goal_city, dt_obj) 
    if not path:
        return jsonify({'error': "No route could be found."}), 404

    message = f"Event detected: {event_obj['displayName']}" if event_obj else "No festival event detected."
    time, distance, fuel = calculate_final_costs(path, event_obj)
    warnings = get_route_warnings(path, event_obj, dt_obj) # Pass the object
    
    return jsonify({
        'path': path, 'message': message, 'warnings': warnings,
        'coordinates': [DB['coordinates'].get(city) for city in path if DB['coordinates'].get(city)],
        'costs': {
            'time_hours': time,
            'distance_km': round(distance, 2),
            'fuel_lkr': round(fuel, 2)
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
