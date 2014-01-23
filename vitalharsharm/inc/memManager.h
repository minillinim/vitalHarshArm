// --------------------------------------------------------------------
// File: memManager.h
// Original Authors: Michael Imelfort and Dominic Eales
// --------------------------------------------------------------------
//
// OVERVIEW:
// This file contains the class definitions for the data management
// object. This object implements a dynamic memory management system
// which I think is kinda kool.
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

#ifndef MemManager_h
#define MemManager_h

using namespace std;

// system includes
#include <iostream>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <string>
#include <string.h>
#include <stdexcept>

// local includes
#include "intdef.h"3
#include "paranoid.h"

//#define MM_ADDR_NULL    ((uMDInt*)0)

template <typename MMSTRUCTTYPE>
class MemManager {
    
public:
    MMSTRUCTTYPE * MM_ADDR_NULL;
    std::string           _name;    // set during call to initialise
    // Construction and destruction
    MemManager() {
        MM_ADDR_NULL = (MMSTRUCTTYPE*)0;
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
        std::cout << "MM: " << _name << ": Peak - Allocated: " << (peak_alloc * sizeof(MMSTRUCTTYPE)) << " bytes, Used: " << (peak_used * sizeof(MMSTRUCTTYPE))<< " bytes" << std::endl;
        #endif
        freeMemory();
    }
    
    // Init functions
    bool initialise( 
    idInt                numBlocksInInitialChunk,
    std::vector<idInt>   subsequentChunkSizeDivisors )
    {
        #ifdef SHOW_MEM
        //std::cout << "MM: " << _name << ": Initially allocating: " << numBlocksInInitialChunk << " blocks at: " << MMBLOCKSIZE << ", Total: " << (numBlocksInInitialChunk * MMBLOCKSIZE * sizeof(uMDInt)) << " bytes" << std::endl;
        #endif
        PARANOID_ASSERT(_initialised == false);
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
            
            // allocate the first chunk
            _initialised = true;
            if (!allocateNewChunk()) {
                return false;
                _initialised = false;
            }
            
            // set initialised
            return true;
    }
    
    // Access functions
    inline bool isValidAddress( idInt id )
    {
        PARANOID_ASSERT((_initialised));
        PARANOID_ASSERT((id<_chunkTotalNumIds[_chunkList.size()-1]));
        MMSTRUCTTYPE * addr;
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
        
        return (addr != MM_ADDR_NULL);
    }
    
    inline MMSTRUCTTYPE * getAddress( idInt id ) {
        //-----
        // Return a pointer to the struct we want
        //
        PARANOID_ASSERT((_initialised));
        PARANOID_ASSERT((id<_chunkTotalNumIds[_chunkList.size()-1]));
        MMSTRUCTTYPE * addr;
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
        PARANOID_ASSERT(addr != MM_ADDR_NULL);
        return addr;
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
        if ( _numBlocksAvailableInLastChunk == 0 )
            allocateNewChunk();
        thisId = _nextNewId;
        #ifdef SHOW_MEM
        ++peak_used;
        #endif
        ++_nextNewId;
        --_numBlocksAvailableInLastChunk;
        
        return thisId;
    }
    
    void getUsageData( idInt * totalBytesAllocated, idInt * maxBytesUsed ) {
        if (totalBytesAllocated != NULL ) {
            *totalBytesAllocated = _chunkTotalNumIds.back() * sizeof(MMSTRUCTTYPE);
        }
        if (maxBytesUsed != NULL ) {
            *maxBytesUsed = _nextNewId * sizeof(MMSTRUCTTYPE);
        }
    }
    
    #ifdef MAKE_PARANOID
    void debugvars(void)
    {
        unsigned int i;
        #define DO_VAR(vAR) PARANOID_INFO( #vAR "=" << vAR)
        DO_VAR(_initialised);
        DO_VAR(_nextNewId);
        DO_VAR(_numBlocksAvailableInLastChunk);
        #define DO_LIST(vAR) for (i=0;i<vAR.size();i++) PARANOID_INFO( #vAR "[" << i << "]=" << vAR[i])
        DO_LIST(_chunkList);
        DO_LIST(_chunkSizes);
        DO_LIST(_chunkFirstId);
        DO_LIST(_chunkTotalNumIds);
    }
    #endif        
    
protected:
    // housekeeping
    bool                  _initialised;
    const char*           _className;
    
    // Memory chunk vars
    idInt                 _nextNewId;
    idInt                 _numBlocksAvailableInLastChunk;
    std::vector<MMSTRUCTTYPE *> _chunkList;
    std::vector<idInt>    _chunkSizes;
    std::vector<idInt>    _chunkFirstId;
    std::vector<idInt>    _chunkTotalNumIds;
    
    #ifdef SHOW_MEM
    idInt peak_alloc, peak_used, re_allocs;  
    #endif
    // Chunk management
    inline bool allocateNewChunk() {
        PARANOID_ASSERT(_initialised);
        PARANOID_ASSERT(_numBlocksAvailableInLastChunk == 0);
        
        unsigned int chunkIdx;
        idInt newChunkSize;
        MMSTRUCTTYPE *pNewChunk;
        
        // find the appropriate size
        chunkIdx = _chunkList.size();
        // if we can't find a size for this chunk, just use the last available chunk size
        if ( chunkIdx > _chunkSizes.size()-1 ) {
            chunkIdx = _chunkSizes.size()-1;
        }
        newChunkSize = _chunkSizes[chunkIdx];
        
        #ifdef SHOW_MEM
        std::cout << "MM: " << _name << ": New chunk - Adding: " << _chunkSizes[chunkIdx] << " blocks at: " << sizeof(MMSTRUCTTYPE) << ", Total: " << (newChunkSize * sizeof(MMSTRUCTTYPE)) << " bytes" << std::endl;
        peak_alloc += _chunkSizes[chunkIdx];
        re_allocs++;
        #endif
        
        // allocate memory
        pNewChunk = (MMSTRUCTTYPE*)calloc(sizeof(MMSTRUCTTYPE), newChunkSize);
        if ( pNewChunk != NULL ) {
            // update lists
            _chunkList.push_back( pNewChunk );
            _chunkFirstId.push_back( _nextNewId );
            _chunkTotalNumIds.push_back( (_nextNewId + newChunkSize) );
            _numBlocksAvailableInLastChunk = _chunkSizes[chunkIdx];
        }
        else
        {
            std::cerr << "["<< _name <<"] " << _name << " Could not allocate memory!" << std::endl;
            throw std::bad_alloc();            
        }
        return ( pNewChunk != NULL );
    }
    
    void freeMemory(void) {
        for (unsigned int chunkIdx = 0; chunkIdx < _chunkList.size(); chunkIdx++) {
            free(_chunkList[chunkIdx]);
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

#ifdef MAKE_PARANOID
class DeletedIdDebugInfo {
public:
    const char *fname;
    int linenum;
};
#endif

template <typename MMSTRUCTTYPE>
class DeletableMemManager : public MemManager<MMSTRUCTTYPE> {
    
public:
    std::string           _name;    // set during call to initialise
    MMSTRUCTTYPE * MM_ADDR_NULL;
    
    // Construction and destruction
    DeletableMemManager() {
        MemManager<MMSTRUCTTYPE>::_className = "DeletableMemManager";
        MM_ADDR_NULL = (MMSTRUCTTYPE*)0;
    }
    virtual ~DeletableMemManager() {
        MemManager<MMSTRUCTTYPE>::freeMemory();
    }
    
    // Access functions
    inline MMSTRUCTTYPE * getAddress( idInt id ) {
        
        // check to see if the address has been deleted
        if(_deletedIds.find(id) != _deletedIds.end()){
            // address in the deleted list
            PARANOID_INFO("Requested deleted block, ID: " << id << ": [ " << _name << " ]" << " deleted on line " << _deletedIdInfo[id].linenum << " of " << _deletedIdInfo[id].fname);
            std::ostringstream oss;
            oss << "["<< _name <<"] " << _name << "Requested deleted block, ID: " << id << std::endl;
            throw std::invalid_argument(oss.str());            
            return MM_ADDR_NULL;
        }
        
        return MemManager<MMSTRUCTTYPE>::getAddress(id);
    }
    
    // Add functions
    idInt getNewId(void) {
        
        // if there is something on the list then give that index back
        if ( _deletedIds.size() != 0 ) {
            std::map<idInt, bool>::iterator id_it = _deletedIds.begin();
            idInt retIndex = id_it->first;
            _deletedIds.erase(id_it);   // erase using the iterator we already have
            #ifdef MAKE_PARANOID
            _deletedIdInfo.erase(retIndex); // erase using the key
            #endif
            
            // done!
            return retIndex;
        }
        
        return MemManager<MMSTRUCTTYPE>::getNewId();
    }
    
    #ifdef MAKE_PARANOID
    # define freeId(iDeNiFiEr) _freeId(iDeNiFiEr,__FILE__,__LINE__)
    #else
    # define freeId(iDeNiFiEr) _freeId(iDeNiFiEr)
    #endif
    
    // Delete function
    inline bool _freeId(
        idInt id
        #ifdef MAKE_PARANOID
        , const char *fname, int linenum
        #endif            
    ) {
        
        // get the address
        MMSTRUCTTYPE * addr = MemManager<MMSTRUCTTYPE>::getAddress( id );
        
        // if success then delete the block
        if ( addr != MM_ADDR_NULL ) {
            _deletedIds[id] = true;
            #ifdef MAKE_PARANOID
            DeletedIdDebugInfo dbgInfo;
            dbgInfo.fname = fname;
            dbgInfo.linenum = linenum;
            _deletedIdInfo[id] = dbgInfo;
            #endif                
            return true;
        }
        std::ostringstream oss;
        oss << "["<< _name <<"] " << _name << "Attempt to free NULL id, ID: " << id << std::endl;
        throw std::invalid_argument(oss.str());            
        return false;
    }
    
private:
    std::map<idInt, bool> _deletedIds;
    #ifdef MAKE_PARANOID
    std::map<idInt, DeletedIdDebugInfo> _deletedIdInfo;
    #endif
};

#endif // MemManager_h
