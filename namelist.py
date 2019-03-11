"""
Fortran namelist class for python.
"""
class nml():
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
            self.__dict__.__init__(_dict)
            self.str_width = max(len(max(self.__dict__.keys(),key=len)), 8) + 1
        else:
            self.str_width = 8
        
        # Set internals vars. These will not be printed.
        self.internals = ['internals','name','str_width']

    def __setattr__(self,name,value):
        self.__dict__[name] = value
    def __getattr__(self,name):
        return self.__dict__[name]
        
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
                    return float(value.lower().replace('d','e'))
                # Bool
                elif value=='.true.' or value=='.false.':
                    return bool(value.replace('.',''))
                # String
                elif "'" in value:
                    return value.strip('\n')[1:-1]
                    
            var, value = line.replace(' ','').split('=')

            if value.endswith(','):
                value = value[:-1]
            # Trailing commas are optional, not desired.

            if ',' in value:
                # Comma separated values are arrays, treat them as python lists.
                old_values = value.split(',')
                new_values = []
                for vi in old_values:
                    # Check if value is not an empty string
                    if vi:
                        new_values.append(get_value(vi))
                return var, new_values
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
        def value_to_write(value):
            if type(value) is int :
                return str(value)

            elif type(value) is str :
                return "'%s'"%value

            elif type(value) is float :
                #value = re.sub('-0*','-',value)
                #value = re.sub('\\+0*','0',value)
                return re.sub('0*e','d',format(value,'.5e'))

            elif type(value) is bool :
                if value :
                    return '.true.'
                else :
                    return '.false.'
            else :
                raise TypeError('%s is not a valid type for %s'%(type(value),value))

        to_write = ['&'+self.name]
        for key, value in self.__dict__.items():
            # No output for internal keys.
            if key in self.internals:
                continue
            if type(value) is list :
                line = ''
                for vi in value :
                    line = line + value_to_write(vi) + ", "
                line = line[:-2]
            else :
                line = value_to_write(value)
            if not line.startswith(('-',"'",'.')):
                line = ' ' +  line

            to_write.append(key.ljust(self.str_width)+' =' + line)
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
