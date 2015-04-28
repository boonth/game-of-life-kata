"""
Conway's Game of Life

"""

import numpy
import os
import sys


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
        """bounds should have format (<xmin>, <xmax>, <ymin>, <ymax>)"""

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
                neighbors = self.GetNumNeighbors(col, row)

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

    def GetNumNeighbors(self, col, row):
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

    def write(self, output):
        """
        Given an output filename, write the current state of the grid to the
        file. Uses my personal file format.
        
        """

        fout = open(output, 'w')
        fout.write('# grid view bounds, in terms of cell coordinates\n')
        fout.write('# format: <xmin> <xmax> <ymin> <ymax>\n')
        fout.write('%i %i %i %i\n' % (self.xmin,self.xmax,self.ymin,self.ymax))

        fout.write('\n')

        fout.write('# live cells, specified by <column> <row>\n')
        for i in range(self.ncols):
            for j in range(self.nrows):
                if self.field[i][j] == CellGrid.alive:
                    x, y = self.gridToWorld(i, j)
                    fout.write('%i %i\n' % (x, y))

        fout.close()


def main(input, num_generations, output_template):

    bounds, cells = loadMyCellFile(input)
    grid = CellGrid(bounds, cells)

    for gen_num in range(num_generations):

        # figure out filename for output of this generation
        output = getOutputFilename(output_template, gen_num)

        # write current grid to a file
        grid.write(output)
        print 'outputted', output

        # generate the next generation
        grid = grid.tick()

    # write last grid to a file
    output = getOutputFilename(output_template, num_generations)
    grid.write(output)
    print 'outputted', output


def loadMyCellFile(filename):
    """
    Load a cell file in my personal file format

    Returns <bounds>, <cell list>

    bounds -- formatted as (<xmin>, <xmax>, <ymin>, <ymax>)
    cell list -- list of coordinates of live cells
    
    """

    # format: xmin, xmax, ymin, ymax
    bounds = None
    cells = []
    fin = open(filename, 'r')
    for line in fin:
        line2 = line.split()
        if len(line2) == 0 or line2[0][0] == '#':
            continue

        if bounds is None:
            # if haven't read bounds of grid yet, then read it in
            bounds = [int(x) for x in line2]
        else:
            # line specifices location of live cell
            cells.append((int(line2[0]), int(line2[1])))

    fin.close()

    return bounds, cells

def getOutputFilename(template, gen_num):
    """
    Given a filename and a generation number, add the number to the end of
    the filename, but before the extension.
    
    """

    filename, ext = os.path.splitext(template)

    return filename + '.' + str(gen_num) + ext



if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage: <input file> <num generations> <output>'
    else:
        input = sys.argv[1]
        num_generations = int(sys.argv[2])
        output = sys.argv[3]
        main(input, num_generations, output)



