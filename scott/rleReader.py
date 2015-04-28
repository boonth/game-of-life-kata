import random
import numpy as np
import sys
import re

nx = 10
ny = 10
infilename = 'life.rle'
outfilename = 'out.txt'
padding = 10

#get file name from call arguments
if len(sys.argv)  >= 2:
	infilename = sys.argv[1]
	
if len(sys.argv)  >= 3:
	outfilename = sys.argv[2]
	
#get padding amount
if len(sys.argv)  >= 4:
	padding = int(sys.argv[3])
	
#parse file into separate strings for each line
with open(infilename) as f:
	data = f.readlines()
	
#remove any leading comment lines
while len(data) > 0 and (data[0].strip() == '' or data[0].startswith('#')):
	data = data[1:]
	
#check that the first line is the dimensions line
if re.search("x\W*=\W*\d+", data[0].lower()) is None or re.search("y\W*=", data[0].lower()) is None:
	print 'invalid dimensions line!'
	exit()

xmatch = re.findall("x\W*=\W*\d+", data[0].lower())
ymatch = re.findall("y\W*=\W*\d+", data[0].lower())
nx = int(re.findall("\d+",xmatch[0])[0])
ny = int(re.findall("\d+",ymatch[0])[0])

print nx, ny

gridString = ''

for line in data[1:]:
	gridString += line.strip()	

gsData = re.findall("\d*o|\d*b|\$|!",gridString)

with open(outfilename,'w') as f:
	rc = 0
	cc = 0
	for i in range(padding):
		for j in range(2 * padding + nx):
			f.write('0')
		f.write('\n')
	for i in range(padding):
		f.write('0')
	for run in gsData:
		if run.endswith('b'):
			length = 1
			if len(run) > 1:
				length = int(run[:-1])
			for i in range(length):
				f.write('0')
			cc += length
		elif run.endswith('o'):
			length = 1
			if len(run) > 1:
				length = int(run[:-1])
			for i in range(length):
				f.write('1')
			cc += length
		elif '$' in run:
			while cc < nx:
				f.write('0')
				cc += 1
			for i in range(padding):
				f.write('0')
			f.write('\n')
			for i in range(padding):
				f.write('0')
			cc = 0
			rc += 1
		elif '!' in run:
			while cc < nx:
				f.write('0')
				cc += 1
			for i in range(padding):
				f.write('0')
			f.write('\n')
			cc = 0
			rc += 1
			if rc < ny-1:
				print 'line count mismatch!'
	for i in range(padding):
		for j in range(2 * padding + nx):
			f.write('0')
		f.write('\n')	

