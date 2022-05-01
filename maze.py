from random import sample
from tabnanny import check
from numpy.random import randint
import matplotlib.pyplot as plt


class Maze:
    def __init__(self, WIDTH: int, HEIGHT: int, RESOLUTION: int) -> None:
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.RESOLUTION = RESOLUTION
        self.TOTAL_CELLS = int(WIDTH*HEIGHT/(RESOLUTION**2))
        self.solution = []
        self.str_to_int = {
            'up': 0,
            'right': 1,
            'down': 2,
            'left': 3,
        }
        self.int_to_str = {
            0: 'up',
            1: 'right',
            2: 'down',
            3: 'left',
        }

        walls = {
            'up': {},
            'right': {},
            'down': {},
            'left': {},
        }

        #initially create a grid
        for key in walls.keys():
            for i in range(0,WIDTH,RESOLUTION):
                walls[key][i] = {}
                for j in range(0,HEIGHT, RESOLUTION):
                    walls[key][i][j] = True
        #example walls[direction][xcoord][ycoord] returns a boolean value for the existence of a wall bounding the cell when looking in direction from coordinate xcoord, ycoord (bottom left corner of box)

        
        #had a weird bug with this particular wall
        if walls['right'][0][self.HEIGHT-self.RESOLUTION] == False and walls['left'][self.RESOLUTION][self.HEIGHT-self.RESOLUTION] == True:
            walls['right'][0][self.HEIGHT-self.RESOLUTION] = True
        #algorithm to etch out the walls so that the cells are all accessible and only one path from entrance to exit

        remaining_cells = set()

        visited_cell = {}
        for i in range(0,WIDTH, RESOLUTION):
            visited_cell[i] = {}
            for j in range(0,HEIGHT, RESOLUTION):
                visited_cell[i][j] = 0
                remaining_cells.add((i,j))
        self.visited_cell = visited_cell
        self.remaining_cells = remaining_cells
        self.walls = walls

    def check_if_loop_or_if_add(self, xcoord: int, ycoord: int):

        if self.visited_cell[xcoord][ycoord] == 0:
            #continue searching
            return False, False
        elif self.visited_cell[xcoord][ycoord] == 1:
            #its a loop
            return True, False
        elif self.visited_cell[xcoord][ycoord] == 2:
            #add it!
            return False, True

    def pick_direction(self, prev_direction: int,currx: int, curry: int):
        #NESW convention Up=0, right=1, down=2, left=3
        new_direction = (prev_direction+2)%4
        while new_direction == (prev_direction+2)%4:
            new_direction = randint(0,4)

        if currx == self.WIDTH - self.RESOLUTION:
            #max x can't go right
            if new_direction == 1:
                new_direction = self.pick_direction(new_direction, currx, curry)
        if currx == 0:
            if new_direction == 3:
                new_direction = self.pick_direction(new_direction, currx, curry)

        if curry == self.HEIGHT -self. RESOLUTION :
            if new_direction == 0:
                new_direction = self.pick_direction(new_direction, currx, curry)
        if curry == 0:
            if new_direction == 2:
                new_direction = self.pick_direction(new_direction, currx, curry)
        return new_direction

    def pick_unvisited_cell(self, completedx: int, completedy: int):
        if len(self.remaining_cells) > 0:
            while self.visited_cell[completedx][completedy] != 0:
                completedx, completedy = sample(self.remaining_cells, 1)[0]
        elif len(self.remaining_cells) == 1:
            completedx, completedy = list(self.remaining_cells)[0]

        return completedx, completedy

    def update_coords(self, curr_x: int, curr_y: int, direction: int):
        if direction == 0:
            return curr_x, curr_y+self.RESOLUTION
        elif direction == 1:
            return curr_x+self.RESOLUTION, curr_y
        elif direction == 2:
            return curr_x, curr_y-self.RESOLUTION
        elif direction == 3:
            return curr_x-self.RESOLUTION, curr_y


    def generate_Maze(self):
        #initialize the start and finish as well as the count of visited cells
        self.visited_cell[0][self.HEIGHT-self.RESOLUTION] = 2
        self.remaining_cells.remove((0,self.HEIGHT-self.RESOLUTION))

        #visited_cell[WIDTH-RESOLUTION][0] = 2
        visited_count = 1

        current_x, current_y = 0, self.HEIGHT-self.RESOLUTION

        current_branch_directions = []
        current_branch_coords = []

        current_branch_direction = self.pick_direction(1, current_x, current_y)
        directions = ['up','right','down','left']

        while visited_count < self.TOTAL_CELLS:
            loops_self, add_list = self.check_if_loop_or_if_add(current_x,current_y)

            if add_list: #we have found a loop to the starting branch

                #still need to add the direction to the list and the coordinates to ensure that the walls get removed
                current_branch_coords.append([current_x,current_y])
                current_branch_directions.append(current_branch_direction)

                number_steps = len(current_branch_directions)
                #if number_steps>0:
                    #print('going to remove walls for this list', current_branch_coords)
                #need to add the runninglist to the established set delete the walls and change all the ones to twos in the visited cells info
                prev_direction = None

                
                for index, coordinate_pair in enumerate(current_branch_coords):
                    if prev_direction is not None:
                        #account for the redundancy in the walls data by removing equivalent wall
                        self.walls[directions[(prev_direction+2)%4]][coordinate_pair[0]][coordinate_pair[1]] = False

                    #the current coordinate pair is now established and counted assuming its not already counted
                    if self.visited_cell[coordinate_pair[0]][coordinate_pair[1]] != 2:
                        self.visited_cell[coordinate_pair[0]][coordinate_pair[1]] = 2
                        visited_count += 1
                        self.remaining_cells.remove(tuple(coordinate_pair))


                    
                

                    #the wall to the next pair needs removing (if there is a next pair)
                    if index < number_steps:
                        self.walls[directions[current_branch_directions[index]]][coordinate_pair[0]][coordinate_pair[1]] = False
                        prev_direction = current_branch_directions[index]
                #everything accounted for, let's reset the lists and pick a new starting point
                current_branch_directions = []
                current_branch_coords = []
                current_x, current_y = self.pick_unvisited_cell(current_x, current_y)
                fresh_branch = True
            elif loops_self: #we have looped onto ourself aka this run was garbage
                #need to delete the current loop and try again
                for coordinate_pair in current_branch_coords:
                    self.visited_cell[coordinate_pair[0]][coordinate_pair[1]] = 0
                current_branch_coords = []
                current_branch_directions = []
                current_x, current_y = self.pick_unvisited_cell(current_x,current_y)
                fresh_branch = True
            else: #we can add this cell and continue
                #this cell is unvisited and gets added to the running coordinate and the direction we moved in also gets added
                self.visited_cell[current_x][current_y] = 1
                current_branch_coords.append([current_x,current_y])
                if not fresh_branch:
                    current_branch_directions.append(current_branch_direction)
                fresh_branch = False        
                current_branch_direction = self.pick_direction(current_branch_direction, current_x, current_y)
                current_x, current_y = self.update_coords(current_x, current_y, current_branch_direction)




        #also need the actual entrance and exit too!
        #entrance
        self.walls['up'][0][self.HEIGHT-self.RESOLUTION] = False
        #exit
        self.walls['right'][self.WIDTH-self.RESOLUTION][0] = False

        self.starting_node = [0, self.HEIGHT-self.RESOLUTION]
        self.ending_node = [self.WIDTH-self.RESOLUTION, 0]

    def display_Maze(self):
        if len(self.remaining_cells) >0:
            print('You need to run the generate_Maze method first to create a random maze that isn\'t a grid')
        fig, ax = plt.subplots(figsize = (14,14))

        for i in range(0,self.WIDTH,self.RESOLUTION):
            for j in range(0,self.HEIGHT, self.RESOLUTION):
                if self.walls['down'][i][j]:
                    ax.hlines(j, i,i + self.RESOLUTION)
                if self.walls['left'][i][j]:
                    ax.vlines(i, j, j + self.RESOLUTION)

        #need to plot the upper and right hand side edges
        for i in range(0, self.WIDTH, self.RESOLUTION):
            if self.walls['up'][i][self.HEIGHT-self.RESOLUTION]:
                ax.hlines(self.HEIGHT, i, i+self.RESOLUTION)
        for j in range(0, self.HEIGHT, self.RESOLUTION):
            if self.walls['right'][self.WIDTH-self.RESOLUTION][j]:
                ax.vlines(self.WIDTH, j, j + self.RESOLUTION)
        ax.set_title(f'{self.HEIGHT//self.RESOLUTION} by {self.WIDTH//self.RESOLUTION} Maze')
        plt.show()


    def check_dead_end_or_hits_target(self, current_node: tuple, visited_nodes: set, graph: dict, direction: str, target: tuple):
        '''
        Will check if current node has been reached or is a dead end, if so will return True, and an empty tuple
        '''
        if current_node == target:
            return True, target
        elif current_node in visited_nodes:
            return False, tuple()
        else: 
            #we aren't at the target and we haven't been here before
            #record that have been here
            visited_nodes.add(current_node)
            #check the other directions if they are deadends
            for key in graph.keys():
                if graph[key][current_node[0]][current_node[1]] == False:
                    isnt_dead_end, point = self.check_dead_end_or_hits_target(current_node = self.update_coords(curr_x=current_node[0], curr_y= current_node[1],direction = self.str_to_int[key]), visited_nodes=visited_nodes, graph=graph, direction = key, target = target)
                    if isnt_dead_end:
                        #this branch yielded the solution append the next point in the series and return true 
                        self.solution.append(point)
                        #print(point)
                        return True, current_node

                    else:
                        #this branch is a deadend so "tape it off"
                        #graph[key][current_node[0]][current_node[1]] = True
                        pass
            #if we made it through the loop without making the return statement then it was a deadend
            return False, tuple()

    def solve(self):
        graph = self.walls
        graph['up'][0][self.HEIGHT-self.RESOLUTION] = True
        starting_node = (0, self.HEIGHT-self.RESOLUTION)
        ending_node = (self.WIDTH-self.RESOLUTION, 0)

        solved, useless = self.check_dead_end_or_hits_target(current_node=starting_node, visited_nodes=set(), graph=graph, direction='down', target=ending_node)

        if solved:
            print('Maze is Solved')
            self.solution.append(starting_node)
            self.solution.reverse()
            graph['up'][0][self.HEIGHT-self.RESOLUTION] = False
            #print('Use display_solution method to see the solution to the maze')
        elif not solved:
            print('Maze is not solved')
            print('WARNING: Something went wrong!')
    
    def display_Solution(self):
        #want to redisplay the maze
        if len(self.remaining_cells) >0:
            print('You need to run the generate_Maze method first to create a random maze that isn\'t a grid')
        fig, ax = plt.subplots(figsize = (14,14))

        for i in range(0,self.WIDTH,self.RESOLUTION):
            for j in range(0,self.HEIGHT, self.RESOLUTION):
                if self.walls['down'][i][j]:
                    ax.hlines(j, i,i + self.RESOLUTION)
                if self.walls['left'][i][j]:
                    ax.vlines(i, j, j + self.RESOLUTION)

        #need to plot the upper and right hand side edges
        for i in range(0, self.WIDTH, self.RESOLUTION):
            if self.walls['up'][i][self.HEIGHT-self.RESOLUTION]:
                ax.hlines(self.HEIGHT, i, i+self.RESOLUTION)
        for j in range(0, self.HEIGHT, self.RESOLUTION):
            if self.walls['right'][self.WIDTH-self.RESOLUTION][j]:
                ax.vlines(self.WIDTH, j, j + self.RESOLUTION)


        #now we need to plot the solution pathway
        xvals = [self.RESOLUTION/2]
        yvals = [self.HEIGHT]
        for (xcoord, ycoord) in self.solution:
            xvals.append(xcoord + self.RESOLUTION/2)
            yvals.append(ycoord + self.RESOLUTION/2)
        
        xvals.append(self.WIDTH)
        yvals.append(self.RESOLUTION/2)

        ax.plot(xvals, yvals, 'r-', label = 'Solution')
        ax.set_title(f'Solved {self.HEIGHT//self.RESOLUTION} by {self.WIDTH//self.RESOLUTION} Maze')
        plt.show()
        




        


        


if __name__ == '__main__':
    a = Maze(WIDTH=50, HEIGHT=80, RESOLUTION= 1)
    a.generate_Maze()
    a.display_Maze()
    a.solve()
    a.display_Solution()
