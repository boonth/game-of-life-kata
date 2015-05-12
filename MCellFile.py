"""
Functions to read and write my files in my personal file format

MCell -> My Cell Format

"""

from CellGrid import CellGrid


def load(filename):
    """
    Load a cell file in my personal file format. Returns a CellGrid object.
    
    """

    # format: xmin, xmax, ymin, ymax
    bounds = None
    liveCells = []
    fin = open(filename, 'r')
    for line in fin:
        line2 = line.split()
        if len(line2) == 0 or line2[0][0] == '#':
            continue

        # if haven't read bounds of grid yet, then read it in
        if bounds is None:
            bounds = [int(x) for x in line2]
            continue

        liveCells.append((int(line2[0]), int(line2[1])))

    fin.close()

    return CellGrid(bounds, liveCells)

def write(grid, output):
    """
    Given a grad and an output filename, write the current state of the grid to
    the file. Uses my personal file format.
    
    """

    fout = open(output, 'w')
    fout.write('# grid view bounds, in terms of cell coordinates\n')
    fout.write('# format: <xmin> <xmax> <ymin> <ymax>\n')
    fout.write('%i %i %i %i\n' % (grid.xmin,grid.xmax,grid.ymin,grid.ymax))

    fout.write('\n')

    fout.write('# live cells, specified by <column> <row>\n')
    for i in range(grid.ncols):
        for j in range(grid.nrows):
            if grid.field[i][j] == CellGrid.alive:
                x, y = grid.gridToWorld(i, j)
                fout.write('%i %i\n' % (x, y))

    fout.close()

