class Spot(object):
    def __init__(self):
        self._Id = None
        self._x = None
        self._y = None
        self._geneName = None

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
        def geneName(self):
            return self._geneName

        @geneName.setter
        def spots(self, value):
            self._geneName = value


