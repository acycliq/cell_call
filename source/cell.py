class Cell(object):
    def __init__(self, x, y, Id):
        self._Id = Id
        self._x = x
        self._y = y
        self._spots = None
        self._cellType = None

        @property
        def Id(self):
            return self._Id

        @Id.setter
        def Id(self, value):
            self._Id = value

        @property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @property
        def y(self):
            return self._y

        @y.setter
        def y(self, value):
            self._y = value

        @property
        def spots(self):
            return self._spots

        @spots.setter
        def spots(self, value):
            self._spots = value

        @property
        def cellType(self):
            return self._cellType

        @Id.setter
        def cellType(self, value):
            self._cellType = value

