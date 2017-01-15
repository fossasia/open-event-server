#based on zlib-1.2.5/CMakeLists.txt
#
cmake_minimum_required(VERSION 2.6)
SET(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS ON)

PROJECT(zlib C)

INCLUDE(CheckTypeSize)
INCLUDE(CheckFunctionExists)
INCLUDE(CheckIncludeFile)
INCLUDE(CheckCSourceCompiles)

CHECK_INCLUDE_FILE(sys/types.h HAVE_SYS_TYPES_H)
CHECK_INCLUDE_FILE(stdint.h    HAVE_STDINT_H)
CHECK_INCLUDE_FILE(stddef.h    HAVE_STDDEF_H)

#
# Check to see if we have large file support
#
SET(CMAKE_REQUIRED_DEFINITIONS -D_LARGEFILE64_SOURCE=1)
# We add these other definitions here because CheckTypeSize.cmake
# in CMake 2.4.x does not automatically do so and we want
# compatibility with CMake 2.4.x.
IF(HAVE_SYS_TYPES_H)
    LIST(APPEND CMAKE_REQUIRED_DEFINITIONS -DHAVE_SYS_TYPES_H)
ENDIF()
IF(HAVE_STDINT_H)
    LIST(APPEND CMAKE_REQUIRED_DEFINITIONS -DHAVE_STDINT_H)
ENDIF()
IF(HAVE_STDDEF_H)
    LIST(APPEND CMAKE_REQUIRED_DEFINITIONS -DHAVE_STDDEF_H)
ENDIF()
CHECK_TYPE_SIZE(off64_t OFF64_T)
IF(HAVE_OFF64_T)
   ADD_DEFINITIONS(-D_LARGEFILE64_SOURCE=1)
ENDIF()
SET(CMAKE_REQUIRED_DEFINITIONS) # clear variable
#
# Check for fseeko
#
CHECK_FUNCTION_EXISTS(fseeko HAVE_FSEEKO)
IF(NOT HAVE_FSEEKO)
    ADD_DEFINITIONS(-DNO_FSEEKO)
ENDIF()
#
# Check for unistd.h
#
CHECK_INCLUDE_FILE(unistd.h Z_HAVE_UNISTD_H)

INCLUDE_DIRECTORIES(
 ${CMAKE_CURRENT_SOURCE_DIR}
 ${OPENJPEG_SOURCE_DIR}/thirdparty/include
)
#
SET(EXT_HDRS
 ${OPENJPEG_SOURCE_DIR}/thirdparty/include/zlib.h
 ${OPENJPEG_SOURCE_DIR}/thirdparty/include/zconf.h
)

SET(HDRS
    crc32.h
    deflate.h
    gzguts.h
    inffast.h
    inffixed.h
    inflate.h
    inftrees.h
    trees.h
    zutil.h
)
SET(SRCS
    adler32.c
    compress.c
    crc32.c
    deflate.c
    gzclose.c
    gzlib.c
    gzread.c
    gzwrite.c
    inflate.c
    infback.c
    inftrees.c
    inffast.c
    trees.c
    uncompr.c
    zutil.c
)

SET(LIBTARGET "z")
#
ADD_LIBRARY(${LIBTARGET} STATIC ${SRCS} ${EXT_HDRS} ${HDRS})
#
IF(MSVC)
  SET_TARGET_PROPERTIES(${LIBTARGET} PROPERTIES PREFIX "lib")
ENDIF(MSVC)

SET_TARGET_PROPERTIES(${LIBTARGET}
    PROPERTIES
    OUTPUT_NAME "${LIBTARGET}"
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/thirdparty/lib
)
#
