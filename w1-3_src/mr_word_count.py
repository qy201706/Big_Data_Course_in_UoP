from mrjob.job import MRJob
import re

wordRE = re.compile(r"[a-zA-Z]+")

class MRWordCount(MRJob):
    def mapper(self, key, value):
        # key: line number – not used here
        # value: contents of one line
        for word in wordRE.findall(value) :
            yield word, 1                 # output a pair: word and count
    def reducer(self, key, values):
        yield key, sum(values)


if __name__ == '__main__':
    MRWordCount.run()
