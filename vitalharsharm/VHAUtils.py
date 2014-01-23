#!/usr/bin/env python
###############################################################################
#                                                                             #
#    VHAUtils.py                                                              #
#                                                                             #
#    Classes for doing all the work which VHA does bestest                    #
#                                                                             #
#    Copyright (C) Michael Imelfort                                           #
#                                                                             #
###############################################################################
#                                                                             #
#        888     888 d8b 888    888                 d8888 8888888b.           #
#        888     888 Y8P 888    888                d88888 888   Y88b          #
#        888     888     888    888               d88P888 888    888          #
#        Y88b   d88P 888 8888888888  8888b.      d88P 888 888   d88P          #
#         Y88b d88P  888 888    888     "88b    d88P  888 8888888P"           #
#          Y88o88P   888 888    888 .d888888   d88P   888 888 T88b            #
#           Y888P    888 888    888 888  888  d8888888888 888  T88b           #
#            Y8P     888 888    888 "Y888888 d88P     888 888   T88b          #
#                                                                             #
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__author__ = "Michael Imelfort"
__copyright__ = "Copyright 2012"
__credits__ = ["Michael Imelfort"]
__license__ = "LGPL2.1"
__version__ = "0.1.0"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"
__status__ = "Alpha"

###############################################################################

import json
import re
import StringIO
import pkgutil
import sys
import os

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class VHA_TemplateNotLoadedException(BaseException): pass
class VHA_BadKeywordException(BaseException): pass
class VHA_MissingKeywordException(BaseException): pass
class VHA_NoFieldsDefinedException(BaseException): pass

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class TCBuilder:
    """Machine for doing the work of building templated classes"""
    def __init__(self):
        self.templates = []
        self.sizeOfInt = 64         # set hard defaults here
        self.sizeOfIdType = 32
        self.templateFileName = ""

    def loadTemplate(self, templateFileName):
        """Parse the template file and create a python dictionary of the JSON"""
        self.templateFileName = templateFileName
        strippedJSON = StringIO.StringIO()
        with open(templateFileName,'r') as f:
            for line in f:
                strippedJSON.write(self.removeComments(line))

        strippedJSON_fh = StringIO.StringIO(strippedJSON.getvalue())
        strippedJSON.close()

        data = json.load(strippedJSON_fh)
        tmp = json.loads(json.dumps(data, separators=(',',':')))

        # override hard defaults now
        self.sizeOfInt = int(tmp['_size_of_int'])
        self.sizeOfIdType = int(tmp['_size_of_idtype'])

        # parse in the data for each class and objectify them
        for t_class in tmp['_classes']:
            TC = TClass(self.sizeOfInt, self.sizeOfIdType, self.templateFileName)
            TC.validateAndPopulate(t_class)
            if TC.active:
                self.templates.append(TC)

        strippedJSON_fh.close()

    def removeComments(self, string):
        """Strip C/C++ style comments from a string

        From: http://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
        """
        string = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,string) # remove all occurance streamed comments (/*COMMENT */) from string
        string = re.sub(re.compile("//.*?\n" ) ,"" ,string) # remove all occurance singleline comments (//COMMENT\n ) from string
        return string

    def createClasses(self, path, makeTest=False):
        """Create classes from a loaded template"""
        if len(self.templates) == 0:
            raise VHA_TemplateNotLoadedException

        if not os.path.exists(path):
            os.makedirs(path)

        id_types = []
        # make the code for each template
        for t in self.templates:
            # make the id type for this template
            id_types.append("DEFINE_ID_TYPE(%s, %s, )" % (t.toIntIdType(), t.toMMName()))
            file_name = os.path.join(path, t.hFileName)
            with open(file_name, 'w') as fh:
                t.codeH(fh)
            file_name = os.path.join(path, t.cppFileName)
            with open(file_name, 'w') as fh:
                t.codeCPP(fh)

        # write the core files to the folder too
        with open(os.path.join(path, "idTypeDefs.h"), 'w') as fh:
            fh.write(pkgutil.get_data('vitalharsharm','inc/idTypeDefs.h').replace("//VHA",
                                                                                  "\n".join(id_types)
                                                                                  )
                     )

        with open(os.path.join(path, "intdef.h"), 'w') as fh:
            id = pkgutil.get_data('vitalharsharm','inc/intdef.h').replace("//VHA_SIZE_OF_INT",
                                                                          "#define SIZE_OF_INT %d" % self.sizeOfInt
                                                                          )
            id = id.replace("//VHA_SIZE_OF_IDTYPE", "#define SIZE_OF_IDTYPE %d" % self.sizeOfIdType)
            fh.write(id)

        unchanged_files = ["memManager.h", "paranoid.h", "paranoid.cpp"]
        if makeTest:
            unchanged_files.append('Makefile')
            includes = []
            for t in self.templates:
                includes.append('#include "%s"' % t.hFileName)
            with open(os.path.join(path, 'test.cpp'), 'w') as fh:
                fh.write(pkgutil.get_data('vitalharsharm','inc/test.cpp').replace("__VHA_TEST_INC__", "\n".join(includes)))


        for fn in unchanged_files:
            with open(os.path.join(path, fn), 'w') as fh:
                fh.write(pkgutil.get_data('vitalharsharm','inc/%s'%fn))




    #-----
    # PRINTING / IO
    def __str__(self):
        """String function for purdy printing"""
        return "\n".join(["%r" % t for t in self.templates])

    #-----
    # MAKING CPP



###############################################################################
###############################################################################
###############################################################################
###############################################################################

class TClass:
    """Object storage for a templated class"""
    def __init__(self, sizeOfInt, sizeOfIdType, templateFileName):
        self.className =    "VOID"
        self.prefix =       "VOID"
        self.description =  "VOID"
        self.idName =       "VOID"
        self.deleteable =   False
        self.active =       False
        self.blockSize =    -1
        self.realloc = [1]
        self.hashDefines =  []
        self.fields =       []

        self.sizeOfInt = sizeOfInt;
        self.sizeOfIdType = sizeOfIdType;

        self.templateFileName = templateFileName

        self.validKeys = ['_className',
                          '_description',
                          '_prefix',
                          #'_blockSize',
                          #'_idName',
                          '_deleteable',
                          '_active',
                          '_realloc',
                          '_defines',
                          '_fields']

        self.cppFileName = "VOID"
        self.hFileName = "VOID"

    def validateAndPopulate(self, template):
        """Make sure a template is legit and populate fields"""

        # first we check to make sure there are no weird keywords here
        for key in template:
            if key not in self.validKeys:
                raise VHA_BadKeywordException("Unknown TEMPLATE keyword %s" % key)

        # now try to load the required decriptors
        try:
            self.className =    template['_className']
            self.cppFileName = self.toFileNamePrefix() +".cpp"
            self.hFileName = self.toFileNamePrefix() +".h"
        except KeyError:
            raise VHA_MissingKeywordException("'className' keyword not defined for %r" % template)
        try:
            self.prefix =    template['_prefix']
        except KeyError:
            raise VHA_MissingKeywordException("'prefix' keyword not defined for %r" % template)

        try:
            self.description =  template['_description']
        except KeyError:
            raise VHA_MissingKeywordException("'description' keyword not defined for %r" % template)

        if False:
            try:
                self.blockSize = template['_blockSize']
            except KeyError:
                raise VHA_MissingKeywordException("'blockSize' keyword not defined for %r" % template)
            try:
                self.idName =       template['_idName']
            except KeyError:
                raise VHA_MissingKeywordException("'idName' keyword not defined for %r" % template)

        try:
            self.deleteable =   template['_deleteable'] == u'True'
        except KeyError:
            raise VHA_MissingKeywordException("'deletable' keyword not defined for %r" % template)
        try:
            self.active =       template['_active'] == u'True'
        except KeyError:
            raise VHA_MissingKeywordException("'active' keyword not defined for %r" % template)

        try:
            self.realloc = template['_realloc']
        except KeyError:
            # user has not specified reallocation, so we just set it to the same
            pass

        # these may or may not be present
        try:
            tmp = template['_template'][0]
            for key in tmp:
                self.cppTemplates.append("%s %s" % (key, tmp[key]))
        except KeyError: pass

        try:
            tmp = template['_defines']#[0]
            for key in tmp:
                self.hashDefines.append("#define %s %s" % (key, tmp[key]))
        except KeyError: pass

        # load fields
        tmp = template['_fields'][0]
        num_fields = len(tmp.keys())
        if num_fields == 0:
            raise VHA_NoFieldsDefinedException("Cannot see any defined fields for class '%'" % self.className)
        bits_used = 0
        keys = [str(i) for i in range(num_fields)]
        for key in keys:
            F = TClassField(self.sizeOfIdType)
            size = F.validateAndPopulate(tmp["_f"+key])
            self.fields.append(F)

            # if the field is a bdata type then we need to add a new ash define
            if F.type == "bdata":
                def_str = "%s_default_%s_size" % (self.prefix, F.name)
                self.hashDefines.append("#ifndef %s\n #define %s %d\n#endif"%(def_str, def_str, size))
                bits_used += size * 8
            else:
                bits_used += size


        self.blockSize = bits_used / self.sizeOfInt
        if self.blockSize == 0:
            self.blockSize = 1


    #----
    # WRITING CODE

    def toFileNamePrefix(self):
        return self.className[0].lower() + self.className[1:]

    def toIntIdType(self, className=None):
        """return the intID name for this class"""
        if className is not None:
            return className + "_Id"
        return self.className + "_Id"

    def toHdef(self):
        """return the #ifndef string for this class"""
        return self.className.upper()+"_H"

    def toStructName(self):
        """make the name of the struct used for this type"""
        return self.className+"_unit"

    def toMMName(self):
        """return the memory manager name"""
        return self.className+"MemManager"

    def codeStructDef(self, fh):
        """create the definition of the struct"""
        # first we group fields into blocks

        _str = "typedef struct {\n"
        for f in self.fields:
            if f.type == "flag":
                _str += "    unsigned int %s : 1;\n" % (f.name)
            elif f.type == "pointer":
                _str += "    %s %s;\n" % (self.toIntIdType(className=f.at), f.name)
            elif f.type == "float":
                _str += "    float %s;\n" % (f.name)
            elif f.type == "bdata":
                def_str = "%s_default_%s_size" % (self.prefix, f.name)
                _str += "    uint%d_t %s[%s];\n" % (f.blockSize, f.name, def_str)
            elif f.type == "int":
                _str += "    int %s : %d;\n" % (f.name, f.size)
            elif f.type == "uint":
                _str += "    unsigned int %s : %d;\n" % (f.name, f.size)

        _str += "} %s;\n\n" % (self.toStructName())
        fh.write(_str)

    def codeDefines(self, fh):
        """Stringify #defines"""
        if len(self.hashDefines) > 0:
            fh.write("\n".join(self.hashDefines)+"\n\n")

    def codeHeader(self, fh, fileName):
        """Print the main header of the source file"""
        _str = """**
** File: %s
**
*******************************************************************************
**
** File for use with projects including MemManager.cpp
**
** This file has been automatically generated by vitalHarshArm.
** It includes implementations to get/set all the fields defined in:
**
** %s
**
** DO NOT EDIT THIS FILE
**
*******************************************************************************\n""" % (fileName, self.templateFileName)
        fh.write(_str)

    def codeAbracadabra(self, fh):
        """for luck!"""
        _str = """**
**                                     A
**                                    A B
**                                   A B R
**                                  A B R A
**                                 A B R A C
**                                A B R A C A
**                               A B R A C A D
**                              A B R A C A D A
**                             A B R A C A D A B
**                            A B R A C A D A B R
**                           A B R A C A D A B R A
**
*******************************************************************************\n"""
        fh.write(_str)

    def codeEnd(self, fh):
        fh.write("""/******************************************************************************
*******************************************************************************
******************************************************************************/\n""")

    def codeH(self, fh):
        """Write the c++ header file for this template"""
        if self.deleteable:
            self.hashDefines.append("#define DMM")  # will make freeId a valid call
        fh.write("/******************************************************************************\n")
        self.codeHeader(fh, self.hFileName)
        self.codeAbracadabra(fh)
        fh.write("""******************************************************************************/

#ifndef %s
    #define %s

// system includes
#include <iostream>
#include <vector>

// local includes
#include "memManager.h"
#include "intdef.h"
#include "idTypeDefs.h"
#include "paranoid.h"

using namespace std;

""" % (self.toHdef(),
       self.toHdef())
                     )

        self.codeDefines(fh)
        self.codeStructDef(fh)

        # load the generic h template and modify to suit
        h_template = pkgutil.get_data('vitalharsharm','inc/h_template')
        if self.deleteable:
            h_template = h_template.replace("__VHA_MM_TYPE__", "Deletable")
        else:
            h_template = h_template.replace("__VHA_MM_TYPE__", "")

        # gets and sets
        getSetStr = ""
        for F in self.fields:
            getSetStr = F.toGetSetHeader(getSetStr, self.toIntIdType())

        fh.write(h_template.replace("__VHA_GET_SET__", getSetStr).replace("__VHA_ID_NAME__", self.toIntIdType()).replace("__VHA_CLASS_NAME__", self.className).replace("__VHA_MM_NAME__", self.toMMName()).replace("__VHA_STRUCT_NAME__", self.toStructName()).replace("__VHA_REALLOC__", ",".join([str(i) for i in self.realloc])))

        if self.deleteable:
            fh.write("#undef DMM\n")
        fh.write("#endif //%s\n\n" % self.toHdef())
        self.codeEnd(fh)

    def codeCPP(self, fh):
        """Write the c++ source file for this template"""

        fh.write("/******************************************************************************\n")
        self.codeHeader(fh, self.cppFileName)
        self.codeAbracadabra(fh)
        fh.write("""******************************************************************************/

// system includes
#include <iostream>
#include <sstream>
#include <stdexcept>

// local includes
#include "memManager.h"
#include "intdef.h"
#include "idTypeDefs.h"
#include "%s"

using namespace std;

/******************************************************************************
** Implementation of %s functions declared inline in %s
******************************************************************************/
/******************************************************************************
 ** Implementation of %s Class
******************************************************************************/

""" % (self.hFileName,
       self.className+"MemManager",
       self.hFileName,
       self.className))

        # gets and sets
        getSetStr = ""
        for F in self.fields:
            getSetStr = F.toGetSetImplementation(getSetStr, self.toIntIdType(), self.className)

        fh.write(getSetStr)

        self.codeEnd(fh)

    #-----
    # PRINTING / IO
    def __str__(self):
        """String function for purdy printing"""
        _str = """####
 ClassName :         %s
 Description :       %s
 IdName :            %s
 BlockSize :         %s
 Deletable :         %r
 Active :            %r%s%s
""" % (self.className,
       self.description,
       self.idName,
       self.blockSize,
       self.deleteable,
       self.active,
       self.printDefines(),
       self.printFields())

        return _str

    def __repr__(self):
        return self.__str__()

    def printFields(self):
        """Stringify class fields"""
        return "\n---\n Fields :\n"+"\n".join(["%r" %f for f in self.fields])

    def printDefines(self):
        """Stringify #defines"""
        if len(self.hashDefines) > 0:
            return "\n---\n Defines :\n "+"\n ".join(self.hashDefines)
        return ""

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class TClassField:
    """Individual fields within a TClass"""
    def __init__(self, sizeOfIdType):
        self.name =      "VOID"
        self.comment =   "VOID"
        self.type =      "VOID"
        self.size =      -1
        self.at =        -1
        self.blockSize = -1

        self.sizeOfIdType = sizeOfIdType;

        self.validKeys = ['_name',
                          '_type',
                          '_size',
                          '_at',
                          '_comment',
                          '_blocksize']

        self.validFieldTypes = ["int",
                                "uint",
                                "flag",
                                "pointer",
                                "float",
                                "bdata"]

        self.validBlockSizes = [4,8,16,32,64]

    def validateAndPopulate(self, template):
        """Populate the fields containers and make sure everything looks sane

        info is a dictionary that describes the fields attributes
        """
        for key in template.keys():
            if key not in self.validKeys:
                raise VHA_BadKeywordException("Unknown FIELD keyword %s" % key)

        try:
            self.type = template['_type']
            if self.type not in self.validFieldTypes:
                raise VHA_BadKeywordException("Unknown 'type' keyword '%s' defined for %r" % (self.type, template))

            # make sure bdata is defined correctly
            if self.type == "bdata":
                try:
                    self.blockSize = template['_blocksize']
                    if self.blockSize not in self.validBlockSizes:
                        raise VHA_BadKeywordException("Bad blocksize '%d' defined for %r" % (self.blockSize, template))
                except KeyError:
                    raise VHA_MissingKeywordException("'blocksize' keyword not defined for 'bdata' type %r" % template)

        except KeyError:
            raise VHA_MissingKeywordException("'type' keyword not defined for %r" % template)

        try:
            self.comment = template['_comment']
        except KeyError:
            raise VHA_MissingKeywordException("'comment' keyword not defined for %r" % template)

        try:
            self.size = template['_size']
            if self.type == "pointer" or self.type == "flag" or self.type == "float":
                raise VHA_BadKeywordException("'size' keyword used for '%s' for %r" % (self.type, template))
        except KeyError:
            if self.type == "pointer":
                self.size = self.sizeOfIdType
            elif self.type == "flag":
                self.size = 1
            elif self.type == "float":
                pass
            else:
                raise VHA_MissingKeywordException("'size' keyword not defined for %r (%s)" % (template,self.type))

        try:
            self.at = template['_at']
            if self.type != "pointer":
                raise VHA_BadKeywordException("'at' keyword used for non-pointer for %r" % template)
        except KeyError:
            if self.type == "pointer":
                raise VHA_MissingKeywordException("'at' keyword not defined for %r" % template)

        try:
            self.name = template['_name']
        except KeyError:
            raise VHA_MissingKeywordException("'name' keyword not defined for %r" % template)

        return self.size

    def toGetSetHeader(self, getSetStr, idType):
        """Return the c++ code for the get set functions for this fella"""
        """Return the c++ code for the get set functions for this fella"""
        getSetStr += "        //%s  -- %s\n" % (self.name, self.comment)
        if self.type == "int":
            getSetStr += "    inline int get_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void set_%s(%s ID, int value) { mData->getAddr(ID)->%s = value; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void clear_%s(%s ID) { mData->getAddr(ID)->%s = 0; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void increment_%s(%s ID) { mData->getAddr(ID)->%s += 1; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void decrement_%s(%s ID) { mData->getAddr(ID)->%s -= 1; }\n\n" % (self.name, idType, self.name)

        if self.type == "uint":
            getSetStr += "    inline unsigned int get_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void set_%s(%s ID, unsigned int value) { mData->getAddr(ID)->%s = value; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void clear_%s(%s ID) { mData->getAddr(ID)->%s = 0; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void increment_%s(%s ID) { mData->getAddr(ID)->%s += 1; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void decrement_%s(%s ID) { mData->getAddr(ID)->%s -= 1; }\n\n" % (self.name, idType, self.name)

        if self.type == "flag":
            getSetStr += "    inline bool is_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void set_%s(%s ID, bool value) { mData->getAddr(ID)->%s = value; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void clear_%s(%s ID) { mData->getAddr(ID)->%s = 0; }\n\n" % (self.name, idType, self.name)

        if self.type == "pointer":
            getSetStr += "    inline %s get_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.at+"_Id", self.name, idType, self.name)
            getSetStr += "    inline void set_%s(%s ID, %s value) { mData->getAddr(ID)->%s = value; }\n" % (self.name, idType, self.at+"_Id", self.name)
            getSetStr += "    inline void clear_%s(%s ID) { mData->getAddr(ID)->%s = 0; }\n\n" % (self.name, idType, self.name)

        if self.type == "float":
            getSetStr += "    inline float get_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void set_%s(%s ID, float value) { mData->getAddr(ID)->%s = value; }\n" % (self.name, idType, self.name)
            getSetStr += "    inline void clear_%s(%s ID) { mData->getAddr(ID)->%s = 0; }\n\n" % (self.name, idType, self.name)

        if self.type == "bdata":
            getSetStr += "    inline uint%d_t* get_%s(%s ID) { return mData->getAddr(ID)->%s; }\n" % (self.blockSize, self.name, idType, self.name)
            getSetStr += "    uint%d_t get_%s_by_index(%s ID, int index);\n" % (self.blockSize, self.name, idType)
            getSetStr += "    inline void set_%s(%s ID, uint%d_t* value) { int i; for(i=0;i<%d;++i){mData->getAddr(ID)->%s[i] = value[i];} }\n" % (self.name,
                                                                                                                                                   idType,
                                                                                                                                                   self.blockSize,
                                                                                                                                                   self.size,
                                                                                                                                                   self.name)
            getSetStr += "    void set_%s_by_index(%s ID, int index, uint%d_t value);\n" % (self.name, idType, self.blockSize)
            getSetStr += "    inline void clear_%s(%s ID) { int i; for(i=0;i<%d;++i){mData->getAddr(ID)->%s[i] = 0;} }\n" % (self.name,
                                                                                                                             idType,
                                                                                                                             self.size,
                                                                                                                             self.name)
            getSetStr += "    inline int get_%s_blocksize(void) { return %d; }\n" % (self.name, self.blockSize)
            getSetStr += "    inline int get_%s_size(void) { return %d; }\n" % (self.name, self.size)


        return getSetStr

    def toGetSetImplementation(self, getSetStr, idType, className):
        if self.type == "bdata":
            getSetStr += "        //%s  -- %s\n" % (self.name, self.comment)
            getSetStr += """uint%d_t %s::get_%s_by_index(%s ID, int index) {
    PARANOID_ASSERT(index < %d);
    PARANOID_ASSERT(index >= 0);
    if(index > %d || index < 0) {
        std::ostringstream oss;
        oss << "[%s::get_%s_by_index] index " << index << " out of range (max == " << %d << ")" << std::endl;
        throw std::out_of_range(oss.str());
    }
    return mData->getAddr(ID)->%s[index];\n}\n\n""" % (self.blockSize, className, self.name, idType, self.size, self.size-1, className, self.name, self.size-1, self.name)


            getSetStr += """void %s::set_%s_by_index(%s ID, int index, uint%d_t value) {
    PARANOID_ASSERT(index < %d);
    PARANOID_ASSERT(index >= 0);
    if(index > %d || index < 0) {
        std::ostringstream oss;
        oss << "[%s::set_%s_by_index] index " << index << " out of range (max == " << %d << ")" << std::endl;
        throw std::out_of_range(oss.str());
    }
    mData->getAddr(ID)->%s[index] = value;\n}\n\n""" % (className, self.name, idType, self.blockSize, self.size, self.size-1, className, self.name, self.size-1, self.name)

        return getSetStr

    def __str__(self):
        if self.type == "int" or self.type == "uint":
            return " ...\n  Name: %s\n  Type: %s\n  Size: %s bits\n  Comment: %s" % (self.name,
                                                                                     self.type,
                                                                                     self.size,
                                                                                     self.comment)
        elif self.type == "float":
            return " ...\n  Name: %s\n  Type: %s\n  Comment: %s" % (self.name,
                                                                    self.type,
                                                                    self.comment)
        elif self.type == "bdata":
            return " ...\n  Name: %s\n  Type: %s\n  Size: %s bytes\n  Comment: %s" % (self.name,
                                                                                      self.type,
                                                                                      self.size,
                                                                                      self.comment)

        elif self.type == "flag":
            return " ...\n  Name: %s\n  Type: %s\n  Size: 1\n  Comment: %s" % (self.name,
                                                                               self.type,
                                                                               self.comment)
        else: # self.type == "pointer"
            return " ...\n  Name: %s\n  Type: %s\n  At: %s\n  Size: %d\n  Comment: %s" % (self.name,
                                                                                          self.type,
                                                                                          self.at,
                                                                                          self.sizeOfIdType,
                                                                                          self.comment)

    def __repr__(self):
        return self.__str__()

###############################################################################
###############################################################################
###############################################################################
###############################################################################