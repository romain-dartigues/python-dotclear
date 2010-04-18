import copy




__all__ = (
	'MazNode',
)


INPLACE  = 0
COPY     = 1
DEEPCOPY = 2

ENTER = 1
LEAVE = 2
SINGLETON = ENTER|LEAVE





class MazNode(object):
	'''
	Usage:
	>>> body = MazNode('body')
	>>> body+= MazNode('p')
	>>> body.child+= MazNode('strong')
	>>> body.child+= MazNode('br')
	>>> body.child+= MazNode('text')
	>>> body.child|= MazNode('blockquote')
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
	__serial__ = 2010, 4,18
	def __init__(self, name, attributes={}, **attr):
		self.name   = name
		self.parent = attr.pop('parent', None)
		self.child  = attr.pop('child', None) # first child
		self.next   = attr.pop('next', None) # next child
		self.prev   = attr.pop('prev', None) # prev child
		self.attr   = attributes
		self.attr.update(attr)
	@staticmethod
	def __add(a, b, mode):
		'''Base function for addition (add `b` as a child of `a`)'''
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
		'''Base function for bitwise or (add `b` as a brother of `a`)'''
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
			b.parent = next.parent
		else:
			a.next = b
			b.prev = a
			b.parent = a.parent
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
	def descend(self, node=None):
		'''Iter through the tree, starting at ``node`` and yield a tuple

		Parameter:
		- `node`: starting node, default is `self`

		Return a tuple of three elements:
		#. a bitmask which might be :var:`ENTER`, :var:`LEAVE or
		   :var:`SINGLETON` upon entering, leaving or entering and
		   leaving (in the case of a singleton)
		#. the current node
		#. the depth from the root to the current node

		.. Note::
		   The iteration is not recursive, so you won't smash your
		   stack.
		'''
		if not node:
			node = self
		root = node
		curr = node
		depth = 0
		prev = None
		while curr:
			status = ENTER
			if not curr.child:
				status|= LEAVE
			elif prev and (curr is root or curr.child is prev):
				status = LEAVE
			yield (status, curr, depth)
			if curr is root:
				if prev or not root.child:
					break

			if curr.child:
				if curr.child is prev:
					prev = curr
				else:
					depth+= 1
					curr = curr.child
					prev = curr
					continue

			if curr.next:
				curr = curr.next
			else:
				depth-= 1
				curr = curr.parent
