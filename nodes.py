class MazNode:
	'''
	Usage:
	>>> body = MazNode('body')
	>>> body+= MazNode('p')
	>>> body.child+= MazNode('strong')
	>>> body.child+= MazNode('br')
	>>> body.child+= MazNode('text')
	>>> body.child&= MazNode('blockquote')
	>>> body&= MazNode('foot')
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
	def __init__(self, name, **attr):
		self.name   = name
		self.parent = attr.pop('parent', None)
		self.child  = attr.pop('child', None) # first child
		self.next   = attr.pop('next', None) # next child
		self.prev   = attr.pop('prev', None) # prev child
		self.attr   = attr
	def __iadd__(self, other):
		'''Add `other` as a child'''
		assert isinstance(other, MazNode)
		if self.child:
			child = self.child
			while child.next:
				child = child.next
			child.next = other
			other.prev = child
		else:
			self.child = other
			other.parent = self
		return self
	def __iand__(self, other):
		'''Add `other` as a brother'''
		assert isinstance(other, MazNode)
		if self.next:
			next = self.next
			while next.next:
				next = next
			next.next = other
			other.prev = next
		else:
			self.next = other
			other.prev = self
		return self
	def __add__(self, other):
		assert isinstance(other, MazNode)
		if self.child:
			child = self.child
			while child.next:
				child = child.next
			child.next = other
			other.prev = child
		else:
			self.child = other
			other.parent = self
		return self
	def __str__(self):
		r = ['<', self.name]
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
	def copy(self):
		return self.__class__(name=self.name, parent=self.parent, child=self.child, prev=self.prev, next=self.next, **self.attr)
	def deepcopy(self):
		copy = self.__class__(name=self.name)
		for name in self.__slots__:
			value = getattr(self, name, None)
			if hasattr(value, 'deepcopy'):
				value = value.deepcopy()
			elif hasattr(value, '__iter__'):
				value = value[:]
			setattr(copy, name, value)
		return copy

