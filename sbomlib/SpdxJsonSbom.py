from .GenericSbom import GenericSbom
from .SbomTypes import * 
import json

class SpdxJsonSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None

    def get_packages(self):
        return self.packages

    def get_files(self):
        return self.files
    
    def get_final_product(self):
        return self.product


    def nodeToPackage(self, pkg):
        p = Package()
        
        p.id = pkg['SPDXID']
        p.name = pkg['name']

        if 'versionInfo' in pkg:
            p.version = pkg['versionInfo']
        
        if 'supplier' in pkg:
            p.supplierName = pkg['supplier']
        
        return p
        

    def nodeToRelationship(self, rel):
        r = Relationship()

        r.fromId = rel['spdxElementId']
        r.toId = rel['relatedSpdxElement']
        r.type = rel['relationshipType']

        return r

    def nodeToFile(self, fil):
        
        f = File()

        f.name = fil['fileName']
        f.id = fil['SPDXID']

        if 'checksums' in fil:
            hashes = []
            for cc in fil['checksums']:
                h = Hash()
                h.algo = cc['algorithm']
                h.value = cc['checksumValue']
                hashes.append(h)
            f.hashes = hashes

        return f


    def __init__(self, infile):
        self.fileName = infile
        with open(infile) as fh:
            data = json.load(fh)

            if 'packages' in data:
                self.packages = []
                for p in data['packages']:
                    self.packages.append(self.nodeToPackage(p))
            
            if 'relationships' in data:
                self.relationships = []
                for r in data['relationships']:
                    self.relationships.append(self.nodeToRelationship(r))
            
            
            if 'creationInfo' in data:
                ci = data['creationInfo']

                fp = FinalProduct()

                fp.name = data['name']
                
                if 'creators' in ci:
                    if isinstance(ci['creators'], list):
                        fp.sbomAuthor = ','.join(ci['creators'])
                
                if 'creator' in ci:
                    if isinstance(ci['creator'], list):
                        fp.sbomAuthor = ','.join(ci['creator'])


                if 'created' in ci:
                    fp.creationDate = ci['created']
                
                self.product = fp

            if 'files' in data:
                self.files = []
                for f in data['files']:
                    self.files.append(self.nodeToFile(f))
        
