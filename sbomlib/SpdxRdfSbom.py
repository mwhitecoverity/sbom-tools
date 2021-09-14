
from os import fpathconf
from typing import OrderedDict

from .GenericSbom import GenericSbom
from .SbomTypes import * 

import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace

from rdflib import RDF


class SpdxRdfSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None
    fileName = None
    spdxns = Namespace("http://spdx.org/rdf/terms#")

    def traverse(self, input, namespace):
        pass

    def extract_top_level(self, input):
        # Extract top level package information

        fp = FinalProduct()

        for s, p, o in input.triples((None, RDF.type, self.spdxns["SpdxDocument"])):

            for ss, pp, oo in input.triples( (  s, self.spdxns['name'], None)  ):

                fp.name = oo

            #for ss, pp, oo in input.triples( (  p, self.spdxns['Package'], None)  ):

                #print(" Package supplier: {}".format(oo))

                #fp.name = oo

            for ss, pp, oo in input.triples(( None, RDF.type, self.spdxns['CreationInfo'] )):

                for sss, ppp, ooo in input.triples(( ss, self.spdxns['created'], None)):
                    #print('Creation date: {}'.format(ooo))
                    fp.creationDate = ooo

                for sss, ppp, ooo in input.triples(( ss, self.spdxns['supplier'], None)):
                    #print('Creation date: {}'.format(ooo))
                    fp.supplierName = ooo

                for sss, ppp, ooo in input.triples(( ss, self.spdxns['creator'], None)):
                    #print('Creation date: {}'.format(ooo))
                    if fp.sbomAuthor is not None:
                        fp.sbomAuthor = fp.sbomAuthor + ', ' + ooo
                    else:
                        fp.sbomAuthor = ooo

                #print(pp)

        self.product = fp

        #print(s)
        
    
    def extract_packages(self, input):

        for s, p, o in input.triples((None, RDF.type, self.spdxns["Package"])):

            p = Package()

            p.id = s.split('#')[1]

            for ss, pp, oo in input.triples((s,  self.spdxns["name"], None )):
                if p.name is not None:
                    print('Warning - multiple names! {}'.format(oo))
                p.name = oo
            
            for ss, pp, oo in input.triples((s,  self.spdxns["versionInfo"], None )):
                if p.version is not None:
                    print('Warning - multiple versions! {}'.format(oo))

                p.version = oo

            for ss, pp, oo in input.triples((s,  self.spdxns["supplier"], None )):
                if p.supplierName is not None:
                    print('Warning - multiple suppliers! {}'.format(oo))

                p.supplierName = oo

            
            for ss, pp, oo in input.triples((s,  self.spdxns["Checksum"], None )):

                p.hashes = []

                h = Hash()

                for sss, ppp, ooo in input.triples((ss, self.spdxns['algorithm'], None)):
                    h.algo = ooo
                
                for sss, ppp, ooo in input.triples((ss, self.spdxns['checksumValue'], None)):
                    h.value = ooo

                p.hashes.append(h)                

                
        
            self.packages.append(p)

    def extract_files(self, input):

        for s, p, o in input.triples((None, RDF.type, self.spdxns["File"])):

            f = File()

            f.id = s.split('#')[1]


            for ss, pp, oo in input.triples((s,  self.spdxns["fileName"], None )):
                if f.name is not None:
                    print('Warning - multiple names! {}'.format(oo))

                f.name = oo
            

            for ss, pp, oo in input.triples((s,  self.spdxns["supplier"], None )):
                if p.supplierName is not None:
                    print('Warning - multiple suppliers! {}'.format(oo))

                f.supplierName = oo


            for ss, pp, oo in input.triples((s,  self.spdxns["checksum"], None )):

                f.hashes = []

                h = Hash()

                for sss, ppp, ooo in input.triples((oo, self.spdxns['algorithm'], None)):
                    h.algo = ooo.split('_')[1]
                
                for sss, ppp, ooo in input.triples((oo, self.spdxns['checksumValue'], None)):
                    h.value = ooo

                f.hashes.append(h)

            self.files.append(f)



    def __init__(self, infile):
        
        self.fileName = infile

        with open(infile) as fh:

            data = ET.parse(infile)

            g = Graph()
            g.parse(fh, format="application/rdf+xml")

            self.extract_top_level(g)

            self.packages = []
            self.extract_packages(g)

            self.files = []

            self.extract_files(g)


            #print('done')

            


            