'''
PyNigma - An implementation of the German enigma machine in python

by Doug Walter (dougwritescode@gmail.com)
'''

import string

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def isEncodableChar(inltr):
	if type(inltr) is not str:
		return False
	elif inltr not in list(string.ascii_uppercase): 
		return False
	return True
	
def isEncodableInt(inint):
	if type(inint) is not int: 
		return False
	if inint not in range(26):
		return False
	return True

def ltrToInt(inltr):
	if not isEncodableChar(inltr):
		return None
	return ord(inltr) - 65
	
def intToLtr(inint):
	if not isEncodableInt(inint):
		return None
	return string.ascii_uppercase[inint]

class cypher(object):
	
	cypher = alphabet
	intcypher = []
	def __init__(self, subs):
		if subs is not str or len(subs) != 26:
			raise TypeError
		self.cypher = subs
		for char in self.cypher:
			intcypher.append(ord(char) - 65)
			
	def __str__(self):
		return self.cypher
		
	def __len__(self):
		return len(self.cypher)
		
	def __getitem__(self, key):
		return self.cypher[key]
		
	def index(self, key):
		if key not in self.cypher:
			raise ValueError("Invalid cypher key")
		return self.cypher.index(key)
			
class rotor(cypher):

	def __init__(self, subs, inturnlist):
		super(cypher, self).__init__()
		self.cypher = subs
		self.turnovers = inturnlist
		
	def __str__(self):
		return self.cypher + ", " + str(self.turnovers)

	def encode(self, inint):
		if not isEncodableInt(inint):
			raise ValueError("Not an encodable value.")
			return None
		return ltrToInt(self[ltrToInt(alphabet[inint])])
		
	def encodeBackwards(self, inint):
		if not isEncodableInt(inint):
			raise ValueError("Not an encodable value.")
			return None
		return ltrToInt(alphabet[ltrToInt(self[inint])])
	
class reflector(cypher):
	
	# checks to make sure that the input cypher is a proper reflector
	def __init__(self, subs):
		super(cypher, self).__init__()
		self.cypher = subs
		for char in self.cypher:
			alphind = alphabet.index(char)
			cyphind = self.cypher.index(char)
			if alphabet[cyphind] != self.cypher[alphind]:
				raise ValueError("Invalid Reflector Values")
		
	def __str__(self):
		return self.cypher
	
class rotorPool:
	
	# Default Rotors
	rotorI = rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ",['R'])
	rotorII = rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE",['F'])
	rotorIII = rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO",['W'])
	rotorIV = rotor("ESOVPZJAYQUIRHXLNFTGKDCMWB",['K'])
	rotorV = rotor("VZBRGITYUPSDNHLXAWMJQOFECK",['A'])
	
	# Default "Wide" Reflectors
	reflectorB = reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")
	reflectorC = reflector("FVPJIAOYEDRZXWGCTKUQSBNMHL")
	
	# M3 and M4 Rotors
	rotorVI = rotor("JPGVOUMFYQBENHZRDKASXLICTW",['A','N'])
	rotorVII = rotor("NZJHGRCXMYSWBOUFAIVLPEKQDT",['A','N'])
	rotorVIII = rotor("FKQHTLXOCBJSPDZRAMEWNIUYGV",['A','N'])
	
	# Kriegsmarine M4 Greek Rotors (Use only with "thin" reflectors)
	rotorBeta = rotor("LEYJVCNIXWPBQMDRTAKZGFUHOS",['A','N'])
	rotorGamma = rotor("FSOKANUERHMBTIYCWLQPZXVGJD",['A','N'])
	
	# Special "thin" reflectors
	reflectorBThin = reflector("ENKQAUYWJICOPBLMDXZVFTHRGS")
	reflectorCThin = reflector("RDOBJNTKVEHMLFCWZAXGYIPSUQ")
	
class rotorSet(rotorPool):
	
	rotors = []
	reflector = None
	rotoroffsets = []
	
	def __init__(self, rotorlist, inreflector):
		for rot in rotorlist:
			self.rotors.append(rot)
			self.rotoroffsets.append(0)
		self.reflector = inreflector
		
	def __str__(self):
		'''
		Displays the enigma's current state, including:
			Rotor selections
			Rotor offsets
			Reflector encoding
			Alphabet encoding at current rotor position
		'''
		tempoffs = self.rotoroffsets
		tempstr = ""
		for rot in self.rotors:
			tempind = self.rotors.index(rot)
			tempstr += "Rotor "
			tempstr += str(tempind)
			tempstr += ": "
			tempstr += str(rot)
			tempstr += " offset: "
			tempstr += str(self.rotoroffsets[tempind])
			tempstr += '\n'
		tempstr += "Reflector: " + str(self.reflector)
		tempstr += '\n'
		tempstr += 'In:  ' + alphabet
		tempstr += '\n'
		temp2 = 'Out: '
		for char in alphabet:
			self.setRotorOffsets([0,0,0])
			temp2 += self.encodeCharacter(char)
		tempstr += temp2
		self.rotoroffsets = tempoffs
		return tempstr
		
	def setRotorOffsets(self, rotorindices):
		'''
		This method allows the positions of the enigma
		rotors to be directly set before encoding.
		'''
		if len(rotorindices) != len(self.rotors):
			raise ValueError("Incorrect number of rotors")
			return
		self.rotoroffsets = rotorindices
		
	def advanceRotors(self):
		'''
		This is a utility method that advances the last rotor 
		in the machine, advancing the earlier rotors at 
		an appropriate turnover point.
		'''
		offs = self.rotoroffsets
		rots = self.rotors
		if rots[2][offs[2]] in rots[2].turnovers:
			self.rotoroffsets[1] += 1
			self.rotoroffsets[1] %= 26
			if rots[1][offs[1]] in rots[1].turnovers:
				self.rotoroffsets[0] += 1
				self.rotoroffsets[0] %= 26
		self.rotoroffsets[2] += 1
		self.rotoroffsets[2] %= 26
		
	def encodeCharacter(self, inchar):
		'''
		This method will return a properly encoded character
		after the machine's state has advanced the cypher rotors.
		
		The return value can be changed to templist
		if the changes in value need to be displayed
		'''
		
		self.advanceRotors()
		
		inind = ltrToInt(inchar)
		templist = [inchar]
		rots = self.rotors
		offs = self.rotoroffsets
		
		pass1 = rots[2][(ltrToInt(inchar) + offs[2]) % 26]
		templist.append(pass1)
		
		pass2 = rots[1][(ltrToInt(pass1) + offs[1]) % 26]
		templist.append(pass2)
		
		pass3 = rots[0][(ltrToInt(pass2) + offs[0]) % 26]
		templist.append(pass3)
		
		reflection = self.reflector[ltrToInt(pass3)]
		templist.append(reflection)
		
		passback1 = alphabet[(rots[0].index(reflection) - offs[0]) % 26]
		templist.append(passback1)
		
		passback2 = alphabet[(rots[1].index(passback1) - offs[1]) % 26]
		templist.append(passback2)
		
		passback3 = alphabet[(rots[2].index(passback2) - offs[2]) % 26]
		templist.append(passback3)
		
		return templist[-1]
		
	def encodeMessage(self, instr):
		'''
		This method uses the encodeCharacter method
		to encode an entire message, leaving spaces
		and punctuation alone.
		'''
		if type(instr) is not str:
			raise ValueError("Invalid text input")
			return None
		message = ""
		instr = instr.upper()
		for char in instr:
			if char not in alphabet:
				message += char
			else:
				message += self.encodeCharacter(char)
		return message

if __name__ == "__main__":
	pool = rotorPool()
	rotorset = rotorSet([pool.rotorI, pool.rotorII, pool.rotorIII], pool.reflectorB)
	print rotorset, '\n'
	
	'''
	These outputs demonstrate that a message will encode and decode
	correctly when the rotors start from the same position.
	'''
	print 'JACKDAWS LOVE MY BIG SPHINX OF QUARTZ'
	rotorset.setRotorOffsets([0,0,0])
	print "start: " + str(rotorset.rotoroffsets)
	print rotorset.encodeMessage('JACKDAWS LOVE MY BIG SPHINX OF QUARTZ')
	rotorset.setRotorOffsets([0,0,0])
	print "start: " + str(rotorset.rotoroffsets)
	print rotorset.encodeMessage('MHQZRJHM RNEJ UD GHH AOGKCP WU GQUJLO')
