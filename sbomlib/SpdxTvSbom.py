from .GenericSbom import GenericSbom
from .SbomTypes import * 

class SpdxTvSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None

    def consumeFile(self, fil):
        f = File()

        f.name = fil['FileName']

        f.id = fil['SPDXID']

        for a in ['MD5', 'SHA1', 'SHA256']:
            if a in fil:
                if f.hashes is None:
                    f.hashes = []
                h = Hash()
                h.algo = a
                h.value = fil[a]
                f.hashes.append(h)
        
        return f


    def consumePackage(self, pkg):
        p = Package()
        
        p.id = pkg['SPDXID']
        p.name = pkg['PackageName']

        if 'PackageVersion' in pkg:
            p.version = pkg['PackageVersion']
        
        if 'PackageSupplier' in pkg:
            p.supplierName = pkg['PackageSupplier']
        
        if 'PackageChecksum' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = Hash()
            h.algo = 'SHA1' # default type
            h.value = pkg['PackageChecksum']
            p.hashes.append(h)
        
        if 'MD5' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = Hash()
            h.algo = 'MD5' 
            h.value = pkg['MD5']
            p.hashes.append(h)

        if 'SHA1' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = Hash()
            h.algo = 'SHA1' 
            h.value = pkg['SHA1']
            p.hashes.append(h)

        if 'SHA256' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = Hash()
            h.algo = 'SHA256' 
            h.value = pkg['SHA256']
            p.hashes.append(h)

        return p
        



    def __init__(self, infile):
        self.fileName = infile

        with open(infile) as fh:
            inTextTag = False
            fragment = {}
            fragments = []
            lastk = None

            for ln in fh.readlines():
                if ln.startswith("#") and not inTextTag:
                    if(len(fragment)> 0):
                        
                        fragments.append(fragment)
                        fragment = {}
                else:
                    ln = ln.strip()
                    
                    #print (len(ln))
                    if(len(ln) == 0 and not inTextTag):
                        if len(fragment) > 0:
                            fragments.append(fragment)
                            fragment = {}
                            #print('ending fragment: ')
                            #print(fragment)
                        continue

                    if not inTextTag:
                        if ':' in ln:
                            k, v = ln.split(':',1)

                            v = v.strip()

                            if k == 'PackageName':
                                #print("{} / {}".format(k, v))
                                pass

                            if k == 'Relationship':
                                if self.relationships == None:
                                    self.relationships = []

                                r = Relationship()
                                r.fromId, r.type, r.toId = v.split(' ', 2)

                                self.relationships.append(r)

                            elif k == 'PackageChecksum' or k == 'FileChecksum':
                                if ':' in v:
                                    algo, value = v.split(':')
                                    fragment[algo] = value.strip()
                            elif k == 'PackageVerificationCode':
                                if ':' in v:
                                    algo, value = v.split(':')
                                    fragment[algo] = value.strip()
                                else:
                                    fragment['SHA1'] = v.strip()
                            else:
                                fragment[k] = v
                                lastk = k

                            if '<text>' in v:
                                inTextTag = True
                                # if it also ends on same line
                                if '</text>' in v:
                                    inTextTag = False

                        else:
                            # assume continuation of last entry
                            #print(ln)
                            fragment[lastk] = fragment[lastk] + " " + ln    

                    else:
                        fragment[lastk] = fragment[lastk] + " " + ln
                        #print("in text: {} ".format(ln))
                        if '</text>' in ln:
                            #print("text ending: {}".format(ln))
                            inTextTag = False
            
            if(len(fragment)> 0):
                fragments.append(fragment)
                fragment = {}

            #print(fragments)

            packageDeDupe = set()
            for frag in fragments:
                if 'PackageName' in frag:
                    #print(frag)
                    if self.packages == None:
                        self.packages = []

                    foundPkg = self.consumePackage(frag)
                    #print(foundPkg.name)
                    if foundPkg.name not in packageDeDupe:
                        self.packages.append(foundPkg)
                        packageDeDupe.add(foundPkg.name)
                if 'DocumentName' in frag:
                    fp = FinalProduct()
                    fp.name = frag['DocumentName']

                    self.product = fp

                if 'Creator' in frag:
                    if self.product is not None:
                        if self.product.sbomAuthor is not None:
                            self.product.sbomAuthor = self.product.sbomAuthor + ',' + frag['Creator']
                        else:
                            self.product.sbomAuthor = frag['Creator']

                if 'Created' in frag:
                    if self.product is not None:
                        self.product.creationDate = frag['Created']


                if 'FileName' in frag:
                    if self.files == None:
                        self.files = []

                    self.files.append(self.consumeFile(frag))

                





