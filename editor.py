import pygame

import sys, os
import json


AUTO_TILE_MAP = {
	tuple(sorted([(1, 0), (0, 1)])): 0,
	tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
	tuple(sorted([(-1, 0), (0, 1)])): 2,
	tuple(sorted([(0, -1), (0, 1), (1, 0)])): 3,
	tuple(sorted([(-1, 0), (1, 0), (0, -1), (0, 1)])): 4,
	tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 5,
	tuple(sorted([(0, -1), (1, 0)])): 6,
	tuple(sorted([(-1, 0), (1, 0), (0, -1)])): 7,
	tuple(sorted([(-1, 0), (0, -1)])): 8,
}

BASE_IMG_PATH = 'assets/imgs/'
PHYSIC_TILES = ['ground_1/type_1', 'ground_1/type_2', 'ground_2', 'black']
PALLET_TILES = ['pallet']
AUTO_TILE_TYPES = ['ground_1/type_1']

INDEX = 3
RENDER_SCALE = 1.6

def load_img(path):
	img = pygame.image.load(BASE_IMG_PATH + path).convert()
	img.set_colorkey((255, 0, 0))

	return img


def load_imgs(path):
	imgs = []
	for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
		try:
			imgs.append(load_img(path + '/' + img_name))
		except:
			pass

	return imgs



class Map:
	def __init__(self, game, tile_size = 16):
		self.game = game
		self.tile_size = tile_size

		try:
			self.map = self.load('map/' + str(INDEX) + '.json')
		except:
			self.map = {
				'special': [],
				'physic': {},
			}

	def save(self, path):
		f = open(path, 'w')
		json.dump(self.map, f)
		f.close()

	def load(self, path):
		f = open(path, 'r')
		map_data = json.load(f)
		f.close()

		return map_data


	def auto_tile(self, layer, pos, tile_type):

		if(not str(pos[0]) + '; ' + str(pos[1]) in self.map[str(layer)]['grid']):
			return

		area = [pos]
		queue = [pos]
		while(len(queue)):
			top = queue[0]
			queue.pop(0)

			for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
				neighbor = (top[0] + offset[0], top[1] + offset[1])
				if(str(neighbor[0]) + '; ' + str(neighbor[1]) in self.map[str(layer)]['grid']):
					if(self.map[str(layer)]['grid'][str(neighbor[0]) + '; ' + str(neighbor[1])]['type'] == tile_type):
						exits = False
						for x in area:
							if(neighbor[0] == x[0] and neighbor[1] == x[1]):
								exits = True
						if(not exits):
							area.append(neighbor)
							queue.append(neighbor)

		for loc in area:
			tile = self.map[str(layer)]['grid'][str(loc[0]) + '; ' + str(loc[1])]
			neighbors = set()
			for shift in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
				check_loc = str(tile['pos'][0] + shift[0]) + '; ' + str(tile['pos'][1] + shift[1])
				if(check_loc in self.map[str(layer)]['grid']):
					if self.map[str(layer)]['grid'][check_loc]['type'] == tile['type']:
						neighbors.add(shift)
			neighbors = tuple(sorted(neighbors))
			if(tile['type'] in AUTO_TILE_TYPES) and (neighbors in AUTO_TILE_MAP):
				tile['index'] = AUTO_TILE_MAP[neighbors]

	def auto_fill(self, layer, pos, tile_type, index):

		if(str(pos[0]) + '; ' + str(pos[1]) in self.map[str(layer)]['grid']):
			return

		area = [pos]
		queue = [pos]
		while(len(queue)):
			top = queue[0]
			queue.pop(0)

			for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
				neighbor = (top[0] + offset[0], top[1] + offset[1])
				exits = False
				for x in area:
					if(neighbor[0] == x[0] and neighbor[1] == x[1]):
						exits = True
				loc = (str(neighbor[0]) + '; ' + str(neighbor[1]))
				if(loc not in self.map[str(layer)]['grid'] and not exits):
					area.append(neighbor)
					queue.append(neighbor)

		for loc in area:
			self.map[str(layer)]['grid'][str(loc[0]) + '; ' + str(loc[1])] = {'type': tile_type, 'index': index, 'pos': loc}

	def render(self, surf, offset=(0, 0), mode='offgrid grid special physic'):
		data = self.map.copy()

		try:
			for layer in sorted(data):
				if('offgrid' in mode):
					for loc in data[layer]['offgrid']:
						tile = loc
						surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]-offset[0], tile['pos'][1]-offset[1]))

				if('grid' in mode):
					for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
						for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
							loc = str(x) + '; ' + str(y)
							if(loc in data[layer]['grid']):
								tile = data[layer]['grid'][loc]
								surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]*self.tile_size-offset[0], tile['pos'][1]*self.tile_size-offset[1]))
		except:
			pass

			# for loc in self.cmtrees:
			# 	tile = loc
			# 	surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]-offset[0], tile['pos'][1]-offset[1]))

		if('special' in mode):
			for loc in data['special']:
				tile = loc
				surf.blit(self.game.assets[tile['type']][tile['index']], (tile['pos'][0]-offset[0], tile['pos'][1]-offset[1]))

		if('physic' in mode):
			for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
					for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
						loc = str(x) + '; ' + str(y)
						if(loc in data['physic']):
							tile = data['physic'][loc]
							tile_img = self.game.assets['physic'][tile['index']]
							if(mode != 'physic'):
								tile_img.set_alpha(120)
							surf.blit(tile_img, (tile['pos'][0]*self.tile_size-offset[0], tile['pos'][1]*self.tile_size-offset[1]))

class Editor:
	def __init__(self, tile_size=16):
		pygame.init()

		self.screen = pygame.display.set_mode((800, 500))
		self.display = pygame.Surface((480, 300))
		# self.display2 = pygame.Surface((480, 300))

		self.CLOCK = pygame.time.Clock()

		self.assets = {
			'ground_1/type_1': load_imgs('ground_1/type_1'),
			'ground_1/type_2': load_imgs('ground_1/type_2'),
			'ground_2': load_imgs('ground_2'),
			'cmtree': load_imgs('cmtree'),
			'candle': load_imgs('candle'),
			'door': load_imgs('door'),
			'chain': load_imgs('chain'),
			'other': load_imgs('other'),
			'black': load_imgs('black'),
			'pallet': load_imgs('pallet'),
			'physic': load_imgs('physic'),
		}
			# 'player': load_img('player/idle/1.png'),

		
		self.left_clicking = False
		self.right_clicking = False
		self.shift = False
		self.on_grid = True

		self.moverment = [False, False, False, False]
		self.scroll = [0, 0]
		

		self.map = Map(self)

		try:
			self.map.load('map/' + str(INDEX) + '.json')
		except FileNotFoundError:
			pass

		self.tile_size = tile_size
		self.tile_list = list(self.assets)
		self.tile_group = 0
		self.tile_index = 0

		self.mode = ["offgrid grid special physic", "offgrid grid", "offgrid grid special physic", "offgrid grid special", "physic"]
		self.mode_index = 0
		self.layer = 1
		
		self.font = pygame.font.SysFont("lucidasans", 16)

	def create_layer(self, index):
		self.map.map[str(index)] = {
			'grid': {},
			'offgrid': [],
		}

	def run(self):
		while True:
			self.display.fill((25, 90, 200))

			self.layer = max(self.layer, 1)

			self.scroll[0] += (self.moverment[1] - self.moverment[0]) * 2
			self.scroll[1] += (self.moverment[3] - self.moverment[2]) * 2
			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
			self.map.render(self.display, offset=render_scroll, mode=self.mode[self.mode_index])

			current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_index].copy()
			current_tile_img.set_alpha(100)
			self.display.blit(current_tile_img, (16, 5))

			label = self.font.render(str(self.layer), 1, (255, 255, 255))
			self.display.blit(label, (0, 0))

			mouse_pos = pygame.mouse.get_pos()
			mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)
			mouse_rect = pygame.Rect(mouse_pos, (1, 1))

			tile_pos = (int((mouse_pos[0] + self.scroll[0]) // self.tile_size), int((mouse_pos[1] + self.scroll[1]) //self.tile_size))

			if(self.on_grid):
				self.display.blit(current_tile_img, (tile_pos[0] * self.tile_size - self.scroll[0], tile_pos[1] * self.tile_size - self.scroll[1]))
			else:
				self.display.blit(current_tile_img, mouse_pos)

			if(self.left_clicking):
				if(str(self.layer) not in self.map.map):
					self.create_layer(self.layer)

				if(self.tile_list[self.tile_group] == 'physic'):
					ptype = [False, False, False, False, False]
					ptype[self.tile_index] = True
					self.map.map['physic'][str(tile_pos[0]) + '; ' + str(tile_pos[1])] = {'type': ptype, 'index': self.tile_index, 'pos': tile_pos}

				else:
					if(self.on_grid):
						self.map.map[str(self.layer)]['grid'][str(tile_pos[0]) + '; ' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'index': self.tile_index, 'pos': tile_pos}
					else:
						if(self.tile_list[self.tile_group] == 'cmtree'):
							self.map.map['special'].append({'type': self.tile_list[self.tile_group], 'index': self.tile_index, 'pos': (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1])})
						else:
							self.map.map[str(self.layer)]['offgrid'].append({'type': self.tile_list[self.tile_group], 'index': self.tile_index, 'pos': (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1])})

						self.left_clicking = False

			if(self.right_clicking):
				loc = str(tile_pos[0]) + '; ' + str(tile_pos[1])
				if(loc in self.map.map[str(self.layer)]['grid']):
					del self.map.map[str(self.layer)]['grid'][loc]
				
				for tile in self.map.map[str(self.layer)]['offgrid'].copy():
					tile_img = self.assets[tile['type']][tile['index']]
					tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
					if(tile_r.colliderect(mouse_rect)):
						self.map.map[str(self.layer)]['offgrid'].remove(tile)

				for tile in self.map.map[str(self.layer)]['special'].copy():
					tile_img = self.assets[tile['type']][tile['index']]
					tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
					if(tile_r.colliderect(mouse_rect)):
						self.map.map[str(self.layer)]['special'].remove(tile)


			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.left_clicking = True
					if event.button == 3:
						self.right_clicking = True
					if self.shift:
						if event.button == 4:
							self.tile_index = (self.tile_index - 1) % len(self.assets[self.tile_list[self.tile_group]])
						if event.button == 5:
							self.tile_index = (self.tile_index + 1) % len(self.assets[self.tile_list[self.tile_group]])
					else:
						if event.button == 4:
							self.tile_group = (self.tile_group - 1) % len(self.tile_list)
							self.tile_index = 0
						if event.button == 5:
							self.tile_group = (self.tile_group + 1) % len(self.tile_list)
							self.tile_index = 0

				if event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						self.left_clicking = False
					if event.button == 3:
						self.right_clicking = False

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()
					if event.key == pygame.K_a:
						self.moverment[0] = True
					if event.key == pygame.K_d:
						self.moverment[1] = True
					if event.key == pygame.K_w:
						self.moverment[2] = True
					if event.key == pygame.K_s:
						self.moverment[3] = True
					if event.key == pygame.K_LSHIFT:
						self.shift = True
					if event.key == pygame.K_q:
						self.layer -= 1
					if event.key == pygame.K_e:
						self.layer += 1
					if event.key == pygame.K_f:
						self.mode_index = (self.mode_index + 1) % len(self.mode)
					if event.key == pygame.K_g:
						self.on_grid = not self.on_grid
					if event.key == pygame.K_t:
						if(self.tile_list[self.tile_group] in AUTO_TILE_TYPES):
							self.map.auto_tile(self.layer, tile_pos, self.tile_list[self.tile_group])
					if event.key == pygame.K_r:
						self.map.auto_fill(self.layer, tile_pos, self.tile_list[self.tile_group], self.tile_index)
					if event.key == pygame.K_o:
						self.map.save('map/' + str(INDEX) + '.json')

				if event.type == pygame.KEYUP:
					if event.key == pygame.K_a:
						self.moverment[0] = False
					if event.key == pygame.K_d:
						self.moverment[1] = False
					if event.key == pygame.K_w:
						self.moverment[2] = False
					if event.key == pygame.K_s:
						self.moverment[3] = False
					if event.key == pygame.K_LSHIFT:
						self.shift = False
						
			# self.display2.blit(pygame.transform.scale(self.display, (self.display.get_width()*0.5, self.display.get_height()*0.5)), (0, 0))
			self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

			self.CLOCK.tick(60)
			pygame.display.update()

Editor().run()