class SourceSinkPath:
    def __int__(self, source, sink):
        self.source = source
        self.sink = sink
        self.walk = []
        self.cost  = 0