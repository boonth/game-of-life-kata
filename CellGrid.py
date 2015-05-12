"""
A class representing a grid of cells. Cells are either dead or alive. Used for
Conway's Game of Life.

"""

import numpy

class CellGrid:
    """
    A grid of cells

    (0, 0) is lower left. First index is column location, second is row.

    world coordinates: cell coordinates based on xmin, xmax, ymin, ymax
    grid coordinates: cell coordinates where lower left cell is (0, 0)

    """

    # possible states of each cell
    dead = 0
    alive = 1

    def __init__(self, bounds, liveCells=None):
        """
        bounds should have format (<xmin>, <xmax>, <ymin>, <ymax>).
        liveCells is a list of tuples of cell coordinates (col, row) in world
        coordinates.
        
        """

        self.xmin = bounds[0]
        self.xmax = bounds[1]
        self.ymin = bounds[2]
        self.ymax = bounds[3]
        self.ncols = bounds[1] - bounds[0] + 1
        self.nrows = bounds[3] - bounds[2] + 1

        # create a representation of the grid as an array of ints,
        # array index is [col][row]
        # turn all cells off
        self.field = numpy.zeros((self.ncols, self.nrows), dtype='int')
        for x in range(self.xmin, self.xmax):
            for y in range(self.ymin, self.ymax):
                self.cellOff(x, y)

        # if any cells were given, bring them to life
        if liveCells is not None:
            for cell in liveCells:
                x, y = cell
                self.cellOn(x, y)

    def worldToGrid(self, col, row):
        """
        Given coordinates in world coordinates, return coordinates in grid
        coordinates
        
        """

        return col - self.xmin, row - self.ymin

    def gridToWorld(self, col, row):
        """
        Given coordinates in grid coordinates, return coordinates in world
        coordinates
        
        """

        return col + self.xmin, row + self.ymin

    def cellOn(self, col, row):
        """
        Make the cell at the given location alive.  Takes world coordinates.
        
        """

        i, j = self.worldToGrid(col, row)
        self.field[i][j] = CellGrid.alive

    def cellOff(self, col, row):
        """
        Make the cell at the given location dead.  Takes world coordinates.
        
        """

        i, j = self.worldToGrid(col, row)
        self.field[i][j] = CellGrid.dead

    def tick(self):
        """Create the next generation. Returns a CellGrid."""

        # create a new grid with the same bounds
        bounds = (self.xmin, self.xmax, self.ymin, self.ymax)
        newgrid = CellGrid(bounds)

        # populate new grid
        for col in range(self.ncols):
            for row in range(self.nrows):

                # get number of live neighbors to this cell
                neighbors = self.getNumNeighbors(col, row)

                # check the rules
                if self.field[col][row] == CellGrid.alive:
                    if neighbors < 2:
                        x, y = self.gridToWorld(col, row)
                        newgrid.cellOff(x, y)
                    elif neighbors >= 2 and neighbors <= 3:
                        x, y = self.gridToWorld(col, row)
                        newgrid.cellOn(x, y)
                    elif neighbors > 3:
                        x, y = self.gridToWorld(col, row)
                        newgrid.cellOff(x, y)
                else:
                    # cell is currently dead
                    if neighbors == 3:
                        x, y = self.gridToWorld(col, row)
                        newgrid.cellOn(x, y)

        return newgrid

    def getNumNeighbors(self, col, row):
        """
        Given the coordinates of a cell in grid space, return the number of
        alive neighbors of that cell.

        """

        neighbors = 0
        displacement = [-1, 0, 1]
        for i in displacement:
            for j in displacement:
                if i == 0 and j == 0:
                    continue

                col2 = col + i
                row2 = row + j
                if col2 >= 0 and col2 < self.ncols:
                    if row2 >= 0 and row2 < self.nrows:
                        if self.field[col2][row2] == CellGrid.alive:
                            neighbors += 1
        return neighbors

    def getLiveCells(self):
        """
        Return all live cells as a list of cell coordinates in world
        coordinates.

        """

        liveCells = []
        for col in range(self.ncols):
            for row in range(self.nrows):
                if self.field[col][row] == CellGrid.alive:
                    liveCells.append(self.gridToWorld(col, row))

        return liveCells

    def printField(self):
        """
        Print out the field. At each location, prints the number of mines
        neighboring it. If a location has a mine, a '*' is printed instead.
        
        """
        
        for row in range(self.nrows):
            s = ''    # string representing the row
            for col in range(self.ncols):
                if self.field[row][col] == CellGrid.mine:
                    s += '*'
                else:
                    s += str(self.field[row][col])
                s += ' '

            # make sure to remove the rightmost space before printing
            print s.rstrip()
