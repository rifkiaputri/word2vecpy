import negsampling

def main():
    # Initialize unigram table, it will read the input file in data directory.
    # The list of index in unigram table will be saved in self.table
    table = negsampling.UnigramTable()

    # Make negative samples, the returns will be the index of the word
    sample = table.sample(30)
    print(sample)

    for i in range(len(sample)):
        # You can use this function to get the words
        print(table.get_word_by_index(sample[i]))


if __name__ == '__main__':
    main()
