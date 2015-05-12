"""
Functions to read and write files in Golly's extended RLE file format.

"""

from CellGrid import CellGrid

def load(filename):
    """Load a file in the extended RLE file format as used by Golly"""

    # format: xmin, xmax, ymin, ymax
    liveCells = []
    upper_left = [0, 0]
    width = 0
    height = 0

    fin = open(filename, 'r')

    # find any special comments, and get the width and height
    for line in fin:
        line2 = line.split()
        if len(line2) == 0:
            continue

        if line2[0][0] == '#':
            # check for special keywords
            if line2[0] == '#CXRLE':
                # the line contains key value pairs, separated by spaces
                pairs = line.split(' ')[1:]

                # each key-value pair is separated by an '='
                for pair in pairs:
                    key, value = pair.split('=')
                    if key == 'Pos':
                        upper_left = [int(x) for x in value.split(',')]
            continue

        # the first non-comment line is a header line, read it, then break
        header_parts = line.split(',')
        xpart = header_parts[0]
        ypart = header_parts[1]
        rule = ','.join(header_parts[2:])
        width = int(xpart.split('=')[1])
        height = int(ypart.split('=')[1])
        first_line_found = True
        break

    # start at the upper left cell
    x = upper_left[0]
    y = upper_left[1]

    # loop over the remaining part of the file to find alive cells
    multiplier = 1
    for line in fin:
        line2 = line.split()
        if len(line2) == 0 or line2[0][0] == '#':
            continue

        # step through each char of the line
        line = line.strip()
        i = 0
        while i < len(line):
            if line[i].isdigit():
                # read in a multiplier
                n = line[i]
                i = i + 1
                while i < len(line) and line[i].isdigit():
                    n = n + line[i]
                    i = i + 1
                multiplier = int(n)
                if i >= len(line):
                    continue
            if line[i] == '.' or line[i] == 'b':
                # a dead cell 
                for _ in range(multiplier):
                    x += 1
                multiplier = 1
                i += 1
                if i >= len(line):
                    continue
            if line[i] == 'A' or line[i] == 'o':
                # a live cell
                for _ in range(multiplier):
                    liveCells.append((x, y))
                    x += 1
                multiplier = 1
                i += 1
                if i >= len(line):
                    continue
            if line[i] == '$':
                # end of row
                for _ in range(multiplier):
                    y -= 1
                x = upper_left[0]
                i += 1
                if i >= len(line):
                    continue
            if line[i] == '!':
                # all done
                break

    fin.close()

    # format: xmin, xmax, ymin, ymax
    bounds = [upper_left[0], upper_left[0] + width - 1,
              upper_left[1] - height + 1, upper_left[1]]
    return CellGrid(bounds, liveCells)

def write():
    """To be written"""
    # TODO: write this
    pass


