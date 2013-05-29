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

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class TCBuilder:
    def __init__(self): pass
    
    def parseTemplate(self, templateFileName):
        """Parse the template file and create classTemplate instances"""
        strippedJSON = StringIO.StringIO()
        with open(templateFileName,'r') as f:
            for line in f:
                strippedJSON.write(self.removeComments(line))
            
        strippedJSON_fh = StringIO.StringIO(strippedJSON.getvalue())
        strippedJSON.close()
        data = json.load(strippedJSON_fh)
        print json.dumps(data, separators=(',',':'))
        strippedJSON_fh.close()

    def removeComments(self, string):
        """Strip C/C++ style comments from a string
        
        From: http://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
        """
        string = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,string) # remove all occurance streamed comments (/*COMMENT */) from string
        string = re.sub(re.compile("//.*?\n" ) ,"" ,string) # remove all occurance singleline comments (//COMMENT\n ) from string
        return string

###############################################################################
###############################################################################
###############################################################################
###############################################################################