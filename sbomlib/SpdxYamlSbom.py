
from os import fpathconf
from typing import OrderedDict

from .GenericSbom import GenericSbom
from .SbomTypes import * 

import yaml


class SpdxYamlSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None
    fileName = None



    def parse_packages(self, inp):

        for pkg in inp:
            p = Package()

            p.id = pkg['SPDXID']

            p.name = pkg['name']

            if 'checksums' in pkg:
                
                p.hashes = []

                for chk in pkg['checksums']:
                    h = Hash()
                    h.algo = chk['algorithm']
                    h.value = chk['checksumValue']
                    p.hashes.append(h)

            if 'packageVerificationCode' in pkg:
                p.hashes = []
                h = Hash()
                h.value = pkg['packageVerificationCode']['packageVerificationCodeValue']
                h.algo = 'sha1'
                p.hashes.append(h)

            if 'versionInfo' in pkg:
                p.version = pkg['versionInfo']
                
            self.packages.append(p)


    def parse_files(self, inp):

        for fil in inp:
            f = File()

            f.id = fil['SPDXID']

            if 'fileName' in fil:
                f.name = fil['fileName']
            else:
                print('{} does not have filename!'.format(f.id))

            if 'checksums' in fil:
                f.hashes = []

                for chk in fil['checksums']:
                    h = Hash()
                    
                    h.algo = chk['algorithm']
                    h.value = chk['checksumValue']

                    f.hashes.append(h)

            self.files.append(f)

    def parse_relationships(self, inp):

        for rel in inp:
            r = Relationship()

            r.fromId = rel['spdxElementId']
            r.toId = rel['relatedSpdxElement']
            r.type = rel['relationshipType']

            self.relationships.append(r)


    def __init__(self, infile):
        
        self.fileName = infile

        with open(infile) as fh:

            res = yaml.safe_load(fh)

            p = FinalProduct()
            
            p.name = res['name']

            creat = res['creationInfo']
            
            if 'created' in creat:
                p.creationDate = creat['created']


            if 'creators' in creat:
                p.sbomAuthor = ','.join(creat['creators'])

            self.product = p

            if 'packages' in res:
                self.packages = []
                self.parse_packages(res['packages'])
            
            if 'files' in res:
                self.files = []
                self.parse_files(res['files'])

            if 'relationships' in res:
                self.relationships = []
                self.parse_relationships(res['relationships'])

            

