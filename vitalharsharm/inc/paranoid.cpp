// --------------------------------------------------------------------
// File: paranoid.cpp
// Original Authors: Dominic Eales and Michael Imelfort
// --------------------------------------------------------------------
//
// OVERVIEW:
// For debug mode. Lots of checking and printing functions (MACROS) to use
//
// --------------------------------------------------------------------
// Copyright (C) 2009 - 2014 Michael Imelfort and Dominic Eales
// --------------------------------------------------------------------
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 2.1 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//
// --------------------------------------------------------------------

#ifdef MAKE_PARANOID

#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <stdexcept>
#include "paranoid.h"

using namespace std;
void __paraAssert(const char * condition, const char * function, const char * file, int linenum)
{
#if EXIT_ON_ASSERT==1
    std::ostringstream oss;
    oss << "--------------------\nparaFAIL: " << condition << "\n" << "File: " << file << ":" << linenum << "\nFunction: " << function << endl;
    throw std::out_of_range(oss.str());
#else
    cerr << "--------------------\nparaFAIL: " << condition << "\n" << "File: " << file << ":" << linenum << "\nFunction: " << function << endl;
#endif
}

#endif //MAKE_PARANOID