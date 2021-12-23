import time
import random
import pygame


class Spot:
    def __init__(self, x=0, y=0, _color=(100, 171, 70)):
        self.x = x
        self.y = y
        self.color = _color

        self.g_score = 0
        self.h_score = 0
        self.f_score = 0

        self.previous = None

    def get_coord(self):
        return self.x, self.y

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def __eq__(self, other):
        return isinstance(other, Spot) and (other.x == self.x and other.y == self.y)

    def __ne__(self, other):
        return not (isinstance(other, Spot)) or (other.x != self.x or other.y != self.y)


class Game:
    BG_COLOR = (94, 91, 91)
    SNAKE_COLOR = (100, 171, 70)
    SNAKE_BORDER_COLOR = BG_COLOR
    SNAKE_FOOD_COLOR = (224, 93, 79)
    SNAKE_FOOD_BORDER_COLOR = SNAKE_BORDER_COLOR
    A_STAR_COLOR = (63, 101, 204)
    UNIFORM_COST_COLOR = (153, 101, 204)
    SNAKE_INITIAL_POS = [0, 0]
    GAME_OVER_FONT_COLOR = (255, 255, 255)
    RED = (255, 0, 0)
    FPS = 11

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('FreeSansBold.ttf', 24)
        self.display = pygame.display.set_mode((700, 600))
        self.display.fill(self.BG_COLOR)
        self.display_border = pygame.draw.rect(self.display, (255, 255, 255), [0, 0, 700, 600], 1)

        self.snake_body_array = [self.SNAKE_INITIAL_POS]
        self.head_of_snake_x = self.snake_body_array[0][0]
        self.head_of_snake_y = self.snake_body_array[0][1]
        self.food_pos = self.get_random_food_pos()

        self.running = True
        self.score = 0
        self.snake_len = 0
        self.lost = False
        self.choice_made = True
        self.a_star_enable = False
        self.uniform_cost_enable = False

        self.max_expanded_nodes_bf = 0
        self.max_expanded_nodes_uc = 0

    def enable_uniform_cost(self):
        self.uniform_cost_enable = True

    def draw_spot(self, spot):
        pygame.draw.rect(self.display, spot.color, [spot.x, spot.y, 19, 19])
        pygame.draw.rect(self.display, self.SNAKE_BORDER_COLOR, [spot.x, spot.y, 20, 20], 1)

    def draw_snake(self):
        for x, y in self.snake_body_array:
            pygame.draw.rect(self.display, self.SNAKE_COLOR, [x, y, 19, 19], 0)
            pygame.draw.rect(self.display, self.SNAKE_BORDER_COLOR, [x, y, 20, 20], 1)

    def get_random_food_pos(self):
        food_x_pos = random.randint(0, 680)
        food_y_pos = random.randint(0, 580)

        while ([food_x_pos, food_y_pos] in self.snake_body_array) or (food_x_pos % 19 != 0) or (food_y_pos % 19 != 0):
            food_x_pos = random.randint(0, 680)
            food_y_pos = random.randint(0, 580)

        return [food_x_pos, food_y_pos]

    def game_over(self):
        game_over_text = self.font.render("GAME OVER!", True, self.GAME_OVER_FONT_COLOR)
        restart_text = self.font.render("Press SPACE to Restart", True, self.GAME_OVER_FONT_COLOR)
        text_rect = game_over_text.get_rect()
        text_rect.center = (350, 300)
        self.display.blit(game_over_text, text_rect)
        text_rect = restart_text.get_rect()
        text_rect.center = (350, 340)
        self.display.blit(restart_text, text_rect)

    def display_score(self):
        score_text = self.font.render("Score: " + str(self.score), True, self.GAME_OVER_FONT_COLOR)
        text_rect = score_text.get_rect()
        text_rect.center = (610, 40)
        self.display.blit(score_text, text_rect)

    @staticmethod
    def valid_places_to_go_a_star(current_spot_pos, obstacle_list):
        valid_places = []

        right_of_curr_coord = [current_spot_pos[0] + 19, current_spot_pos[1]]
        left_of_curr_coord = [current_spot_pos[0] - 19, current_spot_pos[1]]
        top_of_curr_coord = [current_spot_pos[0], current_spot_pos[1] - 19]
        bottom_of_curr_coord = [current_spot_pos[0], current_spot_pos[1] + 19]

        if (left_of_curr_coord not in obstacle_list) \
                and (left_of_curr_coord[0] >= 0) and (left_of_curr_coord[0] <= 680) and (left_of_curr_coord[1] >= 0) \
                and (left_of_curr_coord[1] <= 580):
            valid_places.append(Spot(left_of_curr_coord[0], left_of_curr_coord[1]))

        if (right_of_curr_coord not in obstacle_list) \
                and (right_of_curr_coord[0] >= 0) and (right_of_curr_coord[0] <= 680) and (
                right_of_curr_coord[1] >= 0) \
                and (right_of_curr_coord[1] <= 580):
            valid_places.append(Spot(right_of_curr_coord[0], right_of_curr_coord[1]))

        if (top_of_curr_coord not in obstacle_list) \
                and (top_of_curr_coord[0] >= 0) and (top_of_curr_coord[0] <= 680) and (top_of_curr_coord[1] >= 0) \
                and (top_of_curr_coord[1] <= 580):
            valid_places.append(Spot(top_of_curr_coord[0], top_of_curr_coord[1]))

        if (bottom_of_curr_coord not in obstacle_list) \
                and (bottom_of_curr_coord[0] >= 0) and (bottom_of_curr_coord[0] <= 680) and (
                bottom_of_curr_coord[1] >= 0) \
                and (bottom_of_curr_coord[1] <= 580):
            valid_places.append(Spot(bottom_of_curr_coord[0], bottom_of_curr_coord[1]))
        return valid_places

    @staticmethod
    def manhattan_distance(start, end):
        return abs(start.x - end.x) + abs(start.y - end.y)

    @staticmethod
    def pick_random_valid_place(valid_places):
        try:
            random_idx = random.randint(1, len(valid_places))
            return valid_places[random_idx - 1]
        except (IndexError, ValueError):
            return None

    @staticmethod
    def best_first_search(spot):
        return spot.g_score + spot.h_score

    @staticmethod
    def uniform_cost_search(spot):
        return spot.g_score

    def find_a_star_path(self, open_list, closed_list, path, start_spot, end_spot, func, _color=None):
        goal_reached = False

        while not goal_reached:
            if len(open_list) != 0:
                sorted_open_list_spots_f_scores = sorted(open_list, key=lambda n: n.f_score)
                q = sorted_open_list_spots_f_scores[0]
                open_list.remove(q)

                valid_places = self.valid_places_to_go_a_star((q.x, q.y), self.snake_body_array)
                for neighbor in valid_places:
                    if neighbor == end_spot:
                        neighbor.previous = q
                        temp = neighbor
                        while temp.previous is not None:
                            path.append(temp.previous)
                            temp = temp.previous
                        goal_reached = True

                    else:
                        neighbor.g_score = q.g_score + 1
                        neighbor.h_score = self.manhattan_distance(neighbor, end_spot)
                        neighbor.f_score = func(neighbor)
                        neighbor.previous = q

                        if neighbor in open_list:
                            index = open_list.index(neighbor)
                            if open_list[index].f_score < neighbor.f_score:
                                continue

                        elif neighbor in closed_list:
                            index = closed_list.index(neighbor)
                            if closed_list[index].f_score < neighbor.f_score:
                                continue

                        else:
                            open_list.append(neighbor)

                if q not in closed_list:
                    closed_list.append(q)

            else:
                raise IndexError

        if _color:
            for p in path:
                if p is not start_spot:
                    self.draw_spot(Spot(p.x, p.y, _color=_color))

    def run(self):
        snake_block_left = False
        snake_block_right = False
        snake_block_bottom = False
        snake_block_top = False

        head_x_change = 0
        head_y_change = 0

        while self.running:
            previous_head_pos_x = self.head_of_snake_x
            previous_head_pos_y = self.head_of_snake_y

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if not self.lost:
                    if event.type == pygame.KEYDOWN:
                        if self.a_star_enable is False:
                            if event.key == pygame.K_DOWN:
                                if not snake_block_bottom:
                                    head_y_change = 19
                                    head_x_change = 0
                            elif event.key == pygame.K_UP:
                                if not snake_block_top:
                                    head_y_change = -19
                                    head_x_change = 0
                            elif event.key == pygame.K_RIGHT:
                                if not snake_block_right:
                                    head_x_change = 19
                                    head_y_change = 0
                            elif event.key == pygame.K_LEFT:
                                if not snake_block_left:
                                    head_x_change = -19
                                    head_y_change = 0
                        if event.key == pygame.K_a:
                            self.a_star_enable = not self.a_star_enable
                            head_x_change = 0
                            head_y_change = 0
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.lost = False
                            self.choice_made = True
                            self.snake_body_array.clear()
                            self.snake_body_array.append(self.SNAKE_INITIAL_POS)
                            self.snake_len = 0
                            self.score = 0
                            self.head_of_snake_x = 0
                            self.head_of_snake_y = 0
                            head_x_change = 0
                            head_y_change = 0
                            previous_head_pos_x = 0
                            previous_head_pos_y = 0
                            snake_block_left = False
                            snake_block_right = False
                            snake_block_bottom = False
                            snake_block_top = False

            if self.choice_made:
                self.display.fill(self.BG_COLOR)

                if self.a_star_enable is True:
                    open_list = [Spot(self.head_of_snake_x, self.head_of_snake_y)]
                    closed_list = []
                    path = []
                    start_spot = open_list[0]
                    end_spot = Spot(self.food_pos[0], self.food_pos[1])

                    open_list_uc = [Spot(self.head_of_snake_x, self.head_of_snake_y)]
                    closed_list_uc = []
                    path_uc = []
                    elapsed_time_uc = None

                    if self.uniform_cost_enable:
                        try:
                            t = time.process_time()
                            self.find_a_star_path(
                                open_list_uc,
                                closed_list_uc,
                                path_uc,
                                start_spot,
                                end_spot,
                                self.uniform_cost_search,
                            )
                            elapsed_time_uc = time.process_time() - t
                        except (IndexError, AttributeError):
                            print('Uniform cost search failed')

                    try:
                        t = time.process_time()
                        self.find_a_star_path(
                            open_list,
                            closed_list,
                            path,
                            start_spot,
                            end_spot,
                            self.best_first_search,
                            self.A_STAR_COLOR
                        )
                        elapsed_time = time.process_time() - t

                        if self.uniform_cost_enable is False:
                            if len(closed_list) > self.max_expanded_nodes_bf:
                                self.max_expanded_nodes_bf = len(closed_list)
                                print(f'Expanded nodes: {self.max_expanded_nodes_bf} ({elapsed_time})')
                                print(f'Snake length: {self.snake_len + 1}')
                        else:
                            expanded_bf = len(closed_list)
                            expanded_uc = len(closed_list_uc)
                            display = False

                            if expanded_bf > self.max_expanded_nodes_bf:
                                display = True
                                self.max_expanded_nodes_bf = expanded_bf

                            if expanded_uc > self.max_expanded_nodes_uc:
                                display = True
                                self.max_expanded_nodes_uc = expanded_uc

                            if display is True:
                                print(
                                    f'Expanded nodes (A*): {self.max_expanded_nodes_bf} ({elapsed_time})'
                                )
                                print(
                                    f'Expanded nodes (Uniform Cost): {self.max_expanded_nodes_uc} ({elapsed_time_uc})'
                                )
                                print(f'Snake length: {self.snake_len + 1}')

                        try:
                            self.head_of_snake_x = path[-2].x
                            self.head_of_snake_y = path[-2].y

                        except IndexError:
                            self.head_of_snake_x = self.food_pos[0]
                            self.head_of_snake_y = self.food_pos[1]

                    except IndexError:
                        try:
                            valid_places = self.valid_places_to_go_a_star(
                                [self.head_of_snake_x, self.head_of_snake_y],
                                self.snake_body_array
                            )
                            rand_place = self.pick_random_valid_place(valid_places)
                            try:
                                self.head_of_snake_x = rand_place.x
                                self.head_of_snake_y = rand_place.y
                            except AttributeError:
                                self.lost = True
                                self.choice_made = False
                                self.a_star_enable = False
                                self.game_over()
                        except IndexError:
                            self.lost = True
                            self.choice_made = False
                            self.a_star_enable = False
                            self.game_over()

                else:
                    self.head_of_snake_x += head_x_change
                    self.head_of_snake_y += head_y_change

                self.snake_body_array[0][0] = self.head_of_snake_x
                self.snake_body_array[0][1] = self.head_of_snake_y

                self.draw_snake()
                self.display_score()

                pygame.draw.rect(
                    self.display,
                    self.SNAKE_FOOD_COLOR,
                    [self.food_pos[0], self.food_pos[1], 19, 19],
                    0
                )
                pygame.draw.rect(
                    self.display,
                    self.SNAKE_FOOD_BORDER_COLOR,
                    [self.food_pos[0], self.food_pos[1], 20, 20],
                    1
                )

                if self.food_pos == [self.head_of_snake_x, self.head_of_snake_y]:
                    self.snake_len += 1
                    self.score += 10
                    self.snake_body_array.append([previous_head_pos_x, previous_head_pos_y])
                    self.food_pos = self.get_random_food_pos()

                for j in range(1, len(self.snake_body_array)):
                    self.snake_body_array[j][0] = self.snake_body_array[j - self.snake_len][0]
                    self.snake_body_array[j][1] = self.snake_body_array[j - self.snake_len][1]

                if self.snake_len >= 1:
                    if self.head_of_snake_x > previous_head_pos_x and self.head_of_snake_y == previous_head_pos_y:
                        snake_block_left = True
                        snake_block_right = False
                        snake_block_top = False
                        snake_block_bottom = False
                    elif self.head_of_snake_x < previous_head_pos_x and self.head_of_snake_y == previous_head_pos_y:
                        snake_block_left = False
                        snake_block_right = True
                        snake_block_top = False
                        snake_block_bottom = False
                    elif self.head_of_snake_y > previous_head_pos_y and self.head_of_snake_x == previous_head_pos_x:
                        snake_block_left = False
                        snake_block_right = False
                        snake_block_top = True
                        snake_block_bottom = False
                    elif self.head_of_snake_y < previous_head_pos_y and self.head_of_snake_x == previous_head_pos_x:
                        snake_block_left = False
                        snake_block_right = False
                        snake_block_top = False
                        snake_block_bottom = True

                    if [self.head_of_snake_x, self.head_of_snake_y] in self.snake_body_array[1:-1]:
                        if not (head_x_change == 0 and head_y_change == 0):
                            print("Cause of Death: Self-Collision")
                            self.lost = True
                            self.choice_made = False
                            self.game_over()

                if not ((0 <= self.head_of_snake_x <= 679) and (0 <= self.head_of_snake_y <= 579)):
                    print("Cause of Death: Boundary Collision")
                    self.lost = True
                    self.choice_made = False
                    self.game_over()

            pygame.display.update()
            self.clock.tick(self.FPS)



