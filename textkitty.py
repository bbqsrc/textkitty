import string
import re

from collections import Counter
from io import StringIO
from glob import glob

class NgramCounter(Counter):
	def dumps(self, count=300):
		out = StringIO()
		for word, count in self.most_common(count):
			out.write("%s\t%s\n" % (word, count))
		return out.getvalue()
		
	def dump(self, f, count=300):
		f.write(self.dumps(count))

	@classmethod
	def loads(cls, input):
		counter = cls()
		for line in input.split('\n'):
			#print(line)
			word, count = line.split('\t')
			count = int(count)
			counter[word] = count
		return counter

	@classmethod
	def load(cls, f):
		counter = cls.loads(f.read().strip())
		return counter

def make_profile(fin, fout):
	FrequencyProfile(fin).dump(fout)

class FrequencyProfile(NgramCounter):
	N = range(1, 5+1)
	MAX_NGRAMS = 300

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
		self.profiles = {}
		for fn in glob('*.profile.txt'):
			self.profiles[fn.split('.profile.txt')[0]] = FrequencyProfile.load(open(fn))
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


