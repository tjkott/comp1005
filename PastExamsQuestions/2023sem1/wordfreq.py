punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
filename = 'grimm.txt'
book = open(filename, 'r')
bookNoPunct = book.translate(str.maketrans('','', punctuation))
words = bookNoPunct.split()

wordfreq = {}