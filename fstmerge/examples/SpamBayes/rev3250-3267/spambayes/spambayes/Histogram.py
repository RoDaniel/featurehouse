import math

from spambayes.Options import options

class  Hist :
	"""Simple histograms of float values."""
	    def __init__(self, nbuckets=options["TestDriver", "nbuckets"],
                 lo=0.0, hi=100.0):

        self.lo, self.hi = lo, hi

        self.nbuckets = nbuckets

        self.buckets = [0] * nbuckets

        self.data = []  

        self.stats_uptodate = False
 def add(self, x):

        self.data.append(x)

        self.stats_uptodate = False
 def compute_stats(self):

        if self.stats_uptodate:

            return

        self.stats_uptodate = True

        data = self.data

        n = self.n = len(data)

        if n == 0:

            return

        data.sort()

        self.min = data[0]

        self.max = data[-1]

        if n & 1:

            self.median = data[n // 2]

        else:

            self.median = (data[n // 2] + data[(n-1) // 2]) / 2.0

        if data[0] < 0.0:

            temp = [(abs(x), x) for x in data]

            temp.sort()

            data = [x[1] for x in temp]

            del temp

        sum = 0.0

        for x in data:

            sum += x

        mean = self.mean = sum / n

        var = 0.0

        for x in data:

            d = x - mean

            var += d*d

        self.var = var / n

        self.sdev = math.sqrt(self.var)

        self.pct = pct = []

        for p in options["TestDriver", "percentiles"]:

            assert 0.0 <= p <= 100.0

            i = (n-1)*p/1e2

            if i < 0:

                score = data[0]

            else:

                whole = int(i)

                frac = i - whole

                score = data[whole]

                if whole < n-1 and frac:

                    score += frac * (data[whole + 1] - score)

            pct.append((p, score))
 def __iadd__(self, other):

        self.data.extend(other.data)

        self.stats_uptodate = False

        return self
 def get_lo_hi(self):

        self.compute_stats()

        lo, hi = self.lo, self.hi

        if lo is None:

            lo = self.min

        if hi is None:

            hi = self.max

        return lo, hi
 def get_bucketwidth(self):

        lo, hi = self.get_lo_hi()

        span = float(hi - lo)

        return span / self.nbuckets
 def fill_buckets(self, nbuckets=None):

        if nbuckets is None:

            nbuckets = self.nbuckets

        if nbuckets <= 0:

            raise ValueError("nbuckets %g > 0 required" % nbuckets)

        self.nbuckets = nbuckets

        self.buckets = buckets = [0] * nbuckets

        lo, hi = self.get_lo_hi()

        bucketwidth = self.get_bucketwidth()

        for x in self.data:

            i = int((x - lo) / bucketwidth)

            if i >= nbuckets:

                i = nbuckets - 1

            elif i < 0:

                i = 0

            buckets[i] += 1
 def display(self, nbuckets=None, WIDTH=61):

        if nbuckets is None:

            nbuckets = self.nbuckets

        if nbuckets <= 0:

            raise ValueError("nbuckets %g > 0 required" % nbuckets)

        self.compute_stats()

        n = self.n

        if n == 0:

            return

        print("%d items; mean %.2f; sdev %.2f" % (n, self.mean, self.sdev))

        print("-> <stat> min %g; median %g; max %g" % (self.min,
                                                       self.median,
                                                       self.max))

        pcts = ['%g%% %g' % x for x in self.pct]

        print("-> <stat> percentiles:", '; '.join(pcts))

        lo, hi = self.get_lo_hi()

        if lo > hi:

            return

        self.fill_buckets(nbuckets)

        biggest = max(self.buckets)

        hunit, r = divmod(biggest, WIDTH)

        if r:

            hunit += 1

        print("* =", hunit, "items")

        ndigits = len(str(biggest))

        bucketwidth = self.get_bucketwidth()

        whole_digits = max(len(str(int(lo))),
                           len(str(int(hi - bucketwidth))))

        frac_digits = 0

        while bucketwidth < 1.0:

            frac_digits += 1

            bucketwidth *= 10.0

        format = ("%" + str(whole_digits + 1 + frac_digits) + '.' +
                  str(frac_digits) + 'f %' + str(ndigits) + "d")

        bucketwidth = self.get_bucketwidth()

        for i in range(nbuckets):

            n = self.buckets[i]

            print(format % (lo + i * bucketwidth, n), end=' ')

            print('*' * ((n + hunit - 1) // hunit))



