"""
Conway's Game of Life

Contains logic for producing the next generation.

If executed, will take an initial input file, and output a text file for each
new generation.

usage: <input file> <num generations> <output>

"""

import numpy
import os
import sys

from CellGrid import CellGrid
import MCellFile



def main(input, num_generations, output_template):

    grid = MCellFile.load(input)

    for gen_num in range(num_generations):

        # figure out filename for output of this generation
        output = getOutputFilename(output_template, gen_num)

        # write current grid to a file
        MCellFile.write(grid, output)
        print 'outputted', output

        # generate the next generation
        grid = grid.tick()

    # write last grid to a file
    output = getOutputFilename(output_template, num_generations)
    MCellFile.write(grid, output)
    print 'outputted', output

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



