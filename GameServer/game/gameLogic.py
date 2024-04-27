from wsClient import WebSocketClient
import asyncio
from sys import stderr
from typing import Type, List
import math
import time
from bottibotto import BottiBotto 
import copy
import random

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
ORANGE = "\033[38;2;255;165;0m"

"""
login / logout
"""

global delta_time
delta_time = 0.0

# Class used for the game logic
class gameLogic:
	# constructor
	def __init__(self, client, gameSet, game, userlist):
		print("======STARTING GAME INITIALIZATION======", file=stderr)
		self.client = client
		self.userlist = userlist
		self.game = game
		self.game["users"] = self.userlist
		self.gameSet = gameSet
		self.players = []
		i = 1
		if gameSet["playeramount"] == 1:
			self.players.append(Player("1", "1", gameSet["planksize"], 1))
			self.players.append(Player("2", "2", gameSet["planksize"], 2))
		else:
			for user in userlist:
				self.players.append(Player(user, user, gameSet["planksize"], i))
				i += 1
		ballWidthX = float(gameSet["ballwidth"])
		if len(self.players) == 2:
			ballWidthX = float(gameSet["ballwidth"]) / 2
		self.ball = Ball(float(gameSet["ballwidth"]), ballWidthX, float(gameSet["Speed"]), float(gameSet["acceleration"]), float(gameSet["playeramount"]) == 1)

		self.print("Game logic set")
	#__init__ end
 
	# start the game
	async def start_game(self):
		if self.gameSet["playeramount"] == 1:
			game_settings = await self.get_game_settings()
			self.bottiBotto = BottiBotto(self, game_settings)
			asyncio.create_task(self.bottiBotto.bottibotto_vit_sa_vie())
		await self.gameInput()
 
	# get game settings for bottibotto
	async def get_game_settings(self):
		return {
			"ball_diameter": self.ball.size,
			"ball_speed": self.ball.speed,
			"ball_acceleration": self.gameSet["acceleration"],
			"ball_dir": self.ball.dir.normalize(),
			"ball_pos": self.ball.pos,
			"paddle_length": self.players[1].plankLength,
			"paddle_speed": self.players[1].speed
		}
	#get_game_settings end
 
	# update the game state for bottibotto
	async def update_state(self):
		self.game_state = {
			"ball_diameter": self.ball.size,
			"ball_speed": self.ball.speed,
			"ball_acceleration": self.gameSet["acceleration"],
			"ball_dir": self.ball.dir.normalize(),
			"ball_pos": self.ball.pos,
			"paddle_length": self.players[1].plankLength,
			"paddle_pos": self.players[1].getPos(),
			"game_over": self.game["state"] == "game_over",
		}
	#update_state end

	# set the paddle movement for bottibotto
	async def set_bottibotto_paddle(self):
		self.players[1].up, self.players[1].down = await self.bottiBotto.get_paddle_movement()
	#set_bottibotto_paddle end
 
	# get the game state for bottibotto
	async def get_game_state(self):
		return copy.deepcopy(self.game_state)
	#get_game_state end

	# print function
	def print(self, msg):
		print(YELLOW, "Game logic :", msg, RESET, file=stderr)
	#print end

	# Get messages from the client
	def getMsgs(self):
		messages = self.client.getMsg()
		if not messages:
			return []
		commands = []
		for msg in messages:
			if len(msg) < 5:
				continue
			# print(msg, file=stderr)
			player_i = -1
			try:
				player_i = int(msg[0])
			except:
				pass
			if player_i > 0 and player_i < 5:
				if msg[1] == "u":
					self.players[player_i - 1].up = msg[4] == "n"
				if msg[1] == "d":
					self.players[player_i - 1].down = msg[4] == "n"
		return commands
	#getMsgs end

	# routine for the game
	async def gameInput(self):
		print(f"""
			Ball speed = {self.ball.speed}
			Ball acceleration = {self.ball.acceleration}
		""",
		file=stderr,
		)
		last_time = time.perf_counter()
		try:
			while True:
				if self.gameSet["playeramount"] == 1:
					await self.update_state()
					await self.set_bottibotto_paddle()
				current_time = time.perf_counter()
				global delta_time
				delta_time = current_time - last_time
				last_time = current_time

				commands = self.getMsgs()
				for command in commands:
					player = self.getPlayer(command["token"])
					if not player:
						continue
					player.move(command.move)
				i = 1
				for player in self.players:
					player.update()
					self.game[f'p{i}'] = self.players[i - 1].plankPos
					i += 1
				self.ball.collide(self.players)
				self.game["ballx"] = self.ball.pos.x
				self.game["bally"] = self.ball.pos.y
				#point scored
				if self.ball.game_over():
					player = self.getPlayer(self.ball.last_touch)
					if player:
						self.game["score" + str(player.num)] += 1
						if self.game["score" + str(player.num)] >= int(self.gameSet["winpoint"]):
							self.game["state"] = "game_over"
							await self.client.sendMsg(self.game)
							await self.sendEndMsg()
							break
					self.ball.reset()
				await self.client.sendMsg(self.game)
				await asyncio.sleep(0.02)

		finally:
			print("GAME INPUT EXITED", file=stderr)
	#gameInput end

	# Get player by token
	def getPlayer(self, token):
		for player in self.players:
			if player.token == token:
				return player
		return 0
	#getPlayer end
	
	async def sendEndMsg(self):
		dico = {}
		j = 1
		for user in self.game["users"]:
			dico[f"user{j}"] = (user, self.game[f"score{j}"])
			j += 1
		dico["gameid"] = self.gameSet["gameid"]
		await self.client.sendEndGame(dico)
#gameLogic end



# Player class
class Player:
	# constructor
	def __init__(self, username: str, token: str, plankLength: float, num: int):
		self.username = username
		self.plankPos = 0
		self.plankLength = plankLength
		self.token = token
		self.offset = 0.49
		self.connected = False
		self.upperBound = 0.5
		self.lowerBound = -0.5
		self.num = num
		self.collision = []
		self.speed = 1
		self.up = False
		self.down = False
	#__init__ end

	# move the plank
	def update(self):
		global delta_time
		if self.up:
			self.plankPos += self.speed * delta_time
		if self.down:
			self.plankPos -= self.speed * delta_time
		self.plankPos = min(self.plankPos, self.upperBound)
		self.plankPos = max(self.plankPos, self.lowerBound)
	#update end

	#get Vector posision of the plank
	def getPos(self):
		if self.num == 1:
			return Vec2(-0.5, self.plankPos)
		if self.num == 2:
			return Vec2(0.5, self.plankPos)
		if self.num == 3:
			return Vec2(self.plankPos, -0.5)
		return Vec2(self.plankPos, 0.5)
	#getPos end
#Player end



# Ball class
class Ball:
	# constructor
	def __init__(self, size: float, size_w: float, speed: float, acceleration: float, is_ai: bool = False):
		self.size = size
		self.acceleration = acceleration
		self.pos = Vec2(0.0, 0.0)
		self.speed = speed
		self.size_w = size_w
		self.init_speed = speed
		if (size != size_w):
			self.dir = random_vector_in_angle_range(2)
		else:
			self.dir = random_vector_in_angle_range(4)
		self.collision_angle = 70
		self.last_touch = ""
		self.temp_last_touch = ""
		self.is_ai = is_ai
	#__init__ end

	# reset the ball
	def reset(self):
		self.pos = Vec2(0.0, 0.0)
		if (self.size != self.size_w):
			self.dir = random_vector_in_angle_range(2)
		else:
			self.dir = random_vector_in_angle_range(4)
		self.temp_last_touch = ""
		self.last_touch = ""
		self.speed = self.init_speed
	#reset end

	# check if the ball is out of bounds
	def game_over(self):
		return ((self.pos.x + self.size_w < -0.5) or (self.pos.x - self.size_w > 0.5)
			or (self.pos.y + self.size < -0.5) or (self.pos.y - self.size > 0.5))
	#game_over end

	# check if the ball collides with a paddle or a wall
	def collide_paddle(self, paddle_x, paddle_y, paddle_len, paddle_dir, is_wall):
		if paddle_dir == "x":  # paddle is like this: --
			if paddle_y > 0:
				paddle_y -= self.size / 2
			else:
				paddle_y += self.size / 2
			collision_pos = project_line(self.pos.y, self.pos.x, self.dir.y, self.dir.x, paddle_y)
			collision_point = Vec2(collision_pos, paddle_y)  # collision position
			if not seg_collide(collision_pos, self.size, paddle_x, paddle_len):
				return -1, 0, 0
			# down, y dir positive
			max_col = paddle_len / 2 + self.size / 2
			new_dir = angle_to_Vec2(-self.collision_angle * (paddle_x - collision_pos) / max_col + 90)
			# up, y dir negative
			if self.dir.y > 0:
				new_dir = angle_to_Vec2(-self.collision_angle * (collision_pos - paddle_x) / max_col + 270)
			if is_wall:
				new_dir = Vec2(self.dir.x, -self.dir.y)
			dist = find_dist(collision_pos, paddle_y, self.pos.x, self.pos.y)
			return dist, new_dir, collision_point
		if paddle_x > 0:
			paddle_x -= self.size_w / 2
		else:
			paddle_x += self.size_w / 2
		# paddle is like this: |
		collision_pos = project_line(self.pos.x, self.pos.y, self.dir.x, self.dir.y, paddle_x)  # find the y coordinate of the intersection point
		collision_point = Vec2(paddle_x, collision_pos)
		if not seg_collide(collision_pos, self.size, paddle_y, paddle_len):  # verify that the y coordinate is on the paddle
			return -1, 0, 0
		# right, x dir positive
		# offset (80) * (paddle_center - contact_point) / paddle_size)
		max_col = paddle_len / 2 + self.size / 2

		new_dir = angle_to_Vec2(180 + (self.collision_angle * (paddle_y - collision_pos) / max_col))
		# left, x dir negative
		if self.dir.x < 0:
			new_dir = angle_to_Vec2(self.collision_angle * (collision_pos - paddle_y) / max_col)
		# dist from ball to paddle
		dist = find_dist(paddle_x, collision_pos, self.pos.x, self.pos.y)
		return dist, new_dir, collision_point
	#collide_paddle end

	# check if the ball collides with a horizontal wall
	def collide_horz_wall(self, paddle_y):
		return self.collide_paddle(-1, paddle_y, 10, "x", True)
	#collide_horz_wall end

	#  set the collision position if the new collision is smaller
	def set_if_smaller(self, newCol, last_touch):
		if newCol[0] != -1 and newCol[0] < self.collision[0]:
			self.collision = newCol
			self.temp_last_touch = last_touch
	#set_if_smaller end

	# check if the ball collides with a vertical wall
	def collide(self, players: List[Player]):
		global delta_time
		remaining_dist = self.speed * delta_time
		self.temp_last_touch = ""
		while remaining_dist > 0:
			self.collision = [math.inf, {}, {}]
			if (self.dir.x > 0 and len(players) > 1):  # moving right, can hit right player (2)
				self.set_if_smaller(
					self.collide_paddle(
						players[1].offset,
						players[1].plankPos,
						players[1].plankLength,
						"y",
						False,
					),
					players[1].token,
				)

			if (self.dir.x < 0 and len(players) > 0):  # moving left, can hit left player (1)
				self.set_if_smaller(
					self.collide_paddle(
						-players[0].offset,
						players[0].plankPos,
						players[0].plankLength,
						"y",
						False,
					),
					players[0].token,
				)

			if self.dir.y > 0:  # moving down, can hit bottom player (4)
				if len(players) > 2:
					self.set_if_smaller(
						self.collide_paddle(
							-players[2].plankPos,
							players[2].offset,
							players[2].plankLength,
							"x",
							False,
						),
						players[3].token,
					)
				else:
					self.set_if_smaller(self.collide_horz_wall(0.5), "")

			if self.dir.y < 0:  # moving up, can hit top player (3)
				if len(players) > 2:
					self.set_if_smaller(
						self.collide_paddle(
							-players[3].plankPos,
							-players[3].offset,
							players[3].plankLength,
							"x",
							False,
						),
						players[2].token,
					)
				else:
					self.set_if_smaller(self.collide_horz_wall(-0.5), "")

			# there is a collision. There can be a new collision
			if self.collision[0] >= 0 and self.collision[0] < remaining_dist:
				self.dir = self.collision[1]
				self.pos = self.collision[2]
				remaining_dist -= self.collision[0]
				if self.temp_last_touch != "":
					self.last_touch = self.temp_last_touch
				max_speed = 4
				if self.is_ai:
					max_speed = 1.8
				if self.speed < max_speed:
					self.speed += self.acceleration
				if self.speed > max_speed:
					self.speed = max_speed
			else:
				# there is no collision within range
				self.pos.x += self.dir.x * remaining_dist
				self.pos.y += self.dir.y * remaining_dist
				remaining_dist = 0
	#collide end
#Ball end


# class used for points and directions (2D vector)
class Vec2:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def normalize(self):
		mag = math.sqrt(self.x ** 2 + self.y ** 2)
		self.x /= mag
		self.y /= mag
		return self
# end of Vec2


# project a line
def project_line(start, end, scale_denom, scale_factor, offset):
	if scale_denom == 0:
		return end
	return (offset - start) / scale_denom * scale_factor + end
#project_line end

# get direction vector from angle
def angle_to_Vec2(angle):
	return Vec2(math.cos(math.radians(angle)), math.sin(math.radians(angle)))
#dir_angle end

# get distance between two points
def find_dist(ax, ay, bx, by):
	return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
#dist end

# check if two segments collide
def seg_collide(pos_seg1, len_seg1, pos_seg2, len_seg2):
	if pos_seg1 > pos_seg2:
		return pos_seg1 - (len_seg1 / 2) < pos_seg2 + (len_seg2 / 2)
	return pos_seg2 - (len_seg2 / 2) < pos_seg1 + (len_seg1 / 2)
#seg_collide end

# generates a random number excluding 0
def random_vector_in_angle_range(nb_players):
    # random choice of side
	if (nb_players == 2):
		if random.choice([True, False]):
			# (1, -1) to (1, 1)
			angle = random.uniform(-math.pi / 4, math.pi / 4)
		else:
			# (-1, -1) to (-1, 1)
			angle = random.uniform(3 * math.pi / 4, 5 * math.pi / 4)
		return Vec2(math.cos(angle), math.sin(angle)).normalize()
	else:
		# (1, -1) to (-1, 1)
		angle = random.uniform(0, 2 * math.pi)
		return Vec2(math.cos(angle), math.sin(angle)).normalize()
#non_zero_uniform end
	