// --------------------------------------------------------------------
// File: idTypeDefs.h
// Original Authors: Dominic Eales and Michael Imelfort
// --------------------------------------------------------------------
//
// OVERVIEW:
// This file contains the definitions for generic ID types.
// These are implemented at uMDInt's but any relation to actual ints is
// stripped away leaving a new 32 bit ID which is only defined
// under assignment and comparison (==, < and !=).
// Think of it as an int wrapped in a class, wrapped in an enigma...
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

#ifndef Id_Type_H
    #define Id_Type_H

// system includes
#include <iostream>
#include <fstream>

// local includes
#include "intdef.h"

using namespace std;

/////////////////////////////////////////////////
// Do not define the base type for the ID TYPE classes here
// It is defined in intdef.h, these calculations rely on the value set there

#ifdef SIZE_OF_IDTYPE
# if (SIZE_OF_IDTYPE == 64)
#  define ID_ZERO         ((idInt)0x0000000000000000)
#  define ID_BLOCK_UNUSED ((idInt)0xBBaaaaddFF0000dd)
# elif (SIZE_OF_IDTYPE == 32)
#  define ID_ZERO         ((idInt)0x00000000)
#  define ID_BLOCK_UNUSED ((idInt)0xBaadF00d)
# else
#  error SIZE_OF_IDTYPE not correct
# endif
#else
# error SIZE_OF_IDTYPE not defined
#endif

#define IDTYPE idInt

/////////////////////////////////////////////////
// Can't touch this

// forward declarations
template<typename MMSTRUCTTYPE>
class MemManager;
template<typename MMSTRUCTTYPE>
class DeletableMemManager;

#define DEFINE_ID_TYPE( nAME , mEMmANAGERnAME, __tEMPLATEdEFINITION__ ) \
__tEMPLATEdEFINITION__ \
class mEMmANAGERnAME; /* forward declaration */\
class nAME { \
  private:\
	IDTYPE _x;\
\
	inline IDTYPE get(void)	{ \
		return _x; }\
	inline void   set(IDTYPE a) { _x = a; } \
	inline bool   is_equal(IDTYPE b) { \
		return (_x == b)? 1:0;}\
	inline bool   not_equal(IDTYPE b) { \
		return (_x != b)? 1:0;}\
	inline IDTYPE add(IDTYPE a)		{ \
		_x += a; return _x;}\
	inline IDTYPE subtract(IDTYPE a)	{ \
		_x -= a; return _x;}\
\
    template<typename MMSTRUCTTYPE>\
    friend class MemManager;\
    template<typename MMSTRUCTTYPE>\
    friend class DeletableMemManager;\
    __tEMPLATEdEFINITION__ \
    friend class mEMmANAGERnAME;\
\
  public:\
	nAME()  { _x = getnamehash(); }\
    nAME(std::ifstream * fh) { \
        fh->read(reinterpret_cast<char *>(&_x), sizeof(IDTYPE));} \
    ~nAME() { }\
	inline void operator =(nAME a)	{ \
		_x = a._x; }\
	inline bool operator ==(const nAME b) const { \
		return (_x == b._x)? 1:0;}\
	inline bool operator !=(const nAME b) const { \
		return (_x != b._x)? 1:0;} \
    inline bool operator <(const nAME& b) const { \
        return _x < b._x;} \
    inline void save(std::ofstream * fh) const { \
        fh->write((char *)(&_x), sizeof(IDTYPE));} \
    inline bool isbadfood(void) const { \
        return ( ID_BLOCK_UNUSED == (IDTYPE)_x ); }\
    inline IDTYPE getnamehash(void) { \
        const char * p = #nAME; \
        return ((IDTYPE)((uMDInt)p))^((IDTYPE)ID_BLOCK_UNUSED); }\
    inline IDTYPE getuniquehash(void) { \
        const char * p = #nAME; \
        return ((IDTYPE)((uMDInt)p))^((IDTYPE)ID_BLOCK_UNUSED)^(_x << (SIZE_OF_IDTYPE/2)); }\
    inline IDTYPE getGuts(void) { \
        return _x; }\
        friend ostream& operator <<(ostream &s, nAME a) { s << #nAME << ":" << std::hex << a._x << std::dec; return s; } \
\
}; 
//***********************************************
/////////////////////////////////////////////////
// Define your list of ID TYPE classes
//
// DEFINE_ID_TYPE(SomeId, SomeMemManager, );
// DEFINE_ID_TYPE(SomeOtherId, SomeOtherMemManager, );
//
/////////////////////////////////////////////////
// Definitions automatically added by VHA
//
//VHA
//
/////////////////////////////////////////////////

#endif // Id_Type_H
