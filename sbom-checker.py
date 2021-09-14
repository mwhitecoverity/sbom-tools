import json
from terminaltables import AsciiTable

counts = {}


def do_inc(val):
    global counts

    if val in counts:
        counts[val] = counts[val] + 1
    else:
        counts[val] = 1


explanations = {
    'bom':'Total # SBOMs found',
    'got_final_product':'Final product info was found',
    'sbom_author': 'SBOM has an author',
    'sbom_created': 'SBOM has a creation date',
    'relationships':'SBOM has relationships',
    'files':'SBOM has file-level resolution',
    'sbom_target':'SBOM has \'sbom of what\' declared',
    'packages_with_hashes':'SBOM has hashes at the component/package layer',

    'only one relationship':'SBOM has only one relationship',

    'only two relationships':'SBOM has only two relationship',
    'only one package':'SBOM has only one package',
    'files_with_hashes': 'File entries which have hashes',
    'packages':'SBOM packages found',
    'packages_with_names':'SBOM packages which have the expected name fields',
    'packages_with_ids':'SBOM packages which have the expected ID fields',

    'packages_with_suppliers':'SBOM packages that have supplier names',
    'SpdxJsonSbom': 'SPDX JSON Format',
    'SpdxTvSbom': 'SPDX Tag-Value Format',
    'CdxXmlSbom': 'Cyclone DX XML Format',
    'CdxJsonSbom': 'Cyclone DX JSON Format',
    'NTIA-Supplier-Name': 'All components have supplier names',
    'NTIA-Component-Name': 'All components have names',
    'NTIA-Unique-Identifier': 'All components have unique identifiers',
    'NTIA-SBOM-Author': 'SBOM has an overall author',
    'NTIA-Version-String': 'Components have a version identifier',
    'NTIA-Relationships-Exist': 'Relationships exist',
    'NTIA-SBOM-Timestamp': 'SBOM has a creation timestamp'

}

with open('sbom-report.json') as fh:
    rpt = json.load(fh)

    k = set()

    total = len(rpt)
    if total == 0:
        pass

    print('{} SBOMs'.format(len(rpt)))

    
    for row in rpt:
        l = row.keys()
        for k in l:
            val = row[k]
            
            if k == 'type':
                do_inc(val)
            elif val is None or val == 0:
                pass
            else:
                do_inc(k)

        print(row)
        if 'relationships' in row:
            do_inc('NTIA-Relationships-Exist')

            if row['relationships'] == 1:
                do_inc('only one relationship')
            if row['relationships'] == 2:
                do_inc('only two relationships')

        if 'packages' in row:
            if row['packages'] == 1:
                do_inc('only one package')
            
            for pd in row['packages']:
                if 'id' in pd:
                    do_inc('NTIA-Unique-Identifier')
                if 'version' in pd:
                    do_inc('NTIA-Version-String')
                if 'name' in pd:
                    do_inc('NTIA-Component-Name')
                if 'supplier' in pd:
                    do_inc('NTIA-Supplier-Name')
    
        if 'product' in row:
            if 'sbomAuthor' in row['product']:
                do_inc('NTIA-SBOM-Author')
            if 'creationDate' in row['product']:
                do_inc('NTIA-SBOM-Timestamp')

        

           

    table =  [ ['Key', 'Explanation', 'Count', '%' ] ]

    for k in counts:
        table.append([k, explanations.get(k), counts[k], round(counts[k]/total * 100 )])

    print(AsciiTable(table).table)