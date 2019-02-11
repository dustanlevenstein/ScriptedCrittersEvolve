import random, time, math

BRANCH = 0
SWAP = 1
FLIP_0 = 2
FLIP_1 = 3
LEFT = 4
RIGHT = 5
RETURN = 6

FLAG_0 = 0
FLAG_1 = 1
COMPARE = 2
BEGINNING_OF_LIST = 3
END_OF_LIST = 4
RANDOM = 5
COMMAND_TYPE = 6
BRANCH_TARGET = 7
def execute(cmds, under_list, interrupt_at = 1000, chance_of_interruption = 0.00001):
	"""
	Executes a list of commands according to the following specs:

	Commands are a sort of pseudo-machine-code style.
	Each command is of the following form:

	(flag_0, flag_1, compare, beginning_of_list, end_of_list, random, 
	 command_type, branch_target)

	The first five items are conditionals. The code gets two flags, and a random bit for each command (which it will probably ignore). The conditionals can be one of three
	values: -1 (no condition), 0 (runs if condition is false), and 1 (runs if condition is true).
	The command types are: BRANCH, SWAP, FLIP_0, FLIP_1, LEFT, RIGHT, RETURN. The branch target is interpretted relative to the command following the current one,
	 and it wraps around cmds.
	LEFT and RIGHT move the pointer in the underlying list.

	under_list is the list to be sorted.

	interrupt_at will interrupt on that instruction. If that parameter isn't passed, then chance_of_interruption determines the probability on any given command that the code
	will be interrupted and forced to return what it has at that instant. If interrupted, the list returned will be sorted in reverse, because the code should be expected
	to halt on its own.
	"""
	under_list = list(under_list)
	flag_0 = flag_1 = 0
	current_command = 0
	list_pointer = 0
	def cond(cmd_flag, actual):
		if cmd_flag < 0: return True
		if cmd_flag == 0: return not actual
		return actual
	execution_length = 1
	while True:
		current_command = current_command % len(cmds)
		cmd = cmds[current_command]
		current_command += 1
		if ( cond(cmd[FLAG_0], flag_0) and
		     cond(cmd[FLAG_1], flag_1) and
		     cond(cmd[COMPARE], list_pointer + 1 < len(under_list) and under_list[list_pointer] > under_list[list_pointer+1]) and
		     cond(cmd[BEGINNING_OF_LIST], list_pointer == 0) and
		     cond(cmd[END_OF_LIST], list_pointer +1 == len(under_list)) and
		     cond(cmd[RANDOM], random.randrange(2))
		   ):
			typ = cmd[COMMAND_TYPE]
			if typ == BRANCH:
				current_command += cmd[BRANCH_TARGET]
			elif typ == SWAP and list_pointer+1 < len(under_list):
				under_list[list_pointer], under_list[list_pointer+1] = under_list[list_pointer+1], under_list[list_pointer]
			elif typ == FLIP_0:
				flag_0 = not flag_0
			elif typ == FLIP_1:
				flag_1 = not flag_1
			elif typ == LEFT:
				list_pointer -= 1
				if list_pointer < 0: list_pointer = 0
			elif typ == RIGHT:
				list_pointer += 1
				if list_pointer >= len(under_list): list_pointer = len(under_list) - 1
			else:
				return under_list, execution_length
		if interrupt_at is not None and execution_length >= interrupt_at:
			under_list.sort(reverse=True)
			return under_list, execution_length
		elif interrupt_at is None and random.random() < chance_of_interruption:
			under_list.sort(reverse=True)
			return under_list, execution_length
		execution_length += 1

def score_list(lis):
	"""
	Scores the sorting of the list, between 0 and 1. It is simply the number of pairs which are in the right order (smaller to greater) relative to the
	total number of pairs.
	"""
	score = 0.0
	for i in range(len(lis)):
		for j in range(i+1, len(lis)):
			if lis[i] < lis[j]:
				score += 1
	score *= 2
	score /= len(lis)
	score /= (len(lis)-1)
	return score

def generate_random_command():
	"""
	Generates a command completely at random. Distributations are mostly uniform,
	except for the branch target, which is normal with a mean of -10 and a standard
	deviation of 15.
	"""
	return (random.randrange(-1, 2),           # flag_0
	        random.randrange(-1, 2),           # flag_1
	        random.randrange(-1, 2),           # compare
	        random.randrange(-1, 2),           # beginning_of_list
	        random.randrange(-1, 2),           # end_of_list
	        random.randrange(-1, 2),           # random 
	        random.randrange(7),               # command_type
	        int(round(random.gauss(-10, 15)))) # branch_target

def generate_random_program():
	"""
	Generates a program. The number of commands is normal with a mean of 100 and a standard deviation of 20.
	"""
	num_coms = max(int(round(random.gauss(100, 20))), 1)
	if num_coms < 0: num_coms = 0
	return [generate_random_command() for i in range(num_coms)]

def mutate_single_command(cmd):
	"""
	Each portion of the command has a 1 in 1000 probability of being chosen to mutate, in which case the
	distribution is uniformly random for all but the target, which mutates with a mean equal to the original
	target, and a standard deviation of 2.
	"""
	cmd = list(cmd)
	# flag_0
	if random.random() < .0001:
		cmd[FLAG_0] = random.randrange(-1, 2)
	# flag_1
	if random.random() < .0001:
		cmd[FLAG_1] = random.randrange(-1, 2)
	# compare
	if random.random() < .0001:
		cmd[COMPARE] = random.randrange(-1, 2)
	# beginning_of_list
	if random.random() < .0001:
		cmd[BEGINNING_OF_LIST] = random.randrange(-1, 2)
	# end_of_list
	if random.random() < .0001:
		cmd[END_OF_LIST] = random.randrange(-1, 2)
	# random
	if random.random() < .0001:
		cmd[RANDOM] = random.randrange(-1, 2)
	# command_type
	if random.random() < .0001:
		cmd[COMMAND_TYPE] = random.randrange(7)
	# branch_target
	if random.random() < .0001:
		cmd[BRANCH_TARGET] = int(round(random.gauss(cmd[BRANCH_TARGET], 2)))
	return tuple(cmd)

def mutate_program(cmds):
	cmds = list(cmds)
	i = 0
	if random.random() < .0001:
		cmds.insert(0, generate_random_command())
	while i < len(cmds):
		if i>0 and random.random() < .001:
			del cmds[i:]
			break
		if len(cmds)>1 and random.random() < .0001:
			del cmds[i]
			continue
		if i+1 < len(cmds) and random.random() < .0001:
			cmds[i], cmds[i+1] = cmds[i+1], cmds[i]
		cmds[i] = mutate_single_command(cmds[i])
		i += 1
		if random.random() < .0001:
			cmds.insert(0, generate_random_command())
	#while random.random() < (len(cmds) / 1000.0):
	#	del cmds[random.randrange(len(cmds))]
	#if len(cmds) > 1000:
	#	print "What?!"
	return cmds

def merge_programs(cmds1, cmds2):
	"""
	Literally splices portions (of length of 20 on average) of each program interspersed together, then mutates. Order of parameters does not matter.
	"""
	if random.random() < .5:
		cmds1, cmds2 = cmds2, cmds1
	i_1 = 0
	i_2 = 0
	target = []
	while i_1 < len(cmds1) or i_2 < len(cmds2):
		if random.random() < .05:
			i_1, i_2 = i_2, i_1
			cmds1, cmds2 = cmds2, cmds1
		if i_1 >= len(cmds1):
			i_1, i_2 = i_2, i_1
			cmds1, cmds2 = cmds2, cmds1
		target.append(cmds1[i_1])
		i_1 += 1
	target = mutate_program(target)
	return target

def Main():
	Programs = [[generate_random_program(), 0, 0, 0] for i in xrange(10000)]
	print "Programs generated"
	constant = 3.0
	size = 20
	gen = 1
	try:
		while True:
			initial_time = time.time()
			print
			print "Generation %s" % gen
			sizes = []
			for i in range(10):
				size = int(round(random.gauss(20, 10)))
				if size <= 1: size = 2
				li = range(size)
				random.shuffle(li)
				first = True
				for pair in Programs:
					result, length = execute(pair[0], li) # , None, 1/(size*size*constant) )
					pair[1] += score_list(result)
					pair[2] += length
					pair[3] = len(pair[0])
				sizes.append(size)
			Programs.sort(key = lambda x: (-x[1], x[2]/(sum(size*size for size in sizes)), max(x[3]/10, 2)))
						 # selects for high score, lower execution length, and lower code size
			print "Executed on lists of length %s, %s, %s, %s, %s, %s, %s, %s, %s and %s." % tuple(sizes)
			print "Lowest score =", Programs[-1][1]
			Programs = Programs[:10]
			print "Highest scores, execution lengths, code sizes =", map(lambda x: x[1:], Programs )
			print "Computer execution length =", time.time()-initial_time
			#if Programs[0][0] == 1.0:
				# f = open("EvolutionData.txt", "a")
				# f.write(str(Programs))
				# f.close()
			#	size += 10
			#	new_constant = random.gauss(constant, .1)
			#	if new_constant > 0:
			#		constant = min(new_constant, constant)
			New_Programs = []
			for i in range(10):
				for j in range(i, 10):
					for k in range(100):
						if i == j:
							New_Programs.append([mutate_program(Programs[i][0]), 0, 0, 0])
						else:
							New_Programs.append([merge_programs(Programs[i][0], Programs[j][0]), 0, 0, 0])
			Programs = New_Programs
			gen += 1
	except(KeyboardInterrupt):
		initial_time = time.time()
		print
		print "Interrupted. Computing scores in lax conditions."
		constant = 10.0
		size = 10
		li = range(size)
		random.shuffle(li)
		first = True
		for pair in Programs:
			result, length = execute(pair[0], li) # , None, 1/(size*size*constant) )
			pair[1] = score_list(result)
			pair[2] = length
			pair[3] = len(pair[0])
		Programs.sort(key = lambda x: (-x[1], x[2], x[3]) )
		print
		print "Executed on a list of length %s."%size
		print "Lowest score =", Programs[-1][1]
		Programs = Programs[:10]
		print "Highest scores, execution lengths, code sizes =", map(lambda x: x[1:], Programs)
		print "Computer execution length =", time.time()-initial_time

Main()
