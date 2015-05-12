"""
Displays a grid of cells for Conway's Game of Life.

Location (0, 0) is the bottom left. 

Cell (0, 0) is the first one on the bottom left, coords are (<xpos>, <ypos>).
Cell coordinates can be negative. Each cell has width and height of 1. So cell
(0, 0) has world coordinates (0, 0) and (1, 1).


"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *
import sys


# cell size in pixels
cellSize = (45, 50)
#cellSize = (25, 30)
#cellSize = (10, 10)
backgroundColor = (0.8, 0.8, 0.8, 1.0)
cellColor = (0.6588, 0.4706, 0.4314)
gridColor = (0.35, 0.35, 0.35)
gridLineWidth = 2

anti_alias = True

class CellGridViewerWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        # the bounds of the grid to show, in terms of cells, inclusive
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0

        # list of cells which are alive
        self.liveCells = []

        self.showGrid = True

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.drawCells()
        if self.showGrid:
            self.drawGrid()

        glFlush()

    def drawCells(self):

        glColor3f(*cellColor)
        for cell in self.liveCells:
            i, j = cell
            glRectf(i, j, i+1, j+1)

    def drawGrid(self):

        glColor3f(*gridColor)
        glLineWidth(gridLineWidth)

        glBegin(GL_LINES)

        # vertical lines
        for i in range(self.xmin, self.xmax + 1):
            glVertex2f(i, self.ymin)
            glVertex2f(i, self.ymax+1)

        # horizontal lines
        for i in range(self.ymin, self.ymax + 1):
            glVertex2f(self.xmin, i)
            glVertex2f(self.xmax+1, i)

        glEnd()

    def resizeGL(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.xmin, self.xmax+1, self.ymin, self.ymax+1)
        glViewport(0, 0, w, h)

    def initializeGL(self):
        glClearColor(*backgroundColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        self.setAntiAliasing(anti_alias)

    def setGridView(self, xmin, xmax, ymin, ymax):
        """
        Set the grid view. Parameters are cell coordinates, and are inclusive.
        
        """
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def setLiveCells(self, cells):
        """Set which cells are alive. Needs a list of cell coordinates."""
        self.liveCells = cells

    def gridOn(self):
        """Turn drawing the grid on"""
        self.showGrid = True

    def gridOff(self):
        """Turn drawing the grid off"""
        self.showGrid = False

    def setAntiAliasing(self, flag):
        """enable or disable anti-aliasing"""

        if flag:
            # turn anti-aliasing on
            glEnable(GL_POINT_SMOOTH);
            glEnable(GL_LINE_SMOOTH);
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE);
            #glBlendFunc(GL_ONE, GL_ONE);
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);
            glHint(GL_POINT_SMOOTH_HINT, GL_NICEST);
        else:
            # turn it off
            glDisable(GL_BLEND);
            glDisable(GL_LINE_SMOOTH);

class CellGridViewerMainWindow(QtGui.QMainWindow):

    def __init__(self):
        """Create the window gui"""

        QtGui.QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):

        open_icon = os.path.join(os.path.dirname(__file__), 'icons/open.ico')
        openFile = QtGui.QAction(QtGui.QIcon(open_icon), "Load File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Load File')
        self.connect(openFile, QtCore.SIGNAL('triggered()'), self.onOpen)

        tick_icon = os.path.join(os.path.dirname(__file__), 'icons/tick.ico')
        tick = QtGui.QAction(QtGui.QIcon(tick_icon), "Tick", self)
        tick.setStatusTip('Tick')
        self.connect(tick, QtCore.SIGNAL('triggered()'), self.onTick)

        exit_icon = os.path.join(os.path.dirname(__file__), 'icons/close.ico')
        exit = QtGui.QAction(QtGui.QIcon(exit_icon), "Exit", self)
        exit.setShortcut("Ctrl+Q")
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.setWindowTitle('Game of Life')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(tick)
        fileMenu.addAction(exit)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(openFile)
        toolbar.addAction(tick)
        toolbar.addAction(exit)

        self.viewer = CellGridViewerWidget(self)
        self.setCentralWidget(self.viewer)

        self.statusBar()

        self.centerOnScreen()

    def onOpen(self):
        """Triggered when opening file"""

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file')

        if filename != '':
            self.loadCellFile(str(filename))

    def onTick(self):
        """Triggered when opening file"""

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        print 'filename:', filename

    def loadCellFile(self, filename):
        """Load a cell file"""

        # look at file extension to see what type of file it is
        ext = os.path.splitext(filename)[1]
        if ext == '.txt':
            self.loadMyCellFile(filename)
        elif ext == '.rle':
            self.loadRLEFile(filename)

        self.resize()
        self.centerOnScreen()
        self.updateStatusBar()

    def loadMyCellFile(self, filename):
        """Load a cell file in my personal file format"""

        # format: xmin, xmax, ymin, ymax
        bounds = None
        cells = []
        fin = open(filename, 'r')
        for line in fin:
            line2 = line.split()
            if len(line2) == 0 or line2[0][0] == '#':
                continue

            # if haven't read bounds of grid yet, then read it in
            if bounds is None:
                bounds = [int(x) for x in line2]
                continue

            cells.append((int(line2[0]), int(line2[1])))

        fin.close()

        self.viewer.setGridView(bounds[0], bounds[1], bounds[2], bounds[3])
        self.viewer.setLiveCells(cells)

    def loadRLEFile(self, filename):
        """Load a file in the extended RLE file format as used by Golly"""

        # format: xmin, xmax, ymin, ymax
        cells = []
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
                        cells.append((x, y))
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
        self.viewer.setGridView(bounds[0], bounds[1], bounds[2], bounds[3])
        self.viewer.setLiveCells(cells)

    def resize(self):
        """Recalculate the window size. Make sure aspect ratio is maintained
        such that the cells look square.
        
        """

        xmin = self.viewer.xmin
        xmax = self.viewer.xmax
        ymin = self.viewer.ymin
        ymax = self.viewer.ymax
        winSize = ((xmax - xmin + 1) * cellSize[0], 
                   (ymax - ymin + 1) * cellSize[1])
        self.setGeometry(0, 0, winSize[0], winSize[1])

    def updateStatusBar(self):
        """Update the status bar"""

        xmin = self.viewer.xmin
        xmax = self.viewer.xmax
        ymin = self.viewer.ymin
        ymax = self.viewer.ymax
        self.statusBar().showMessage('bounds:  (%i, %i) to (%i, %i)' % 
                                     (xmin, ymin, xmax, ymax))

    def centerOnScreen (self):
        """Center the window on the screen"""

        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2)  - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        """Event when someone tries to close the window"""
        pass

        ## ask the user if you really want to close
        #reply = QtGui.QMessageBox.question(self, "Confirmation",
        #              "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #              QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore()

if __name__ == '__main__':
    app = QtGui.QApplication(['Game of Life'])
    window = CellGridViewerMainWindow()
    if len(sys.argv) >= 2:
        window.loadCellFile(sys.argv[1])
    window.show()
    sys.exit(app.exec_())


