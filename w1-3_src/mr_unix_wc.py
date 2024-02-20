from mrjob.job import MRJob

class MRUnixWC(MRJob):

    def mapper(self, key, line):
        yield "chars", len(line)
        yield "words", len(line.split())
        yield "lines", 1

    def reducer(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    MRUnixWC.run()
