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
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"
__status__ = "Alpha"

###############################################################################

import json
import re
import StringIO
import pkgutil
import sys

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class VHA_TemplateNotLoadedException(BaseException): pass
class VHA_BadKeywordException(BaseException): pass
class VHA_MissingKeywordException(BaseException): pass

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
    
    def loadTemplate(self, templateFileName):
        """Parse the template file and create a python dictionary of the JSON"""
        strippedJSON = StringIO.StringIO()
        with open(templateFileName,'r') as f:
            for line in f:
                strippedJSON.write(self.removeComments(line))
            
        strippedJSON_fh = StringIO.StringIO(strippedJSON.getvalue())
        strippedJSON.close()
        data = json.load(strippedJSON_fh)
        tmp = json.loads(json.dumps(data, separators=(',',':')))
        
        # override hard defaults now
        self.sizeOfInt = int(tmp['SIZE_OF_INT']) 
        self.sizeOfIdType = int(tmp['SIZE_OF_IDTYPE'])
        
        # parse in the data for each class and objectify them
        for t_class in tmp['classes']:
            TC = TClass()
            TC.validateTemplate(t_class)
            self.templates.append(TC) 
        
        strippedJSON_fh.close()

    def removeComments(self, string):
        """Strip C/C++ style comments from a string
        
        From: http://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
        """
        string = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,string) # remove all occurance streamed comments (/*COMMENT */) from string
        string = re.sub(re.compile("//.*?\n" ) ,"" ,string) # remove all occurance singleline comments (//COMMENT\n ) from string
        return string

    def createClasses(self):
        """Create classes from a loaded template"""
        if len(self.templates) == 0:
            raise VHA_TemplateNotLoadedException

    #-----
    # PRINTING / IO
    def __str__(self):
        """String function for purdy printing"""
        return "\n".join(["%r" % t for t in self.templates])


###############################################################################
###############################################################################
###############################################################################
###############################################################################

class TClass:
    """Object storage for a templated class"""
    def __init__(self):
        self.className =    "VOIDFIELD"
        self.description =  "VOIDFIELD"
        self.idName =       "VOIDFIELD"
        self.deleteable =   "VOIDFIELD"
        self.active =       "VOIDFIELD"
        self.blockSize =    "VOIDFIELD"
        
        self.hashDefines =  []
        self.cppTemplates = []
        self.fields =       []
    
    def validateTemplate(self, template):
        """Make sure a template is legit and populate fields"""
        
        # first we check to make sure there are no weird keywords here
        valid_keys = ['className',
                      'description',
                      'idName',
                      'deleteable',
                      'active',
                      'template',
                      'defines',
                      'fields',
                      'blockSize']
        for key in template:
            if key not in valid_keys:
                raise VHA_BadKeywordException("Unknown TEMPLATE keyword %s" % key)

        # now try to load the required decriptors        
        try:
            self.className =    template['className']
        except KeyError:
            raise VHA_MissingKeywordException("'className' keyword not defined for %r" % template)
        try:
            self.description =  template['description']
        except KeyError:
            raise VHA_MissingKeywordException("'description' keyword not defined for %r" % template)
        try:
            self.idName =       template['idName']
        except KeyError:
            raise VHA_MissingKeywordException("'idName' keyword not defined for %r" % template)
        try:
            self.deleteable =   template['deleteable'] == u'1'
        except KeyError:
            raise VHA_MissingKeywordException("'deletable' keyword not defined for %r" % template)
        try:
            self.active =       template['active'] == u'1'
        except KeyError:
            raise VHA_MissingKeywordException("'active' keyword not defined for %r" % template)
        try:
            self.blockSize = template['blockSize']
        except KeyError:
            raise VHA_MissingKeywordException("'blockSize' keyword not defined for %r" % template)

        # these may or may not be present
        try:
            tmp = template['template'][0]
            for key in tmp:
                self.cppTemplates.append("%s %s" % (key, tmp[key]))
        except KeyError: pass
        
        try:
            tmp = template['defines'][0]
            for key in tmp:
                self.hashDefines.append("#define %s %s" % (key, tmp[key]))
        except KeyError: pass

        # load fields
        tmp = template['fields'][0]
        keys = [str(i) for i in range(len(tmp.keys()))]
        for key in keys:
            F = TClassField()
            F.populate(tmp[key])
            self.fields.append(F)
        
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
 Active :            %r%s%s%s
""" % (self.className,
       self.description,
       self.idName,
       self.blockSize,
       self.deleteable,
       self.active,
       self.printCPPTemplates(),
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
    
    def printCPPTemplates(self):
        """Stringify cpp templates"""
        if len(self.cppTemplates) > 0:
            return "\n---\n Templates :\n "+"\n ".join(self.cppTemplates)
        return ""

class TClassField:
    """Individual fields within a TClass"""
    def __init__(self):
        self.name =     "VOIDFIELD"
        self.comment =  "VOIDFIELD"
        self.type =     "VOIDFIELD"
        self.size =     "VOIDFIELD"
    
    def populate(self, template):
        """Populate the fields containers and make sure everything looks sane
        
        info is a dictionary that describes the fields attributes
        """
        valid_keys = ['name',
                      'type',
                      'size',
                      'comment']
        for key in template:
            if key not in valid_keys:
                raise VHA_BadKeywordException("Unknown FIELD keyword %s" % key)
        try:
            self.type = template['type']
        except KeyError:
            raise VHA_MissingKeywordException("'type' keyword not defined for %r" % template)
        try:
            self.comment = template['comment']
        except KeyError:
            raise VHA_MissingKeywordException("'comment' keyword not defined for %r" % template)
        try:
            self.size = template['size']
        except KeyError:
            raise VHA_MissingKeywordException("'size' keyword not defined for %r" % template)
        try:
            self.name = template['name']
        except KeyError:
            raise VHA_MissingKeywordException("'name' keyword not defined for %r" % template)
        
    def __str__(self):
        return " ...\n  Name: %s\n  Type: %s\n  Size: %s\n  Comment: %s" % (self.name,
                                                                            self.type,
                                                                            self.size,
                                                                            self.comment)
    def __repr__(self):
        return self.__str__()
    
###############################################################################
###############################################################################
###############################################################################
###############################################################################