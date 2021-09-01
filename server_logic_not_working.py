import random;
import math;
from typing import List, Dict;
from collections import namedtuple;
import queue;

Point = namedtuple('Point', ['x', 'y'])
def strpt(pt: Point) -> str: return '[' + str(pt.x) + ',' + str(pt.y) + ']';
# Move = NamedTuple('Move', 'up down left right')

# MAPS/MATRICES
# maps are a group of columns. This way, you can access them like map[x][y] and not map[y][x].
# trying to be memory efficient by making maps global. it looks like it works, but be on the lookout for asynchrony issues.

# more maps can be added
# not totally sure how to allocate the functions of the board without overlap
UNDEFINED = -10;
EMPTY = 0;

danger_map: List[List[int]] = [];
DEATH_BODY_SELF = -4;
DEATH_BODY = -3;
DEATH_HEAD = -2;
DANGER_HEAD = -1;

eat_map: List[List[int]] = [];
FOOD = 10;
KILL_HEAD = 11;

latest_move = 'up';

# main function 
def choose_move(data: dict) -> str:
  update_maps_immediate(data);

  my_head: Point = Point(data['you']['head']['x'], data['you']['head']['y']);
  my_neck: Point = Point(data['you']['body'][1]['x'], data['you']['body'][1]['y']);

  next_heads: List[Point] = neighbors(my_head, data['board']['width'], data['board']['height']);
  print(f'{next_heads} = moves on the board');

  consider = remove_death_moves(next_heads, DEATH_BODY);
  if len(consider): 
    next_heads = consider;
    print(f'{next_heads} = minus death by body');
  consider = remove_death_moves(next_heads, DANGER_HEAD);
  if len(consider): 
    next_heads = consider;
    print(f'{next_heads} = minus danger by head');
  
  if (len(next_heads) > 1):
    consider = remove_traps(my_head, my_neck, next_heads, len(data['you']['body']));
    if len(consider): 
      next_heads = consider;
      print(f'{next_heads} = minus traps');

  if (len(next_heads) > 1):
    consider = encourage_kill(my_head, next_heads);
    if len(consider): 
      next_heads = consider;
      print(f'{next_heads} = minus traps');

  if (len(next_heads) > 1 and data['you']['health'] < 50):
    consider = encourage_food(my_head, next_heads);
    if len(consider): 
      next_heads = consider;
      print(f'{next_heads} = minus traps');

  if (len(next_heads) > 1):
    consider = discourage_edges(next_heads, data['board']['width'], data['board']['height']);
    if len(consider): 
      next_heads = consider;
      print(f'{next_heads} = minus edge discourage');

  
  # TODO: Using information from 'data', make your Battlesnake move towards a piece of food on the board
  
  # possible_moves = go_for_food(data, my_head, possible_moves)

  global latest_move;
#   move = latest_move;
  move = 'right';

  if len(next_heads):
    string_moves: list[str] = list(map(lambda point: to_direction(my_head, point), next_heads));
    print(f'{string_moves} considered')
    # if latest_move not in string_moves:

  move = random.choice(string_moves);
  print(f'{move} returned');
  latest_move = move;
  return move;

# initialize all to -10s at start
def init_maps(data: dict):
  global danger_map;
  global eat_map;
  danger_map = [[UNDEFINED]*data['board']['height'] for i in range(data['board']['width'])];
  eat_map = [[UNDEFINED]*data['board']['height'] for i in range(data['board']['width'])];

# for debugging; print each row to the console
# kinda wacky since maps are a group of columns
def print_map(to_print: List[List[int]]):
  # print rows in descending order (0 is at the bottom of the board)
  for y in reversed(range(len(to_print[0]))): 
    print(format(y, '02d') + '|', end = ' ');
    for x in range(len(to_print)):
      spot = to_print[x][y];
      print(spot if spot != 0 else '__', end = ' ');
    print('')

# wipe matrix between turns
def wipe_map(matrix: List[List[int]]):
  for col in range(len(matrix)):
    for cell in range(len(matrix[0])):
      matrix[col][cell] = EMPTY;


# immediate because that's the only thing the snake cares about rn LOL
# will we do any non-immediate functions? who knows
def update_maps_immediate(data: Dict):
  global danger_map;
  global eat_map;

  wipe_map(danger_map);
  wipe_map(eat_map);

  # remember that it's thinking one move in advance
  # other snake body (not including tail) and head = DEATH_BODY
  for s in data['board']['snakes']: 
    if s['id'] == data['you']['id']:
      continue;
    longer_than_you = s['length'] >= data['you']['length'];
    s_head = Point(s['head']['x'], s['head']['y']);
    head_moves = neighbors(s_head, data['board']['width'], data['board']['height']);
    for head in head_moves:
      if longer_than_you:
        danger_map[head.x][head.y] = DANGER_HEAD;
      else:
        eat_map[head.x][head.y] = KILL_HEAD;
  # snake body will override a head move (good)
    for body_piece in s['body'][:-1]:
      danger_map[body_piece['x']][body_piece['y']] = DEATH_BODY;

  for me_piece in data['you']['body'][:-1]:
    danger_map[me_piece['x']][me_piece['y']] = DEATH_BODY_SELF;

  for f in data['board']['food']:
    eat_map[f['x']][f['y']] = FOOD;
  
  print_map(danger_map)

def up(point: Point) -> Point: return Point(point.x, point.y + 1)
def down(point: Point) -> Point: return Point(point.x, point.y - 1)
def left(point: Point) -> Point: return Point(point.x - 1, point.y)
def right(point: Point) -> Point: return Point(point.x + 1, point.y)

# assumes a and b are right beside each other
def to_direction(point_a: Point, point_b: Point) -> str:
  if point_a.y < point_b.y:
    return 'up'
  elif point_a.y > point_b.y:
    return 'down'
  elif point_a.x > point_b.x:
    return 'left'
  elif point_a.x < point_b.x:
    return 'right'
  else:
    return 'bad point from to_direction'

# 0-4 cardinal neighbors of given coordinate
# does not return out-of-bounds neighbors
def neighbors(point: Point, board_width: int, board_height: int) -> List[Point]:
  out = [];
  if point.y + 1 < board_height:
    out.append(up(point));
  if point.y - 1 >= 0:
    out.append(down(point));
  if point.x - 1 >= 0:
    out.append(left(point));
  if point.x + 1 < board_width:
    out.append(right(point));
  return out;

def remove_death_moves(next_heads: List[Point], death_type: int) -> List[Point]:
  ret: List[Point] = [];
  for nh in next_heads:
    if danger_map[nh.x][nh.y] > death_type:
      ret.append(nh);
  return ret;

def remove_traps(head: Point, neck, next_heads: List[Point], snake_length: int) -> List[Point]:
  ahead_dir: str = to_direction(neck, head);
  behind_dir: str = to_direction(head, neck);
  sides = ['up', 'down', 'left', 'right'];
  if ahead_dir in sides:
    sides.remove(ahead_dir);
  if behind_dir in sides:
    sides.remove(behind_dir);
  side1_dir = sides[0];
  side2_dir = sides[1];

  pt_ahead: Point = globals()[ahead_dir](head);
  pt_s1: Point = globals()[side1_dir](head);
  pt_s2: Point = globals()[side2_dir](head);
  pt_a_s1: Point = globals()[ahead_dir](pt_s1);
  pt_a_s2: Point = globals()[ahead_dir](pt_s1);
  '''
+------+-------+----
|      |  s1   | a_s1  
+------+-------+----
|[][][][][][]< | ahead 
+------+-------+----
|      |  s2   | a_s2  
+------+-------+----
  '''
  space_s1 = 0;
  space_ahead = 0;
  space_s2 = 0;

  # there will be at least 2 and at most 3 next_heads in the list
  if pt_ahead not in next_heads: # side1, side2, or dead
    space_s1 = floodfill_init(pt_s1);
    space_s2 = floodfill_init(pt_s2);
  else:
    space_ahead = floodfill_init(pt_ahead);
    if pt_s1 in next_heads:
      space_s1 = floodfill_init(pt_s1);
    if pt_s2 in next_heads:
      space_s2 = floodfill_init(pt_s2);

  ret: List[Point] = [];
  if space_ahead >= space_s1 and space_ahead >= space_s2:
    ret.append(space_ahead);
  if space_s1 >= space_ahead and space_s1 >= space_s2:
    ret.append(space_s1);
  if space_s2 >= space_s1 and space_s2 >= space_ahead:
    ret.append(space_s2);
    
  return ret;

def floodfill_init(point: Point):
  visited: List[List[bool]] = [[False]*len(danger_map[0]) for i in range(len(danger_map))];
  q = queue.Queue()
  q.put(point);
  visited[point.x][point.y] = True;
  return floodfill(point, q, visited)

def floodfill(point: Point, q, visited: List[List[bool]]):
  total = 0;
  while not q.empty:
    nbrs = neighbors(point, len(visited), len(visited[0]))
    for n in nbrs:
      visited[n.x][n.y] = True;
      if not (visited[n.x][n.y] or danger_map[n.x][n.y] < 0):
        q.put(n);
  print('hi')
  return 1 + floodfill(q.get(), q, visited);


def encourage_food(head, next_heads):
  ret: List[Point] = [];
  for nh in next_heads:
    if eat_map[nh.x][nh.y] == FOOD:
      ret.append(nh);
  return ret;

def encourage_kill(head, next_heads):
  ret: List[Point] = [];
  for nh in next_heads:
    if eat_map[nh.x][nh.y] == KILL_HEAD:
      ret.append(nh);
  return ret;

def discourage_edges(next_heads: List[Point], board_width, board_height) -> List[Point]:
  ret: List[Point] = [];
  for nh in next_heads:
    if nh.x != 0 and nh.y != 0 and nh.x != board_width - 1 and nh.y != board_height - 1:
      ret.append(nh);
  return ret;


def go_for_food(data: dict, my_head: Dict[str, int], possible_moves: List[str]) -> List[str]:
  
#   food_distance_list = [];
  foods = data["board"]["food"]

  if "left" in possible_moves and len(possible_moves) > 1:
    if foods[0]["x"] > my_head["x"]:
      possible_moves.remove("left")

  if "right" in possible_moves and len(possible_moves) > 1:
    if foods[0]["x"] <= my_head["x"]:
      possible_moves.remove("right")

  if "down" in possible_moves and len(possible_moves) > 1:
    if foods[0]["y"] > my_head["y"]:
      possible_moves.remove("down")

  if "up" in possible_moves and len(possible_moves) > 1:
    if foods[0]["y"] <= my_head["y"]:
      possible_moves.remove("up")
  
  return possible_moves
