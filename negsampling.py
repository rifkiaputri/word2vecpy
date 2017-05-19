import math
import numpy as np


class VocabItem:
    def __init__(self, word):
        self.word = word
        self.count = 0
        self.path = None # Path (list of indices) from the root to the word (leaf)


class Vocab:
    def __init__(self, fi, min_count):
        vocab_items = []
        vocab_hash = {}
        word_count = 0
        fi = open(fi, 'r', encoding='utf8')

        # Add special tokens <bol> (beginning of line) and <eol> (end of line)
        for token in ['<bol>', '<eol>']:
            vocab_hash[token] = len(vocab_items)
            vocab_items.append(VocabItem(token))

        for line in fi:
            tokens = line.split()
            for token in tokens:
                if token not in vocab_hash:
                    vocab_hash[token] = len(vocab_items)
                    vocab_items.append(VocabItem(token))
                    
                #assert vocab_items[vocab_hash[token]].word == token, 'Wrong vocab_hash index'
                vocab_items[vocab_hash[token]].count += 1
                word_count += 1
            
                if word_count % 10000 == 0:
                    print('Reading word %d' % word_count)

            # Add special tokens <bol> (beginning of line) and <eol> (end of line)
            vocab_items[vocab_hash['<bol>']].count += 1
            vocab_items[vocab_hash['<eol>']].count += 1
            word_count += 2

        self.bytes = fi.tell()
        self.vocab_items = vocab_items         # List of VocabItem objects
        self.vocab_hash = vocab_hash           # Mapping from each token to its index in vocab
        self.word_count = word_count           # Total number of words in train file

        # Add special token <unk> (unknown),
        # merge words occurring less than min_count into <unk>, and
        # sort vocab in descending order by frequency in train file
        self.__sort(min_count)

        #assert self.word_count == sum([t.count for t in self.vocab_items]), 'word_count and sum of t.count do not agree'
        print('Total words in training file: %d' % self.word_count)
        print('Total bytes in training file: %d' % self.bytes)
        print('Vocab size: %d' % len(self))

    def __getitem__(self, i):
        return self.vocab_items[i]

    def __len__(self):
        return len(self.vocab_items)

    def __iter__(self):
        return iter(self.vocab_items)

    def __contains__(self, key):
        return key in self.vocab_hash

    def __sort(self, min_count):
        tmp = []
        tmp.append(VocabItem('<unk>'))
        unk_hash = 0
        
        count_unk = 0
        for token in self.vocab_items:
            if token.count < min_count:
                count_unk += 1
                tmp[unk_hash].count += token.count
            else:
                tmp.append(token)

        tmp.sort(key=lambda token : token.count, reverse=True)

        # Update vocab_hash
        vocab_hash = {}
        for i, token in enumerate(tmp):
            vocab_hash[token.word] = i

        self.vocab_items = tmp
        self.vocab_hash = vocab_hash

        print('Unknown vocab size:', count_unk)

    def indices(self, tokens):
        return [self.vocab_hash[token] if token in self else self.vocab_hash['<unk>'] for token in tokens]


class UnigramTable:
    """
    A list of indices of tokens in the vocab following a power law distribution,
    used to draw negative samples.
    """
    def __init__(self):
        filename = 'enwik8'
        vocab = Vocab('data/%s' % filename, 1)
        power = 0.75
        norm = sum([math.pow(t.count, power) for t in vocab]) # Normalizing constant

        table_size = int(1e8) # Length of the unigram table
        table = np.zeros(table_size, dtype=np.uint32)

        print ('Filling unigram table')
        p = 0 # Cumulative probability
        i = 0
        fi = open('data/vocab-list-%s.txt' % filename, 'w', encoding='utf8')
        for j, unigram in enumerate(vocab):
            fi.write('%d - %s\n' % (j, unigram.word)) # This is for checking vocab parsing result
            p += float(math.pow(unigram.count, power))/norm
            while i < table_size and float(i) / table_size < p:
                table[i] = j
                i += 1
        self.table = table
        self.vocab = vocab
        fi.close()

    def sample(self, count):
        """
        :param count: the number of samples to return.
        :return: array of index in vocabulary item list.
        """
        indices = np.random.randint(low=0, high=len(self.table), size=count)
        return [self.table[i] for i in indices]

    def get_word_by_index(self, idx):
        """
        :param idx: index of the word.
        :return: word based on the index. Word will be returned in string type.
        """
        return self.vocab.vocab_items[idx].word
