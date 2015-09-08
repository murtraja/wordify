false = False
jsonfile = open('json_words.txt','r')
import json
string = jsonfile.read()
string = json.loads(string)
output = ''
wordfile = open('grewords.txt','w+')
i=0
for word in string:
	output = word['word'] +"-->" + word['definition'] + '\n'
	try:
		wordfile.write(output)
	except:
		print "could not write the word",word['word']
	i +=1
	#print i,":",word['word']
print "processed",i,"words!"
wordfile.close()
jsonfile.close()