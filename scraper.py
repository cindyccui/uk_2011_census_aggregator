import scraperwiki

# Blank Python

import csv
import re
import numpy as np

print 'Reading Office of National Statistics lookup table data.'
data = scraperwiki.scrape("http://www.ons.gov.uk/ons/external-links/other-ns-online/census-geography/further-lookup/index.html")
#reader = csv.reader(open('PCD11_OA11_LSOA11_MSOA11_LAD11_EW_LU.csv', 'rb'), delimiter=',')
reader = csv.reader(data, delimiter=',')
reader.next() # Skip line
rows = [row for row in reader]
print ' '


print 'Creating postcode to output area lookup table.' # Currently the bottleneck
p = re.compile('[A-Z]+') # This regex pulls out the first two (or one) letters of the postcode.
postcode_oacode_dict = {}
for row in rows:
        postcode = row[0]
        oacode = row[2]
        m = p.match(postcode)
        postcode_area = m.group()

        try:
                if oacode not in postcode_oacode_dict[postcode_area]:
                        postcode_oacode_dict[postcode_area].append(oacode)
        except KeyError:
                postcode_oacode_dict[postcode_area] = [oacode]

npostcodeareas = len(postcode_oacode_dict.keys())
print 'Number of postcode areas = ',npostcodeareas
print ' '


print 'Reading Geolytix Census data'
reader = csv.reader(open('Census11Data.txt', 'rb'), delimiter='\t')
headers = reader.next() # Skip header
censusdata = [row for row in reader]
ncensusvariables = len(censusdata[0][4:]) # Dropping first four columns (OAID OA popX popY)
print 'Number of census variables = ',ncensusvariables
print ' '


print 'Creating output area code to census row lookup table.'
oacode_row_dict = {}
for row in censusdata:
        oacode = row[1]
        rownumber = row[0]
        oacode_row_dict[oacode] = int(rownumber)
print ' '


print 'Summing output area census data in postcode areas.'
output_data = []
out = csv.writer(open("census_by_postcodearea.csv","w"), delimiter=',',quotechar=' ')
out.writerow(['PostArea']+headers[4:])
for postcode in postcode_oacode_dict.keys():
        postcodetotal = np.zeros(ncensusvariables)
        for oacode in postcode_oacode_dict[postcode]:
                rownumber = oacode_row_dict[oacode]
                data = censusdata[rownumber][4:]
                data = [w.replace('-1', '0') for w in data]
                postcodetotal += np.array(map(float, data))
        out.writerow( [postcode] + postcodetotal.astype(int).tolist() )