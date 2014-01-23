# vitalHarshArm

## Overview

Python library for creating memory efficient C++ classes

## Installation

Should be as simple as

    pip install vitalHarshArm

## Example usage

	vitalHarshArm <template> [-f <folder>] [-t]

	Will create c++ code corresponding to the classes defined in the template file.

	-f specifies the folder to create the code in
	-t will make a Makefile and a test.cpp file to allow for quick testing

### VHA template overview:

You should include all class templates in ONE template file. VHA will
produce a set of .cpp and .h files which you can copy into your project
directory. You should NOT modify these files by hand. Instead they should
be wrapped and accessed via that wrapper.

### Template fields:

You can specify any number of fields for each class and VHA will produce
appropriate get and set routines. Routines automatically provided are:

int      : signed integer             : Get Set Increment Decrement Clear
uint     : unsigned integer           : Get Set Increment Decrement Clear
pointer  : pointer to tclass instance : Get Set Clear
bdata    : blocked data container     : Get GetByIndex Set SetByIndex Clear
flag     : boolean flag               : Is Set Clear
float    : floating point number      : Get Set Clear

###Template format:

Templates are written in modified JSON format that allows C-style comments.
Compulsory words are prefixed with a '_'.

    {
        "_size_of_int"         : 32|64,
        "_size_of_idtype"      : 32|64,
        "_classes" : [
            {
                "_className"   : "<string>",                      // Name of the class (Must be unique)
                "_prefix"      : "<string>",                      // Prefix associated with MACRO statements for this class
                "_description" : "<string>",                      // Description of the class
                "_defines"     : { "KEY" : "VALUE" } [,... ]},    // Macro definitons (#define KEY VALUE)
                "_deleteable"  : "True|False",                    // Instances can be deleted*
                "_active"      : "True|False",                    // Use this template
                "_realloc"     : [integer [,integer,...] ]        // Determines how memory is reallocated**
                "_fields"      : [                                // Class fields***
                    {
                        // for all ints the format is consistent
                        "_f0"  : { "_type":"int|uint", "_size":integer, "_name":"<string>", "_comment":"<string>"},
                        // pointer size is set (_size_of_idtype), however we need to know what 'type' we're pointing 'at'
                        "_f1"  : { "_type":"pointer", "_at":"className", "_name":"<string>", "_comment":"<string>"},
                        // flags are always one bit
                        "_f2"  : { "_type":"flag", "_name":"<string>", "_comment":"<string>"}
                        // the size of floats is decided by the compiler
                        "_f3"  : { "_type":"float", "_name":"<string>", "_comment":"<string>"}
                        // bdata is an array of integers. You can decide the 'blocksize' and 'size' of the array****
                        "_f4"  : { "_type":"bdata", "_size":<integer>, "_blocksize":8|16|32|64, "_name":"<string>", "_comment":"<string>"}
                        ...
                    }
                ]
            }[,{..}]
        ]
    }

*       If this flag is set to False then you can not delete instances. This speeds things up a bit.

**      When you instantiate one of the classes you tell it how many spaces to pre-allocate. Ex: calling Foo(80) will pre-allocate space for 80 Foos.
        When this space is used up the memory management will automatically allocate more space. The integers here specify how this will happen.
        "_realloc" : [1]        --> keep reallocating the same number of spaces as originally allocated. ie. 80 Foos each time
        "_realloc" : [1,2]      --> allocate the same as original on the first reallocation and then half as many spaces as the original for all subsequent allocations. 80 Foos then 40 Foos for all subsequent allocations.
        "_realloc" : [1,2,4]    --> 80 Foos, then 40 Foos, then 20 Foos for all subsequent allocation.

***     Fields are always identified as "_f0", "_f1", ... , "_fn". This isn't used the cpp, just when making it.

****    _size indicates the length of the array, _blocksize is any int flavour from <stdint> (uint8_t, uint16_t, ...)

See the test folder for a working template example.


## Help

If you experience any problems using vitalHarshArm, open an [issue](https://github.com/minillinim/vitalHarshArm/issues) on GitHub and tell us about it.

## Licence and referencing

Project home page, info on the source tree, documentation, issues and how to contribute, see http://github.com/minillinim/vitalHarshArm

This software is currently unpublished

## Copyright

Copyright (c) 2014 Michael Imelfort. See LICENSE.txt for further details.


