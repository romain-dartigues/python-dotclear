import copy




__all__ = (
	'MazNode',
)


INPLACE  = 0
COPY     = 1
DEEPCOPY = 2





class MazNode(object):
	'''
	Usage:
	>>> body = MazNode('body')
	>>> body+= MazNode('p')
	>>> body.child+= MazNode('strong')
	>>> body.child+= MazNode('br')
	>>> body.child+= MazNode('text')
	>>> body.child&= MazNode('blockquote')
	>>> body|= MazNode('foot')
	>>> body.next+= MazNode('text')
	>>> print 'body (%d childs): %s' % (len(body), body)
	body (2 childs): <body><p><strong /><br /><text /></p><blockquote /></body>
	>>> print 'body[1]: %s' %(body[1],)
	body[1]: <p><strong /><br /><text /></p>
	>>> for child in body:
	...         print '  : %s' %(child,)
	... 
	  : <p><strong /><br /><text /></p>
	  : <blockquote />
	'''
	__slots__ = ('name', 'parent', 'child', 'prev', 'next', 'attr')
	__serial__ = 2010, 4,14
	def __init__(self, name, **attr):
		self.name   = name
		self.parent = attr.pop('parent', None)
		self.child  = attr.pop('child', None) # first child
		self.next   = attr.pop('next', None) # next child
		self.prev   = attr.pop('prev', None) # prev child
		self.attr   = attr
	@staticmethod
	def __add(a, b, mode):
		'''Base function for addition'''
		assert isinstance(a, MazNode) and isinstance(b, MazNode)
		if mode == COPY:
			a = copy.copy(a)
			b = copy.copy(b)
		elif mode == DEEPCOPY:
			a = copy.deepcopy(a)
			b = copy.deepcopy(b)
		if a.child:
			child = a.child
			while child.next:
				child = child.next
			child.next = b
			b.prev = child
			b.parent = a
		else:
			a.child = b
			b.parent = a
		return a
	def __iadd__(self, other):
		'''Add `other` as a child, in-place'''
		return self.__add(self, other, mode=INPLACE)
	def __ladd__(self, other):
		return self.__add(self, other, mode=DEEPCOPY)
	def __radd__(self, other):
		return self.__add(other, self, mode=DEEPCOPY)
	def __add__(self, other):
		'''Add `other` as a child and return a new object (deepcopy of self and other)'''
		return self.__add(self, other, mode=DEEPCOPY)
	@staticmethod
	def __or(a, b, mode):
		'''Base function for bitwise or'''
		assert isinstance(a, MazNode) and isinstance(b, MazNode)
		if mode == COPY:
			a = copy.copy(a)
			b = copy.copy(b)
		elif mode == DEEPCOPY:
			a = copy.deepcopy(a)
			b = copy.deepcopy(b)
		if a.next:
			next = a.next
			while next.next:
				next = next
			next.next = b
			b.prev = next
		else:
			a.next = b
			b.prev = a
		return a
	def __ior__(self, other):
		'''Add `other` as a brother, in-place'''
		return self.__or(self, other, INPLACE)
	def __lor__(self, other):
		return self.__or(self, other, DEEPCOPY)
	def __ror__(self, other):
		return self.__or(other, self, DEEPCOPY)
	def __or__(self, other):
		'''Add `other` as a brother and return a new object (deepcopy of self and other)'''
		return self.__or(self, other, DEEPCOPY)
	def __str__(self):
		r = ['<', self.name]
		# FIXME: don't rely on the slots
		r+= [' %s=%r' %(attr, self.attr[attr]) for attr in self.attr if attr not in self.__slots__]
		if self.child:
			r+= ['>'] + [str(child) for child in self] + ['</', self.name, '>']
		else:
			r+= [' />']
		return ''.join(r)
	def __repr__(self): return repr(self.__str__())
	def __len__(self):
		'''Number of childs'''
		c = 0
		for child in self:
			c+= 1
		return c
	@property
	def children(self):
		return [child for child in self]
	def __nonzero__(self): return True
	def __getitem__(self, key):
		if isinstance(key, basestring):
			return self.attr[key]
		if isinstance(key, int):
			if key < 0:
				raise TypeError('negative indexes not supported')
			c = 0
			for child in self:
				if key == c:
					return child
				c+= 1
			raise IndexError
		raise TypeError
	def __iter__(self):
		'''Iter through childs'''
		child = self.child
		while child:
			yield child
			child = child.next
