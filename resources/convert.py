import json

with open('clist.txt') as f:
	text = f.read()

lines = text.split('\n')
clist = []

for line in lines:
	sections = line.split(', ')
	word = sections[0][6:]
	start = sections[1][12:]
	end = sections[2][10:]
	clist.append({'start':start, 'end':end, 'word':word})

# Export clist to json

with open('clist.json', 'w') as outfile:
    json.dump(clist, outfile)