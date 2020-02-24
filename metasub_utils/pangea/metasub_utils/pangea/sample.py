


class Sample:

    def __init__(self, sample_name, metadata={}):
        self.name = sample_name
        self.metadata = metadata

    def upload(self):
        return add_sample(self.name, metadata=self.metadata)
