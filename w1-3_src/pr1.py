import sys, os
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import RawValueProtocol

#N = sys.argv[2]
NITER = 50

class MRPageRank(MRJob):
    OUTPUT_PROTOCOL = RawValueProtocol

    def mapper(self, key, value):
        fields = value.split()
        #print(fields)
        pageRank = float(fields[1])
        outLinks = fields[2:]
        prContrib = pageRank / len(outLinks)
        yield fields[0], outLinks # emit outLinks list to reducer for this node
        for m in outLinks:
            yield m, prContrib

    def reducer(self, m, values):
        s = 0
        for val in values:
            if (isinstance(val, list)): # one of these should be received for each m
                outLinks = val
            else:
                s += val
        pageRank = s * 0.85 + 0.15 / 11
        record = ()
        for i in outLinks:
            record += (i, )
        yield None, m + ' ' + str(pageRank) + ' ' + ' '.join(record)

    def steps(self) :
        # Repeat the same map-reduce phase NITER times
        step = MRStep(mapper=self.mapper, reducer=self.reducer)
        return [step] * NITER

if __name__ == '__main__':
    MRPageRank.run()
