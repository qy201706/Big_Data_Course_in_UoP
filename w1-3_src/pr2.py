from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import RawValueProtocol

NITER = 50
N = 11
initPageRank = 1 / N

class MRPageRank(MRJob): 

    OUTPUT_PROTOCOL = RawValueProtocol
        # Default for input; use here for output so we can "input our output"

    def preMapper(self, key, value):

        if len(value) == 0 or value [0] == '#':
            return

        fields = value.split()
        fromNode = fields [0]
        toNode   = fields [1]

        yield toNode, None
        yield fromNode, toNode

    def preReducer(self, mId, values):

        outLinks = []
        for val in values :
            if not (val is None) :
                outLinks.append(val)

        yield None, mId + " " + str(initPageRank) + " " + " ".join(outLinks)


    def intermapper(self, key, line):

        fields = line.split()
        myId  = fields [0]      # ID of this page

        yield myId, line        # forward directly to interreducer for output

        if(len(fields) == 2) :  # dangling node
            pageRank = float(fields [1])   # current pagerank of this page
            yield "accDangling", pageRank

    def interreducer(self, mId, values):

        if mId == "accDangling" :
            s = sum(values)
            yield None, "accDangling " + str(s)
        else :
            # Should only receive one value, from first yield in intermapper
            line = next(values)
            yield None, line


    def mapper(self, key, value):

        fields = value.split()
        myId     = fields [0]         # ID of this page
        pageRank = float(fields [1])  # current pagerank of this page

        if myId == "accDangling" :
            p = pageRank / N
            for i in range(N) :
                yield str(i + 1), p   # to be shared amongst *all N* nodes
        else :
            outLinks = fields [2:]    # outgoing links of this page

            yield myId, outLinks

            nOutLinks = len(outLinks)
            if(nOutLinks > 0) :
                prContrib = pageRank / nOutLinks
                for mId in outLinks :
                    yield mId, prContrib

    def reducer(self, mId, values):
        s = 0
        for val in values :
            if(isinstance(val, list)) :
                mOutLinks = val  # From "outLinks" yield in mapper above
            else :
                s += float(val)

        mPageRank = s * 0.85 + 0.15 / N
        yield None, mId + " " + str(mPageRank) + " " + " ".join(mOutLinks)


    def steps(self) :
        # preprocessing, then N times "inter" MR followed by "main" MR
        pre   = MRStep(mapper=self.preMapper, reducer=self.preReducer)
        inter = MRStep(mapper=self.intermapper, reducer=self.interreducer)
        step  = MRStep(mapper=self.mapper, reducer=self.reducer)
        return [pre] + [inter, step] * NITER

if __name__ == '__main__':
    MRPageRank.run()
