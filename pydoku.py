### This version of pydoku can now deal with backtracking for complex puzzles...
### David Lipson, 08/15


# each cell is defined with a value and coordinate system (r, c, b)

from flask import Blueprint, jsonify
from flask import Flask, url_for, session,  redirect,  render_template, request
import socket

import copy
import time
import sys, os
import math

py_api = Blueprint('py_api', __name__)


class Square:
	def __init__(self, val, row, column, box):
		if val == [0]:
			self.possible = [a for a in range(1,10)]
		else:
			self.possible = val
		self.row = row
		self.column = column
		self.box = box

# each puzzle contains 9x9 Squares; the other attributes are based on the original tree model.
class Puzzle:
	def __init__(self, pieces, parent, children, depth, odds):
		self.pieces = pieces
		self.parent = parent
		self.children = children
		self.depth = depth
		self.odds = odds

# determines box of a cell
def Box(r,c):
	if r < 3:
		if c < 3:
			return 0
		elif c < 6:
			return 1
		else:
			return 2
	elif r < 6:
		if c < 3:
			return 3
		elif c < 6:
			return 4
		else:
			return 5
	else:
		if c < 3:
			return 6
		elif c < 6:
			return 7
		else:
			return 8	

# returns puzzle values as string of arrays
def stringify(puzzle):
	string = []
	for c in puzzle:
		string.append(c.possible)	
	return string

# scrubs cells if any new values are inputted
def Update(square, node, check):
	r = square.row
	c = square.column
	b = square.box
	if check == "row":
		fellows = [s for s in node.pieces if s.row == r and not s == square]
	elif check == "col":
		fellows = [s for s in node.pieces if s.column == c and not s == square]
	elif check == "box":
		fellows = [s for s in node.pieces if s.box == b and not s == square]
	for f in fellows:
		if len(f.possible) == 1 and f.possible[0] in square.possible and len(square.possible) > 1:
			(square.possible).remove(f.possible[0])
	return node

# solves for cells with a unique possibility
def Solve(num, node, check):
	if check == "row":
		cells = [c for c in node.pieces if c.row == num]
	if check == "col":
		cells = [c for c in node.pieces if c.column == num]
	if check == "box":
		cells = [c for c in node.pieces if c.box == num]
	for val in range(1,10):
		possible = []
		for c in cells:
			if val in c.possible:
				possible.append(c)
		if len(possible) == 1:
			a = possible[0]
			a.possible = [val]
			updaterow = [b for b in node.pieces if b.row == a.row and not b == a]
			updatecol = [b for b in node.pieces if b.column == a.column and not b]
			updatebox = [b for b in node.pieces if b.box == a.box and not b == a]
			for s in updaterow:
				node = Update(s, node, "row")
			for s in updatecol:
				node = Update(s, node, "col")
			for s in updatebox:
				node = Update(s, node, "box")
	return node

# 0 = wrong, 1 = correct, 2 = complete puzzle
def Correct(node):
	for i in node.pieces:
		related = [b.possible for b in node.pieces if (b.row == i.row or b.column == i.column or b.box == i.box) and not b == i]
		if (len(i.possible) == 1 and i.possible in related) or len(i.possible) == 0:
			return 0
	if len([a for a in stringify(node.pieces) if len(a) == 1]) < 81:
		return 1
	return 2

# solves and scrubs puzzle until it's either complete or ambiguous.
def Engine(node):
	cont = 0
	while cont == 0:
		curpuzzle = stringify(node.pieces)
		lastpuzzle = curpuzzle
		update = 1
		while update == 1:
			for s in node.pieces:
				node = Update(s, node, "row")
				node = Update(s, node, "col")
				node = Update(s, node, "box")
			if curpuzzle == stringify(node.pieces) or Correct(node) == 0:
				update = 0
			curpuzzle = stringify(node.pieces)
		solve = 1
		while solve == 1:
			for row in range(0,9):
				node = Solve(row, node, "row")
			for col in range(0,9):
				node = Solve(col, node, "col")
			for box in range(0,9):
				node = Solve(box, node, "box")
			if curpuzzle == stringify(node.pieces) or Correct(node) == 0:
				solve = 0
			curpuzzle = stringify(node.pieces)
		if lastpuzzle == stringify(node.pieces) or Correct(node) == 0:
			cont = 1
	return node

# creates children for all possible ambiguous choices of a given puzzle
def CreateChildren(node):
	dup = copy.deepcopy(node)
	for p in dup.pieces:
		if len(p.possible) > 1:
			pos = copy.deepcopy(p).possible
			for i in range(0,len(pos)):
				new = []
				cells = copy.deepcopy(node).pieces
				for n in cells:
					if n.possible == p.possible and n.row == p.row and n.column == p.column:
						x = Square([pos[i]], n.row, n.column, n.box)
						new.append(x)
					else:
						new.append(Square(n.possible, n.row, n.column, n.box))
				puz = Engine(Puzzle(new, node, [], node.depth + 1, len(pos)))
				use = Correct(puz)
				if use == 2:
					return [puz]
				elif use == 1:
					node.children.append(puz)
	return node

# returns the odds (1/#possibilities) for a cell value
def getOdds(node):
	return node.odds

# runs through all possible ambiguous puzzles until it solves
def Main(stack):
	while len(stack) > 0:
		stack = sorted(stack, key=getOdds, reverse=False)
		ind = 0
		maxim = len(stack)
		while ind < maxim:
			n = CreateChildren(stack.pop(0))
			if type(n) == type([]):
				return n[0]
			else:
				for c in n.children:
					stack.append(c)
				ind += 1
	return "ERROR"

def Run(param):
	puzzle = []
	for index,c in enumerate(param):
		row = math.floor(index / 9)
		column = index % 9
		box = Box(row,column)
		if c == '_':
			puzzle.append(Square([0], row, column, box))
		else:
			puzzle.append(Square([int(c)], row, column, box))

	parent = Engine(Puzzle(puzzle, 0, [], 0, 1))
	stack = [parent]
	if Correct(stack[0]) == 2:
		final = stack[0]
	elif Correct(stack[0]) == 0:
		final = "ERROR"
	else:
		final = Main(stack)
		
	if final == "ERROR":
		return (final, param, param)
	else:
		string = ""

		for cell in final.pieces:
			string += str(cell.possible[0])

		return string


@py_api.route('/py/solve', methods=["POST"])
def pysolve():
	try:
		string = request.get_json()["string"]
		result = Run(string)
		if result == "ERROR":
			return "There was an error with the puzzle...", 400		
		else:
			return result, 200
	except:
		return "There was an error with the puzzle...", 400

