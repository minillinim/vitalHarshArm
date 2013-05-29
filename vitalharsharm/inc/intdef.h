// --------------------------------------------------------------------
// File: intdef.h
// Original Author: Dominic Eales and Michael Imelfort
// --------------------------------------------------------------------
//
// OVERVIEW:
// Wrapper for defining different size ints
//
// --------------------------------------------------------------------
// Copyright (C) 2009 - 2013 Michael Imelfort and Dominic Eales
// --------------------------------------------------------------------
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
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

#ifndef IntDef_h
    #define IntDef_h

    //
    // how to define 32/64 bit integers on your compiler?
    // set this up so that: sizeof(uint_64t) == 8
    // and: sizeof(uint_32t) == 4
    //
    
	# define SIZE_OF_INT    64

    //
    // All internal memory pointers are set as either 32 or 64 bit ints
    // and then wrapped up accordingly.
    //

	# define SIZE_OF_IDTYPE 32

	//
	// Make sure we KNOW what these terms mean
    //

	typedef unsigned long long uint_64t;
	typedef signed long long   sint_64t;
	
	typedef unsigned int       uint_32t;
	typedef signed int         sint_32t;
	
	typedef unsigned short     uint_16t;
	typedef signed short       sint_16t;
	
	typedef unsigned char      uint_8t;
	typedef signed char        sint_8t;
	
	//
	// Shorthand wrapper for our longest ints
	//
	
	#ifdef SIZE_OF_INT
	# if (SIZE_OF_INT == 64)
		typedef uint_64t uMDInt;
		typedef sint_64t sMDInt;
	# elif (SIZE_OF_INT == 32)
		typedef uint_32t uMDInt;
		typedef sint_32t sMDInt;
	# else
	#  error SIZE_OF_INT not correct
	# endif
		
	//
	// Id types
    //
		
	# if (SIZE_OF_IDTYPE == 64)
	   typedef uint_64t           idInt;
	# elif (SIZE_OF_IDTYPE == 32)
	   typedef uint_32t           idInt;
	# else
	#  error SIZE_OF_IDTYPE not correct
	# endif
	
	#else
	# error SIZE_OF_INT not defined
	#endif

#endif // IntDef_h

