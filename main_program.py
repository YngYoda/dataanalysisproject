from scipy import integrate
import math
inf = float("infinity")
e = 2.71828
pie = math.pi

keywords = {}
keywords["AG.LND.TOTL.K2"] = ["land", "area", "square", "kilometer", "sq.","hectare", "acre", "acres", "hectares"]
keywords["BN.KLT.DINV.CD"] = ["foreign" , "direct", "investment", "net", "BoP", "trade"]
keywords["BX.GSR.MRCH.CD"] = ["goods", "export", "united", "states" ,"trade"]
keywords["EG.ELC.PROD.KH"] = ["electricity", "production" ,"electric", "kWh", "kilo", "watt","hour"]
keywords["EN.ATM.CO2E.KT"] = ["co2", "carbon", "dioxide", "emission", "CO2"]
keywords["EP.PMP.DESL.CD"] = ["diesel", "fuel", "price", "pump"]
keywords["FP.CPI.TOTL.ZG"] = ["inflation", "Inflation", "consumer", "price", "index", "prices"]
keywords["IT.NET.USER.P2"] = ["internet", "users", "user", "per 100" ]
keywords["NY.GDP.MKTP.CD"] = ["gross", "domestic", "product", "GDP"]
keywords["SP.DYN.LE00.IN"] = ["life", "expectancy", "birth"]
keywords["SP.POP.TOTL"] = ["population" , "census" ]


def gaussian(x , mu , sigma) :
	return pow(e , (-1) * pow(x - mu , 2) / (2 * pow(sigma , 2))) / (sigma * pow(2 *float(pie) , 0.5))

def mean(l) :
	xbar = 0
	for x in range(0 , len(l)) :
		xbar = xbar + float(l[x])
	return (xbar * 1.0) /len(l)

def stdev(l) :
	xbar = mean(l)
	stdev = 0
	for x in range(0 , len(l)) :
		stdev = stdev + pow((float(l[x]) - xbar) , 2)
	return pow((stdev * 1.0) / (len(l) - 1) , 0.5)

#return P(Z > t) assuming t > 0
def p_normal(t) :
	args = (0 , 1)
	z= integrate.quad(gaussian , t , inf , args)
	return z[0]

#return P(|Z| > |T|)
def prob(value, l) :
	diff = inf
	mark = inf
	for item in l:
		temp = float(item) - float(value)
		if temp<0:
			temp = -1 * temp
		if temp<diff:
			diff = temp
			mark = float(item)
	if mark == 0:
		return 0
	return ((diff*1.0)/mark)*100.0


input_file = open('countries_id_map.txt' , 'r')

country_map={}
for line in input_file:
	words = line.split('\t')
	country_map[words[0]] = words[1].strip()
'''
for key , value in country_map.items():
	print key ,"->",value
'''

input_file.close()

facts= {}
dataset_file = open('kb-facts-train_SI.tsv' , 'r')
for line in dataset_file:
	words = line.split('\t')
	if words[0] not in facts:
		facts[words[0]] = {}
	if words[2] not in facts[words[0]]:
		facts[words[0]][words[2]] = []
	facts[words[0]][words[2]].append(words[1])
dataset_file.close()

		
#print facts

data = {}
for key, value in facts.items():
	if key not in data:
		data[key] = {}
	for key2, value2 in value.items():
		if key2 not in data[key]:
			data[key][key2] = []
		#print key2
		if key2.strip() == "BN.KLT.DINV.CD":
			for i in range(0,len(value2)):
				if value2[i][0:1] == '-':
					value2[i] = value2[i][1:]
		data[key][key2].append(mean(value2))
		data[key][key2].append(stdev(value2))
		data[key][key2].append(len(value2))
'''
facts_writer = open('facts.txt' , 'w')
for key,value in facts.items():
	facts_writer.write(key)
	for key2, value2 in value.items():
		facts_writer.write( "->"+ key2)
		for item in value2:
  			facts_writer.write("%s\n" % item)
  		facts_writer.write("%s " % data[key][key2][0])
  		facts_writer.write("%s\n" % data[key][key2][1])
'''
alpha = 50.0
dataset_sentences = open('sentences.tsv' , 'r')
for line in dataset_sentences:
	line = line.strip()
	words = line.split('\t')
	numbers_done=[]
	for numbers in words[2].split(','):
		if numbers not in numbers_done:
			countries_done=[]
			for countries in words[3].replace(' ','').split(','):
				if countries not in countries_done:
					countries.strip()
					if countries == 'Israeli':
						countries = 'Israel'
					if countries == 'US':
						countries = 'USA'
					if countries == 'British':
						countries = 'England'
					if countries == 'Australian':
						countries = 'Australia'
					
					for key3, values3 in country_map.items():
						if values3 == countries:
							if key3 in data:
								for key, values in facts[key3].items():
									key = key.replace('\n','')						
									if numbers == '':
										break
									flag = False
									for word in  words[1].split():
										if word in keywords[key]:
											flag = True
									if  flag == True and prob(numbers , values) < alpha:
										print words[0] +'\t'+countries +'\t'+ key +'\t'+ numbers +'\t'+ "SCORE_" +"%.2f" % (100-prob(numbers , values))+"%"
					countries_done.append(countries)
			numbers_done.append(numbers)
dataset_sentences.close()


