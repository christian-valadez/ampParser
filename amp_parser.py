import csv
import sys
import numpy as np
import math
import os.path
#todo: add scoring, and fix newline/spacing
=
class AMP_Parser:


	def __init__(self, info_file):
		self.names = []
		self.numtasks = []
		self.cats = []
		self.indices = []
		self.numblocks = 7
		self.read_info(info_file)

	def read_info(self, info_file):
		default_name = "Part"
		default_numtasks = 10
		default_cats = 1
		try:
			f = open(info_file, 'r')
		except:
			print "Error: IAT property file " +info_file+" doesn't exist. Quitting parser..."
			sys.exit(1)

		print "Reading in IAT properties..."
		csv_reader = csv.reader(f)
		for row in csv_reader:
			self.names.append(row[0]) if (len(row) > 0) else self.names.append(default_name)
			self.numtasks.append(int(row[1])) if (len(row) > 1) else self.numtasks.append(default_numtasks)
			self.cats.append(int(row[2])) if (len(row) > 2) else self.cats.append(default_cats)
		self.numblocks = len(self.names)
		f.close()

	def parse_file(self, infile, outfile):
		try:
			fin = open(infile, 'rb')
		except:
			print "Error: Input file "+infile+" does not exist. Quitting parser..."
			sys.exit(1)
		try:
			fout = open(outfile, 'wb')
		except:
			print "Error: cannot create output file "+outfile+". Quitting parser..."
			sys.exit(1)

		print "Parsing file..."
		csv_reader = csv.reader(fin)
		csv_writer = csv.writer(fout)
		head1 = csv_reader.next()
		head2 = csv_reader.next()
		self.parse_header(head1)
		csv_writer.writerow(head1 + ['Parsed IAT Results'])
		csv_writer.writerow(head2 + self.generate_subheader())
		for row in csv_reader:
			csv_writer.writerow(row + self.parse_row(row))

		print "Parsing complete!"
		fin.close()
		fout.close()

	def parse_header(self, head1):
		for name in self.names:
			try:
				self.indices.append(head1.index(name))
			except:
				print "Warning: no IAT section called "+name+" exists"
				self.indices.append(None)

	def generate_subheader(self):
		header = []
		for i in range(0, self.numblocks):
			sections = []
			for j in range(0, self.numtasks[i]):
				rootname = self.names[i]+" Task "+str(j+1)+" "
				sections += [rootname+"Target", rootname+"Correct", rootname+"Latency"]
			header += sections
		header += ['IsValid']

		stage_header = []
		stage_header += ['Num_Valid_Responses','Num_CorrectResponses', 'Num_IncorrectResponses']
		stage_header += ['Mean_CorrectLatencies','Stdev_CorrectLatencies']
		stage_header += ['Mean_Raw', 'Stdev_Raw']
		stage_header += ['Mean_V1', 'Stdev_V1']
		stage_header += ['Mean_V2', 'Stdev_V2']

		for i in range(0, self.numblocks):
			for head in stage_header:
				header.append('Block '+str(i+1)+'_'+head)

		if (self.numblocks == 7): #use standard IAT scoring
			header += ['DScore_Raw','DScore_V1','DScore_V2']
		return header

	def parse_row(self, row):
		result = []
		for i in range(0,self.numblocks):
			block = row[self.indices[i]].split(',')
			block_result = ['']*(self.numtasks[i]*3)
			#if (len(block) > self.numtasks[i] + 1):
			#	print len(block), self.numtasks[i], block
			for j in range(0, min(len(block) - 1,self.numtasks[i])):
				target, correct, latency = self.parse_result(block[j])
				if (self.cats[i] == 2):
					target = 'CatX_'+target if (j%2 == 0) else 'CatY_'+target
				block_result[3*j] = target
				block_result[3*j + 1] = correct
				block_result[3*j + 2] = latency
			result += block_result
		result += self.score_row(row)
		return result


	def parse_result(self, result):
		stats = result.split('.')
		target = stats[0]+'A' if (int(stats[2])) else stats[0]+'B'
		correct = 'true' if (stats[1]=='C') else 'false'
		latency = stats[3]
		return target, correct, latency

def main():

	info_file = ""
	infile = ""
	outfile = ""
	infile = raw_input("Enter the name of your input.csv file: ") if (len(sys.argv) < 2) else sys.argv[1]
	outfile = raw_input("Enter the name of your output.csv file: ") if (len(sys.argv) < 3) else sys.argv[2]
	info_file = raw_input("Enter the name of the file specifying the properties of this IAT: ") if (len(sys.argv) < 4) else sys.argv[3]
	if (os.path.isfile(outfile)):
		print "Error: your output file already exists and probably shouldn't be overwritten. Quitting parser..."
		sys.exit(1)
	amp_parser = AMP_Parser(info_file)
	amp_parser.parse_file(infile,outfile)

if __name__ == "__main__":
    main()
