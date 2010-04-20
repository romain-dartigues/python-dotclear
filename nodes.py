import copy




__all__ = (
	'MazNode',
)


INPLACE  = 0
COPY     = 1
DEEPCOPY = 2

ENTER = 1
LEAVE = 2
EMPTY = ENTER|LEAVE





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
	'''
	__slots__ = ('name', 'parent', 'child', 'prev', 'next', 'attr')
	__serial__ = 2010, 4,21

	def __init__(self, name='', attributes={}, **attr):
		self.name   = name
		self.parent = attr.pop('parent', self)
		self.child  = attr.pop('child', None) # first child
		self.next   = attr.pop('next', self) # next child
		self.prev   = attr.pop('prev', self) # prev child
		self.attr   = attributes.copy()
		self.attr.update(attr)
		assert isinstance(self.parent, MazNode)
		assert isinstance(self.child,  (None.__class__, MazNode))
		assert isinstance(self.prev,   MazNode)
		assert isinstance(self.next,   MazNode)
		assert isinstance(self.attr,   dict)
		assert isinstance(self.name,   basestring)
		assert bool(self.name) | bool(self.attr.get('value'))

	@staticmethod
	def __add(a, b, mode):
		'''Base function for addition (add `b` as a child of `a`)'''
		assert isinstance(a, MazNode) and isinstance(b, MazNode)
		assert mode in (INPLACE, COPY, DEEPCOPY)
		if mode == COPY:
			a = copy.copy(a)
			b = copy.copy(b)
		elif mode == DEEPCOPY:
			a = copy.deepcopy(a)
			b = copy.deepcopy(b)
		assert a.name, 'nameless nodes should not have children'
		b.parent = a
		if a.child:
			MazNode.__or(a.child, b, INPLACE)
		else:
			a.child = b
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
		assert mode in (INPLACE, COPY, DEEPCOPY)
		if mode == COPY:
			a = copy.copy(a)
			b = copy.copy(b)
		elif mode == DEEPCOPY:
			a = copy.deepcopy(a)
			b = copy.deepcopy(b)
		b.prev = a.prev
		b.next = a
		b.parent = a.parent
		a.prev.next = b
		a.prev = b
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
		if not self.name:
			assert self.attr.get('value', False)
			return self.attr['value']
		l = len(self)
		r = ['<', self.name]
		r+= [' %s=%r' %(attr, self.attr[attr]) for attr in self.attr]
		if l < 1:
			r+= [' />']
		elif l < 2:
			r+= ['>', unicode(self.child), '</%s>' % self.name]
		else:
			r+= ['>', '<!-- %u child%s --->' %(l, l>1 and 's' or ''), '</%s>' % self.name]
		return unicode(''.join(r))

	def __repr__(self):
		return repr(self.__str__())

	def __len__(self):
		'''Return the number of childs'''
		c = 0
		for child in self:
			c+= 1
		return c

	@property
	def children(self):
		return [child for child in self]

	def __nonzero__(self):
		return True

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
			if child.parent.child is child:
				break

	def descend(self, node=None):
		'''Iter through the tree, starting at ``node`` and yield a tuple

		Parameter:
		- `node`: starting node, default is `self`

		Return a tuple of three elements:
		#. a bitmask which might be :var:`ENTER`, :var:`LEAVE` or
		   :var:`EMPTY` upon entering, leaving or entering and
		   leaving at once (in the case of an empty element)
		#. the current node
		#. the depth from the root to the current node

		.. Note::
		   The iteration is not recursive, so you won't smash your
		   stack.
		'''
		if not node:
			node = self
		root = node
		curr = root
		depth = 0
		while 1:
			yield (curr.child and ENTER or EMPTY, curr, depth)
			if curr.child:
				curr = curr.child
				depth+= 1
				continue
			if curr.child:
				yield (LEAVE, curr, depth)
			if curr is root:
				break
			curr = curr.next
			if curr is not curr.parent.child:
				continue
			curr = curr.parent.next
			depth-= 1
			yield (LEAVE, curr.prev, depth)
			while curr is curr.parent.child:
				depth-= 1
				curr = curr.parent.next
				yield (LEAVE, curr.prev, depth)
			if curr is root.next:
				break
