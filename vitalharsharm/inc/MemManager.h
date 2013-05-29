// --------------------------------------------------------------------
// File: MemManager.h
// Original Authors: Michael Imelfort and Dominic Eales
// --------------------------------------------------------------------
//
// OVERVIEW:
// This file contains the class definitions for the data management
// object. This object implements a dynamic memory management system
// which I think is kinda kool.
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

#ifndef MemManager_h
    #define MemManager_h

using namespace std;

// system includes
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <string.h>
                 
// local includes
#include "intdef.h"

#ifdef SIZE_OF_INT
# if (SIZE_OF_INT == 64)
#  define MM_ZERO         ((uMDInt)0x0000000000000000)
#  define MM_BLOCK_UNUSED ((uMDInt)0xBBaaaaddFF0000dd)
# elif (SIZE_OF_INT == 32)
#  define MM_ZERO         ((uMDInt)0x00000000)
#  define MM_BLOCK_UNUSED ((uMDInt)0xBaadF00d)
# else
#  error SIZE_OF_INT not correct
# endif
#else
# error SIZE_OF_INT not defined
#endif
                 
#define MM_ADDR_NULL    ((uMDInt*)0)
   
template <int MMBLOCKSIZE>
class MemManager {

    public:
		std::string           _name;
	
        // Construction and destruction
        MemManager() {
            _className = "MemManager";
            _nextNewId = 0;
            _numBlocksAvailableInLastChunk = 0;
            _initialised = false;
            _name = "";
#ifdef SHOW_MEM
            peak_used = 0;
            peak_alloc = 0;
            re_allocs = 0;
#endif

        };
        virtual ~MemManager() {
#ifdef SHOW_MEM
            idInt total_alloc, total_used;
            getUsageData(&total_alloc, &total_used);
            std::cout << "MM: " << _name << ": At destructor: - Allocated: " << total_alloc << " bytes, Used: " << total_used << " bytes" << std::endl;
            std::cout << "MM: " << _name << ": Peak - Allocated: " << (peak_alloc * MMBLOCKSIZE * sizeof(uMDInt)) << " bytes, Used: " << (peak_used * MMBLOCKSIZE * sizeof(uMDInt))<< " bytes" << std::endl;
#endif
            freeMemory();
        }

        // Init functions
        bool initialise( 
            idInt                numBlocksInInitialChunk,
            std::vector<idInt>   subsequentChunkSizeDivisors )
        {
#ifdef SHOW_MEM
            std::cout << "MM: " << _name << ": Initially allocating: " << numBlocksInInitialChunk << " blocks at: " << MMBLOCKSIZE << ", Total: " << (numBlocksInInitialChunk * MMBLOCKSIZE * sizeof(uMDInt)) << " bytes" << std::endl;
#endif
            if (_initialised == true)
                return true;
	
            // create the chunk sizes from the parameters
            unsigned int idx;
            idInt numBlocksInChunk = numBlocksInInitialChunk;
            for (idx = 0; idx < subsequentChunkSizeDivisors.size(); idx++)
            {
                _chunkSizes.push_back( numBlocksInChunk );
                numBlocksInChunk = numBlocksInInitialChunk/subsequentChunkSizeDivisors[idx];
            }
            _chunkSizes.push_back( numBlocksInChunk );
        
            // set initialised
            _initialised = true;
        
            // allocate the first chunk
            if (!allocateNewChunk()) {
                _initialised = false;
#ifdef SHOW_MEM
                std::cout << "MM: " << _name << " Could not allocate memory!" << std::endl;
#endif
                return false;
            }
        
            return true;
        }

        // Access functions
        inline bool isValidAddress( idInt id )
        {
            uMDInt * addr;

            // do something finally
            if ( _chunkList.size() == 1 ) {
                addr = &((_chunkList[0])[id]);
            } else {
                unsigned int chunkIdx = 0;
                while (id >= _chunkTotalNumIds[chunkIdx]) {
                    chunkIdx++;
                    if (chunkIdx == _chunkList.size()) { return false; };
                }
                addr = &((_chunkList[chunkIdx])[id-_chunkFirstId[chunkIdx]]);
            }

            return (addr != MM_ADDR_NULL && addr[0] != MM_BLOCK_UNUSED);
        }

        inline uMDInt * getAddress( idInt id ) {
            //-----
            // Return a pointer to the start int of the block.
            //
            uMDInt * addr;

            // do something finally
            if ( _chunkList.size() == 1 ) {
                addr = &((_chunkList[0])[id]);
            } else {
                unsigned int chunkIdx = 0;
                while (id >= _chunkTotalNumIds[chunkIdx]) {
                    chunkIdx++;
                    if (chunkIdx == _chunkList.size()) { return MM_ADDR_NULL; };
                }
                addr = &((_chunkList[chunkIdx])[id-_chunkFirstId[chunkIdx]]);
            }

            return addr;
        }

        inline void setAddressUsed( idInt id ) {
        	//-----
            // reset any MM_BLOCK_UNUSED flags
        	//
            uMDInt * addr;

            // do something finally
            if ( _chunkList.size() == 1 ) {
                addr = &((_chunkList[0])[id]);
            } else {
                unsigned int chunkIdx = 0;
                while (id >= _chunkTotalNumIds[chunkIdx]) {
                    chunkIdx++;
                    if (chunkIdx == _chunkList.size()) { return; };
                }
                addr = &((_chunkList[chunkIdx])[id-_chunkFirstId[chunkIdx]]);
            }

            addr[0] = MM_ZERO;
        }

        // Wrapping and unwrapping IdTypes
        template <class T>
        inline void wrapId(idInt rawId, T * idType)
        {
            // wrap the value in rawId in an IdType of type T
            idType->set(rawId);
        }
        
        template <class T>
        inline idInt unWrapId(T idType)
        {
            // get the guts of the idType and return as an idInt
            return idType.get();
        }

        // Add functions
        idInt getNewId(void)
        {
            idInt thisId;
            if ( _numBlocksAvailableInLastChunk == 0 ) {
                if (!allocateNewChunk()) {
                	std::cout << "ERROR: allocateNewChunk returned 'Out of memory'" << std::endl
                }
            }
            thisId = _nextNewId;
#ifdef SHOW_MEM
            peak_used++;
#endif
            _nextNewId += (idInt)MMBLOCKSIZE;
            _numBlocksAvailableInLastChunk--;

            // get rid of any MM_BLOCK_UNUSED flags
            MemManager<MMBLOCKSIZE>::setAddressUsed( thisId );
            return thisId;
        }

        void getUsageData( idInt * totalBytesAllocated, idInt * maxBytesUsed ) {
            if (totalBytesAllocated != NULL ) {
                *totalBytesAllocated = _chunkTotalNumIds.back() * MMBLOCKSIZE * sizeof(uMDInt);
            }
            if (maxBytesUsed != NULL ) {
                *maxBytesUsed = _nextNewId * MMBLOCKSIZE * sizeof(uMDInt);
            }
        }
        
    protected:
        // housekeeping
        bool   _initialised;
        const char * _className;
    
        // Memory chunk vars
        idInt                 _nextNewId;
        idInt                 _numBlocksAvailableInLastChunk;
        std::vector<uMDInt *> _chunkList;
        std::vector<idInt>    _chunkSizes;
        std::vector<idInt>    _chunkFirstId;
        std::vector<idInt>    _chunkTotalNumIds;

#ifdef SHOW_MEM
        idInt peak_alloc, peak_used, re_allocs;  
#endif
        // Chunk management
        inline bool allocateNewChunk() {

            unsigned int chunkIdx;
            idInt newChunkSize;
            uMDInt *pNewChunk;

            // find the appropriate size
            chunkIdx = _chunkList.size();
            // if we can't find a size for this chunk, just use the last available chunk size
            if ( chunkIdx > _chunkSizes.size()-1 ) {
                chunkIdx = _chunkSizes.size()-1;
            }
            newChunkSize = _chunkSizes[chunkIdx] * MMBLOCKSIZE;

#ifdef SHOW_MEM
            std::cout << "MM: " << _name << ": New chunk - Adding: " << _chunkSizes[chunkIdx] << " blocks at: " << MMBLOCKSIZE << ", Total: " << (newChunkSize * sizeof(uMDInt)) << " bytes" << std::endl;
            peak_alloc += _chunkSizes[chunkIdx];
            re_allocs++;
#endif

            // allocate memory
            pNewChunk = new uMDInt[newChunkSize];
            if ( pNewChunk != NULL ) {

                uMDInt * addr;
                idInt   counter;

                // empty it
                memset( pNewChunk, 0, newChunkSize * sizeof(uMDInt) );

                // put in MM_BLOCK_UNUSED flags
                addr = pNewChunk;
                counter = 0;
                while (counter < _chunkSizes[chunkIdx]) {
                    addr[0] = MM_BLOCK_UNUSED;
                    addr += MMBLOCKSIZE;
                    counter++;
                }

                // update lists
                _chunkList.push_back( pNewChunk );
                _chunkFirstId.push_back( _nextNewId );
                _chunkTotalNumIds.push_back( (_nextNewId + newChunkSize) );
                _numBlocksAvailableInLastChunk = _chunkSizes[chunkIdx];
            }
            return ( pNewChunk != NULL );
        }

        void freeMemory(void) {
            for (unsigned int chunkIdx = 0; chunkIdx < _chunkList.size(); chunkIdx++) {
                delete[] _chunkList[chunkIdx];
            }
            _nextNewId = 0;
            _numBlocksAvailableInLastChunk = 0;
            _initialised = false;
            _chunkList.clear();
            _chunkSizes.clear();
            _chunkFirstId.clear();
            _chunkTotalNumIds.clear();
        }
};

template <int MMBLOCKSIZE>
class DeletableMemManager : public MemManager<MMBLOCKSIZE> {

    public:
        // Construction and destruction
        DeletableMemManager() {
            MemManager<MMBLOCKSIZE>::_className = "DeletableMemManager";
        }
        virtual ~DeletableMemManager() {
            MemManager<MMBLOCKSIZE>::freeMemory();
        }

        // Access functions
        inline uMDInt * getAddress( idInt id ) {

            uMDInt * addr = MemManager<MMBLOCKSIZE>::getAddress(id);

            // check if empty block
            if (  ( addr != MM_ADDR_NULL )
                &&( addr[0] == MM_BLOCK_UNUSED ) ) {

                return MM_ADDR_NULL;
            }

            return addr;
        }

        // Add functions
        idInt getNewId(void) {

            // if there is something on the list then give that index back
            if ( _deletedIdList.size() != 0 ) {

                idInt retIndex = _deletedIdList[_deletedIdList.size()-1];
                _deletedIdList.pop_back();

                // unset the unused flags
                MemManager<MMBLOCKSIZE>::setAddressUsed( retIndex );

                // done!
                return retIndex;
            }

            return MemManager<MMBLOCKSIZE>::getNewId();
        }

        // Delete function
        inline bool _freeId( 
               idInt id
        ) {

            // get the address
            uMDInt * addr = MemManager<MMBLOCKSIZE>::getAddress( id );

            // if success then delete the block
            if ( addr != MM_ADDR_NULL ) {
                // empty it
                memset( addr, 0, MMBLOCKSIZE * sizeof(uMDInt));

                // set block as unused
                addr[0] = MM_BLOCK_UNUSED;

                // add the address to the deleted list
                _deletedIdList.push_back( id );

                return true;
            }
            return false;
        }

    private:
        std::vector<idInt> _deletedIdList;

};

#endif // MemManager_h
