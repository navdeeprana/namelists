# namelists
A python implementation of fortran namelists using dictionaries.
Useful to load fortran namelists and use the parameters for data processing and analysis.

## Implementation
`nml` class is an extension of `dict` class with methods to read/write fortran namelists.

## Examples
### Python Example
```python

from namelists import nml

# Create a new name list with a dictionary.
dummy = nml('dummy_nml',_dict={'n': 123, 'f' : 3.14e0, 'b' : True, 'c' : 'foobar'}

# Add a new variable/ change existing
dummy.c = 'barfoo'
#or
dummy['c'] = 'barfoo'

# Write to standard python output
dummy.write()
# Write to a valid fortran namelist file
dummy.write(fname='dummy.nml')
```
### Fortran Example
```fortran
program namelist_demo
implicit none
!! Define some variables
integer      :: n
real(kind=8) :: f
logical      :: b

character(len=16) :: c

!! Create a namelist
namelist /dummy_nml/ n, f, b, c

!! Read from file
open(unit=10,file='dummy.nml',status='old')
read(10,nml=dummy_nml)
close(10)
!! Print
write(*,*) dummy_nml
end program
```
