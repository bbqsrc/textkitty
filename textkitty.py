import bz2
import gzip
import os
import re
import string

from collections import Counter
from glob import glob
from io import StringIO
from os.path import basename, join as pjoin


class NgramCounter(Counter):
	def dumps(self, c=None):
		out = StringIO()
		for word, count in self.most_common(c):
			out.write("%s\t%s\n" % (word, count))
		return out.getvalue()
		
	def dump(self, f, c=None):
		f.write(self.dumps(c))

	@classmethod
	def loads(cls, input):
		counter = cls()
		for line in input.split('\n'):
			if isinstance(line, bytes):
				line = line.encode('utf-8')
			word, count = line.split('\t')
			counter[word] = int(count)
		return counter

	@classmethod
	def load(cls, f):
		counter = cls.loads(f.read().strip())
		return counter


def make_profile(fin, fout):
	FrequencyProfile(fin).dump(fout)


class FrequencyProfile(NgramCounter):
	N = range(1, 5+1)
	MAX_NGRAMS = 1000

	def __init__(self, f=None):
		if f is None:
			return

		def iter_ngrams(word):
			word = "_%s" % word
			
			for n in self.N:
				c = 0
				while c+n < len(word)+1:
					#print(n, word[c:c+n])
					self[word[c:c+n]] += 1
					c += 1
				word += "_"

		punc = re.sub("'", "", string.punctuation)
		page = re.sub(r"[%s]" % punc, "", f.read())
		for word in page.split():
			#print(word)
			if not re.search("[0-9]", word):
				iter_ngrams(word)
		
	def get_place_order(self, count=None):
		if count is None:
			count = self.MAX_NGRAMS
		counter = Counter()
		c = 0
		last = None
		for ngram, count in self.most_common(count):
			if count != last:
				c += 1
				last = count
			counter[ngram] = c
			if c >= self.MAX_NGRAMS:
				break

		return counter

	def write(self, fn):
		f = open(fn, 'w')
		self.dump(f)
		f.close()


class TextKitty(object):
	# XXX load all the frequencies in the path 
	def __init__(self, f):
		self.profiles = profiles
		self.scores = Counter()
		self.document = FrequencyProfile(f)

	def classify(self):
		# XXX do a path and shit
		self._find_distances()
		#print(self.scores)
		return self.scores.most_common()[-1][0]
		
	def _find_distances(self):
		max_out_of_place = self.document.MAX_NGRAMS
		doc = self.document.get_place_order()
		for profile, ngrams in self.profiles.items():
			
			for ngram, count in ngrams.get_place_order().items():
				doc_ngram = doc.get(ngram)
				
				if doc_ngram is None:
					self.scores[profile] += max_out_of_place
				else:
					self.scores[profile] += abs(doc_ngram - count)

	def meow(self):
		print("KITTY GOES MEOW.")


def classify(text):
	return TextKitty(StringIO(text)).classify()

# GLOBALS
path = [
	"/usr/share/textkitty/profiles",
	os.path.expanduser("~/.textkitty/profiles"),
	"./profiles",
	"."
]
profiles = {}
for d in path:
	for fn in glob(pjoin(d, "*.profile.txt*")):
		ftypes = {
			"bz2": bz2.BZ2File,
			"gz": gzip.GzipFile,
			"txt": open
		}
		try:
			f = ftypes.get(fn.split('.')[-1])(fn, 'r')
			profiles[basename(fn.split('.profile.txt')[0])] = FrequencyProfile.load(f)
		except IOError:
			print("Unexpected filetype for file: %s. Continuing." % fn)


