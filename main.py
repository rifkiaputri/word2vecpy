import negsampling

def main():
    table = negsampling.UnigramTable()
    sample = table.sample(1)
    print(sample)
    print(table.get_word_by_index(sample[0]))


if __name__ == '__main__':
    main()
