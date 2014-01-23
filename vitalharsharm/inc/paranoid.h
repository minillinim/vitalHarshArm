// --------------------------------------------------------------------
// File: paranoid.h
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


# ifndef PARANOID_H
# define PARANOID_H

// define all paranoid statements to do nothing
# define PARANOID_ASSERT(cONDITION)
# define PARANOID_ASSERT_PRINT(cONDITION, pRINTiNFO)
# define PARANOID_INFO(cOUTsTRING)

# endif // PARANOID_H

#ifdef MAKE_PARANOID
// some paranoid parameters
#define EXIT_ON_ASSERT 1

// forward declaration of assert function
void __paraAssert(const char * condition, const char * function, const char * file, int linenum);

// ASSERT Macros
#undef PARANOID_ASSERT
#define PARANOID_ASSERT(cOND) {if(!(cOND)){__paraAssert(#cOND,__PRETTY_FUNCTION__,__FILE__,__LINE__);}}
#undef PARANOID_ASSERT_PRINT
#define PARANOID_ASSERT_PRINT(cOND,pRINT) {if(!(cOND)){__paraAssert(#cOND,__PRETTY_FUNCTION__,__FILE__,__LINE__); { std::cerr << "Info: " << pRINT << std::endl; } }}
#ifdef PARANOID_INFO
    #undef PARANOID_INFO
    #define PARANOID_INFO(cOUTsTRING) {std::cout << "--------------------\nparaINFO: " __FILE__ << ":" << __LINE__ << "\nMessage: " << cOUTsTRING << std::endl;}
#endif

#endif // MAKE_PARANOID