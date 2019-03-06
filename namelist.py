"""
Fortran namelist class for python, is based on dictionary. It is basically a dictionary
with added support to load a fortran namelist file and write it as well. 
"""
class nml(dict):
    def __init__(self,name,**kwargs):
        """
        Initiate a namelist with given name.

        Parameters
        ----------
        name : str
            Name of the namelist, This is included in the output. For example if name is
            'spectral', output will be
            &spectral
            ...
            /
        fname : filename, optional
            Filename from which a namelist can be loaded.
        _dict : dictionary, optional
            Dictionary from which a namelist can be created.
        
        Notes
        -----
        If both fname and _dict are given, fname is given preference.

        Examples
        --------
        >>> sp = nml('dummy_nml',_dict={'foo':1,'bar':2})
        >>> sp.write()
        """

        self.name=name
        fname = kwargs.get('fname',None)
        if fname:
            _dict = self.load(fname)
        else:
            _dict = kwargs.get('_dict',None)
        if _dict:
            dict.__init__(self,_dict)
            self.str_width = max(len(max(self.keys(),key=len)), 8) + 1
        else:
            self.str_width = 8
        

    def load(self,fname):
        import re
        regex = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([dDeE][+-]?\d+)?')
        def get_pair(line):
            def get_value(value):
                # Numbers
                if value.isdigit():
                    return int(value)
                # Float
                if (re.match(regex,value)):
                    return float(value.lower().replace('d+','e+').replace('d-','e-'))
                # Bool
                elif value=='.true.' or value=='.false':
                    return bool(value.replace('.',''))
                # String
                elif "'" in value:
                    return value.strip('\n')[1:-1]
                    
            var, value = line.replace(' ','').split('=')
            if ',' in value:
                old_value = value.split(',')
                new_value = []
                for li in old_value:
                    new_value.append(get_value(li))
                return var, new_value
            else:
                return var, get_value(value)
        
        _dict = {}
        with open(fname,'r') as f:
            read_nml = False
            for line in f:
                line = line.strip('\n')
                if not line.strip():
                    continue
                if line.startswith('&'+self.name):
                    read_nml = True
                if read_nml and '=' in line:
                    var,value = get_pair(line)
                    _dict[var] = value
                if read_nml and line.startswith('/'):
                    break
        return _dict

    def change(self,key,value):
        """
        Change the value corresponding to an already present key in the namelist.

        Parameters
        ----------
        key : str
              Must be in dictionary.

        value : datatype
              Must be a valid fortran datatype.
        """
        if key in self:
            if type(self[key]) is type(value):
                self[key] = value
            else:
                raise TypeError('Expected %s, got %s'%(type(self[key]), type(value)))
        else:
            raise ValueError('%s is not a part of the namelist.'%key)

    def write(self,**kwargs):
        import re
        """
        Print a name list to stderr, or write it to a file, in a fortran readable format.

        Parameters
        ----------

        fname : filename, optional
                Filename to which to write to.
        mode  : ['a','w'] str, optional
        Write mode, 'w' either creates a new file or overwrites, 'a' appends to an existing file,
        helpful when writing multiple namelists to the same file.
        """
        def fortran_double(value):
            value = re.sub('0*e','d',format(value,'.5e'))
            #value = re.sub('-0*','-',value)
            #value = re.sub('\\+0*','0',value)
            return value
        
        to_write = ['&'+self.name]
        for key, value in self.items():
            if type(value) is str :
                value = "'%s'"%value

            elif type(value) is float :
                value = fortran_double(value)

            elif type(value) is bool :
                if value :
                    value = '.true.'
                else :
                    value = '.false.'

            elif type(value) is list :
                new = ''
                for l in value :
                    if type(l) is float:
                        new = new + fortran_double(l) + ", "
                    else:
                        new = new + str(l) + ", "
                value = new[:-2]

            to_write.append(key.ljust(self.str_width)+'= '+str(value))
        to_write.append('/')
        fname = kwargs.get('fname',None)
        if fname:
            mode = kwargs.get('mode','w')
            with open(fname,mode) as f:
                for line in to_write:
                    f.write(line+'\n')
        else:
            for line in to_write:
                print(line)
