import re, pdb, sys, math

functionPunctuation = ' ,-'
contentPunctuation = '.?!\n'
punctuationCharacters = functionPunctuation+contentPunctuation

sentenceEndCharacters = '.?!'

class WordType:
	Content=0
	Function=1
	ContentPunctuation=2
	FunctionPunctuation=3

class Word:
	Text=''
	Type=''

class Sentence:
	Words = []

	def getFullSentence(self):
		text = ''
		for w in self.Words:
			text += w.Text
		return text.strip()

	def getReducedSentence(self):
		sentenceText = ''
		sentenceEnd = self.Words[len(self.Words)-1]
		contentWords = filter(lambda w: w.Type == WordType.Content, self.Words)
		i = 0
		while i < len(contentWords):
			w = contentWords[i]
			# upper case the first character of the sentence
			if i == 0:
				li = list(w.Text)
				li[0] = li[0].upper()
				w.Text = ''.join(li)
			sentenceText += w.Text
			if i < len(contentWords)-1:
				sentenceText += ' '
			elif sentenceEnd.Text != w.Text:
				sentenceText += sentenceEnd.Text
			i = i+1
		return sentenceText
			

class Paragraph:
	Sentences = []

def isContentPunctuation(text):
	for c in contentPunctuation:
		if text.lower() == c.lower():
			return True
	return False

def isFunctionPunctuation(text):
	for c in functionPunctuation:
		if text.lower() == c.lower():
			return True
	return False

def isFunction(text, stopWords):
	for w in stopWords:
		if text.lower() == w.lower():
			return True
	return False

def tag(sampleWords, stopWords):
	taggedWords = []
	for w in sampleWords:
		tw = Word()
		tw.Text = w
		if isContentPunctuation(w):
			tw.Type = WordType.ContentPunctuation
		elif isFunctionPunctuation(w):
			tw.Type = WordType.FunctionPunctuation
		elif isFunction(w, stopWords):
			tw.Type = WordType.Function
		else:
			tw.Type = WordType.Content
		taggedWords.append(tw)
	return taggedWords

def tokenize(text):
	return filter(lambda w: w != '', re.split('([{0}])'.format(punctuationCharacters), text))	

def getWords(sentenceText, stopWords):
	return tag(tokenize(sentenceText), stopWords) 

def getSentences(line, stopWords):
	sentences = []
	sentenceTexts = filter(lambda w: w != '', re.split('[{0}]'.format(sentenceEndCharacters), line))	
	sentenceEnds = re.findall('[{0}]'.format(sentenceEndCharacters), line)
	sentenceEnds.reverse()
	for t in sentenceTexts:
		if len(sentenceEnds) > 0:
			t += sentenceEnds.pop()
		sentence = Sentence()
		sentence.Words = getWords(t, stopWords)
		sentences.append(sentence)
	return sentences

def getParagraphs(lines, stopWords):
	paragraphs = []
	for line in lines:
		paragraph = Paragraph()
		paragraph.Sentences = getSentences(line, stopWords)
		paragraphs.append(paragraph)
	return paragraphs

class Graph:
	Vertices = []
	Edges = []

	def getRankedVertices(self):
		rankedVertices = []
		for v in self.Vertices:
			rank = 0
			for e in self.Edges:
				if e.Vertex1 == v or e.Vertex2 == v:
					rank = rank + e.Weight
			rankedVertices.append((v, rank))
		return sorted(rankedVertices, key=lambda x: x[1])
			

class Vertex:
	Sentence = None

class Edge:
	Vertex1 = None
	Vertex2 = None
	Weight = 0

def findWeight(sentence1, sentence2):
	weight = 0
	for w1 in filter(lambda w: w.Type == WordType.Content, sentence1.Words):
		for w2 in filter(lambda w: w.Type == WordType.Content, sentence2.Words):
			if w1.Text.lower() == w2.Text.lower():
				weight = weight + 1
	length1 = len(filter(lambda w: w.Type == WordType.Content, sentence1.Words))
	length2 = len(filter(lambda w: w.Type == WordType.Content, sentence2.Words))
	normalised1 = 0
	if length1 > 0:
		normalised1 = math.log(length1)
	normalised2 = 0
	if length2 > 0:
		normalised2 = math.log(length2)
	norm = normalised1 + normalised2
	if norm == 0:
		return 0
	return weight / float(norm)

def buildGraph(sentences):
	g = Graph()
	for s in sentences:
		v = Vertex()
		v.Sentence = s
		g.Vertices.append(v)
	for i in g.Vertices:
		for j in g.Vertices:
			if i != j:
				w = findWeight(i.Sentence, j.Sentence)
				e = Edge()
				e.Vertex1 = i
				e.Vertex2 = j
				e.Weight = w
				g.Edges.append(e)
	return g

def sentenceRank(paragraphs):
	sentences = []
	for p in paragraphs:
		for s in p.Sentences:
			sentences.append(s)
	g = buildGraph(sentences)
	return g.getRankedVertices()

sampleFile = sys.argv[1]
stopWordsFile = 'stopWords.txt'
stopWords= open(stopWordsFile).read().splitlines()

lines = open(sampleFile).read().splitlines()
contentLines = filter(lambda w: w != '', lines)

paragraphs = getParagraphs(contentLines, stopWords)

reductionRatio = 0.5
rankedSentences = sentenceRank(paragraphs)

orderedSentences = []
for p in paragraphs:
	for s in p.Sentences:
		orderedSentences.append(s)

reducedSentences = []
i = 0
while i < math.trunc(len(rankedSentences) * reductionRatio):
	s = rankedSentences[i][0].Sentence
	position = orderedSentences.index(s)
	reducedSentences.append((s, position))
	i = i + 1
reducedSentences = sorted(reducedSentences, key=lambda x: x[1])

for s,r in reducedSentences:
	print(s.getFullSentence())

