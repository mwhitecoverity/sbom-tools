
import xmltodict
import re
import gzip
import json
import yaml

from . import * 


def try_json(fh):
    try:
        js = json.load(fh)

        return js
    except Exception as e:
        return None


def try_xml(fh):
    try: 
        tree = xmltodict.parse(''.join(fh.readlines()))

        return tree
    except Exception as e:
        #print(e)
        return None


def try_yaml(fh):
    try:
        res = yaml.safe_load(fh)

        return res

    except Exception as e:
        return None

class BomSniffer():

    sbom = None
    gzipped = False
    zipfile = False

    def get_parser(self):
        if self.sbom is None:
            return None
        
        if self.gzipped is True:
            return None
        
        if self.zipfile is True:
            return None

        parser = None

        if self.sbom['standard'] == 'spdx':
            if self.sbom['format'] == 'json':
                parser = SpdxJsonSbom(self.sbom['file'])
            elif self.sbom['format'] == 'xml/rdf':
                parser = SpdxRdfSbom(self.sbom['file'])
            elif self.sbom['format'] == 'xml':
                parser = None
            elif self.sbom['format'] == 'tv':
                parser = SpdxTvSbom(self.sbom['file'])
        elif self.sbom['standard'] == 'cdx':
            if self.sbom['format'] == 'xml':
                parser = CdxXmlSbom(self.sbom['file'])
            elif self.sbom['format'] == 'json':
                parser = CdxJsonSbom(self.sbom['file'])
        elif self.sbom['standard'] == 'swid' or self.sbom['standard'] == 'swid-multi':
            parser = None
        
        if parser is None:
            print('Not parsed: {} {} '.format(self.sbom['standard'], self.sbom['format']))

        return parser


    def __init__(self, infile):

        gzipped = False
        zipfile = False
        info = {}

        info['file'] = infile

        with open(infile, 'rb') as test_f:
            gzipped = test_f.read(2) == b'\x1f\x8b'
            
            test_f.seek(0)
            zipfile = test_f.read(2) == b'\x50\x4b'

            info['gzipped'] = gzipped
            self.gzipped = gzipped
            info['zipfile'] = zipfile
            self.zipfile = zipfile

        # TODO: Unzip zip file
        if zipfile:
            #print ('Skipping zipfile')
            return

        with open(infile, encoding='utf-8') as fl:
            
            j = None

            if gzipped:
                with gzip.open(infile) as fh:
                    j = try_json(fh)
                    fh.seek(0)
                    x = try_xml(fh)
                    fh.seek(0)
                    y = try_yaml(fh)
            else:
                j = try_json(fl)
                fl.seek(0)
                x = try_xml(fl)
                fl.seek(0)
                y = try_yaml(fl)

            if j is not None:
                if 'bomFormat' in j:
                    info['standard'] = 'cdx'
                    info['format']  = 'json'
                    if 'specVersion' in j:
                        info['version']  = j['specVersion']
                elif 'spdxVersion' in j:
                    info['standard'] = 'spdx'
                    info['format'] = 'json'
                    info['version']  = j['spdxVersion']
                else:
                    print("Unknown JSON: {} ".format(j))
            
            # TODO: Make XML work
            if x is not None:
                info['format'] = 'xml'

                if 'SoftwareIdentity' in x: 
                    swid = x['SoftwareIdentity']

                    info['standard'] = 'swid'
                    info['tagId'] = swid['@tagId']
                    info['swidVersion'] = swid['@version']

                elif 'SBOM' in x and 'SoftwareIdentity' in x['SBOM']:
                    info['standard'] = 'swid-multi'

                elif 'bom' in x:
                    info['standard'] = 'cdx'
                    #version = x['specVersion']
                elif 'rdf:RDF' in x:
                    rdfRoot = x['rdf:RDF']
                    
                    info['format'] = 'xml/rdf'

                    spdxns = None
                    for ns in rdfRoot:
                        if rdfRoot[ns] == 'http://spdx.org/rdf/terms#':
                            spdxns = ns.replace('@xmlns:', '')
                            #print(spdxns)
                    
                    spdxRoot = rdfRoot['{}:SpdxDocument'.format(spdxns)]
                    version = spdxRoot['{}:specVersion'.format(spdxns)]

                    #print(spdxRoot)
                    #namespace = 
                    info['standard'] = 'spdx'
                    info['version'] = version
            
            if y is not None and j is None:
                # YAML
                info['standard'] = 'spdx'
                info['format'] = 'yaml'
                info['version'] = y['spdxVersion']


            # Check for tag-value
            if x is None and j is None and y is None:
                fl.seek(0)

                try: 
                    lines = fl.readlines()
                    fulldoc = '\n'.join(lines)
                    #if 'SPDXVersion: ' in fulldoc:
                    m = re.search('SPDXVersion: SPDX-(\d+\.\d+)', fulldoc)
                    if m:
                        # tag value
                        info['standard'] = 'spdx'
                        info['format'] = 'tv'
                        info['version'] = m.group(1)
                except UnicodeDecodeError as u:
                    # If the file turns out not to be text.. 
                    pass

        self.sbom = info

