
import glob,os,csv
strain_file = 'strain_ids.csv'

expected_strains = ['CNB440','CNB527','CNB536','CNH646','CNP193','CNQ748','CNR114','CNR894','CNR942','CNS055','CNS197','CNS205','CNS237','CNS863','CNT003','CNT005','CNT029','CNT138','CNT148','CNT150','CNT849','CNT851','CNT855','CNX508','CNY012','CNY202','CNY330']


hack_map = {'DSM45548':'CNT148','DSM45547':'CNT138','DSM45543':'CNS863','DSM45549':'CNT150'}

if __name__ == '__main__':
	in_dir = '/Users/simon/Dropbox/BioResearch/Meta_clustering/MS2LDA/BGC/scripts/bigscape/bigscape_refs_output_duncan_sel_c0.10';
	in_files = glob.glob(os.path.join(in_dir,'Network*.tsv'))


	strain_dict = {}
	with open(strain_file,'r') as f:
		reader = csv.reader(f)
		for line in reader:
			strain_dict[line[0]] = line[1]

	missing = {}
	unique_strains = {}
	for filename in in_files:
		with open(filename,'r') as f:
			reader = csv.reader(f,delimiter ='\t')
			heads = reader.next()
			for line in reader:
				accession = line[0].split('.')[0]
				if not accession.startswith('BGC'):
					stra = line[2].split()[2]
					if stra == 'DSM':
						stra += line[2].split()[3]
					if '-' in stra:
						stra = ''.join(stra.split('-'))
					if ',' in stra:
						stra = ''.join(stra.split(','))
					if stra in strain_dict.values():
						strain_dict[accession] = stra

					if not stra in strain_dict.values():
						if stra in hack_map:
							stra = hack_map[stra]
							strain_dict[accession] = stra
					unique_strains[stra] = True



	with open(strain_file,'w') as f:
		writer = csv.writer(f)
		for a,s in strain_dict.items():
			writer.writerow([a,s])


	us = set(unique_strains.keys())
	es = set(expected_strains)
	print len(us),len(es),len(us.intersection(es))
	print us - es
	print es - us

