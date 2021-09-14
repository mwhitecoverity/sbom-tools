

class GenericSbom:

    def get_packages(self):
        pass
    
    def count_relationships(self):
        return len(self.relationships)

    def get_files(self):
        pass

    def get_final_product(self):
        pass

    def count_packages(self):
        return len(self.packages)
    

    def get_all_hashes(self, algo):
        
        ret = set()

        if self.packages is not None:
            for p in self.packages:
                if p.hashes is not None:
                    for h in p.hashes:
                        if h.algo is algo:
                            ret.add(h.value)
        
        if self.files is not None:
            for f in self.files:
                if f.hashes is not None:
                    for h in f.hashes:
                        if h.algo is algo:
                            ret.add(h.value)

        return ret


    def dumpJson(self):
        report = {}

        report['bom'] = self.fileName
        report['type'] = type(self).__name__

        if self.packages is None:
            report['packages'] = 0
        else:
            report['packages'] = len(self.packages)
            supplierNames = 0
            ids = 0
            hashes = 0
            names = 0

            for p in self.packages:
                if p.supplierName is not None:
                    supplierNames = supplierNames + 1
                if p.id is not None:
                    ids = ids + 1
                if p.hashes is not None:
                    hashes = hashes + 1
                if p.name is not None:
                    names = names + 1

            report['packages_with_suppliers'] = supplierNames
            report['packages_with_ids'] = ids
            report['packages_with_hashes'] = hashes
            report['packages_with_names'] = names   

        if self.relationships is not None:
            report['relationships'] = len(self.relationships)
        else:
            report['relationships'] = 0


        if self.files is not None:
            report['files'] = len(self.files)
            hashes = 0
            for f in self.files:
                if f.hashes is not None:
                    hashes = hashes + 1
            report['files_with_hashes'] = hashes
        else:
            report['files'] = 0
        

        if self.product is None:
            report['got_final_product'] = False
        else:
            fp = self.product
            report['got_final_product'] = True
            report['sbom_author'] = fp.sbomAuthor
            report['sbom_target'] = fp.name
            report['sbom_created'] = fp.creationDate


        return report


    def dump(self):

        print ('---- SBOM report ---- ')
        print ('File name: {}'.format(self.fileName))
        print ('Type: {}'.format(type(self).__name__))

        if self.product is not None:
            if self.product.name is not None:
                print(' SBOM of: {}'.format(self.product.name))
            else:
                print(' SBOM has no name!')

            if self.product.sbomAuthor is not None:
                print(' SBOM author(s): {}'.format(self.product.sbomAuthor))
            else:
                print(' SBOM has no authors!')


            if self.product.creationDate is not None:
                print(' SBOM timestamp: {}'.format(self.product.creationDate))
            else:
                print(' SBOM has no timestamp!')



            #if self.product.supplierName is not None:
            #    print(' SBOM supplier(s): {}'.format(self.product.supplierName))
            #else:
            #    print(' SBOM has no supplier name!')


            if self.product.id is not None:
                print(' SBOM ID: {}'.format(self.product.id))
            else:
                print(' SBOM has no ID!')


        if self.packages is not None:
            print (' Has packages: Yes')
            for p in self.packages:
                print('  Package name:  ' + p.name)
                if p.supplierName is not None:
                    print('  Package supplier:  ' + p.supplierName)
                else:
                    print('  Package has no supplier name')
                
                if p.version is not None:
                    print('  Package version:  ' + p.version)
                else:
                    print('  Package has no version')
                
                if p.id is not None:
                    print('  Package ID:  ' + p.id)
                else:
                    print('  Package has no ID')

                if p.hashes is not None:
                    print('   Package has hashes')
                    for h in p.hashes:
                        print('   Hash {} {} '.format(h.algo, h.value))
                else:
                    print('   Package does not have hashes')

        if self.relationships is not None:
            print(' Has relationships: Yes')
        else:
            print(' Has relationships: No')

        if self.files is not None:
            print(' Has files: Yes')

            for f in self.files:
                print(' File name: {}'.format(f.name))
                if f.id is not None:
                    print('  File ID: {}'.format(f.id))
                else:
                    print('  File has no ID')
                if f.hashes is not None:
                    for h in f.hashes:
                        print('    Hash: {} {} '.format(h.algo, h.value))
                else:
                    print('    File has no hash')

        else:
            print(' Has files: No')

