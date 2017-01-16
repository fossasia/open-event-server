# 3rd party libs

#------------
# Try to find lib Z
IF(BUILD_THIRDPARTY)
  # Try to build it
  message(STATUS "We will build Z lib from thirdparty")
  ADD_SUBDIRECTORY(libz)
  SET(Z_LIBNAME z PARENT_SCOPE)
  SET(Z_INCLUDE_DIRNAME ${OPENJPEG_SOURCE_DIR}/thirdparty/include PARENT_SCOPE)
  SET(ZLIB_FOUND 1)
ELSE (BUILD_THIRDPARTY)
  # Try to find lib Z
  FIND_PACKAGE(ZLIB)
  IF(ZLIB_FOUND)
    SET(Z_LIBNAME ${ZLIB_LIBRARIES} PARENT_SCOPE)
    SET(Z_INCLUDE_DIRNAME ${ZLIB_INCLUDE_DIRS} PARENT_SCOPE)
    message(STATUS "Your system seems to have a Z lib available, we will use it to generate PNG lib")
    # message(STATUS "DEBUG: ${ZLIB_INCLUDE_DIRS} vs ${ZLIB_INCLUDE_DIR}")
  ELSE (ZLIB_FOUND) # not found
    message(STATUS "Z lib not found, activate BUILD_THIRDPARTY if you want build it (necessary to build libPNG)")
  ENDIF(ZLIB_FOUND)
ENDIF(BUILD_THIRDPARTY)


#------------
# Try to find lib PNG (which depends on zlib)
IF(BUILD_THIRDPARTY)
  # Try to build it
  message(STATUS "We will build PNG lib from thirdparty")
  ADD_SUBDIRECTORY(libpng)
  SET(OPJ_HAVE_PNG_H 1 PARENT_SCOPE)
  SET(OPJ_HAVE_LIBPNG 1 PARENT_SCOPE)
  SET(PNG_LIBNAME png PARENT_SCOPE)
  SET(PNG_INCLUDE_DIRNAME ${OPENJPEG_SOURCE_DIR}/thirdparty/libpng PARENT_SCOPE)
ELSE (BUILD_THIRDPARTY)
  IF (ZLIB_FOUND)
    FIND_PACKAGE(PNG)
    IF(PNG_FOUND)
      message(STATUS "Your system seems to have a PNG lib available, we will use it")
      SET(OPJ_HAVE_PNG_H 1 PARENT_SCOPE)
      SET(OPJ_HAVE_LIBPNG 1 PARENT_SCOPE)
      SET(PNG_LIBNAME ${PNG_LIBRARIES} PARENT_SCOPE)
      SET(PNG_INCLUDE_DIRNAME ${PNG_PNG_INCLUDE_DIR} PARENT_SCOPE)
    ELSE(PNG_FOUND) # not found
      SET(OPJ_HAVE_PNG_H 0 PARENT_SCOPE)
      SET(OPJ_HAVE_LIBPNG 0 PARENT_SCOPE)
      message(STATUS "PNG lib not found, activate BUILD_THIRDPARTY if you want build it")
    ENDIF(PNG_FOUND)
  ENDIF (ZLIB_FOUND)
ENDIF(BUILD_THIRDPARTY)

#------------
# Try to find lib TIFF

IF(BUILD_THIRDPARTY)
  # Try to build it
  message(STATUS "We will build TIFF lib from thirdparty")
  ADD_SUBDIRECTORY(libtiff)
  SET(TIFF_LIBNAME tiff PARENT_SCOPE)
  SET(TIFF_INCLUDE_DIRNAME
    ${OPENJPEG_SOURCE_DIR}/thirdparty/libtiff
    ${OPENJPEG_BINARY_DIR}/thirdparty/libtiff
    PARENT_SCOPE)
  SET(OPJ_HAVE_TIFF_H 1 PARENT_SCOPE)
  SET(OPJ_HAVE_LIBTIFF 1 PARENT_SCOPE)
ELSE (BUILD_THIRDPARTY)
  FIND_PACKAGE(TIFF)
  IF(TIFF_FOUND)
    message(STATUS "Your system seems to have a TIFF lib available, we will use it")
    SET(OPJ_HAVE_TIFF_H 1 PARENT_SCOPE)
    SET(OPJ_HAVE_LIBTIFF 1 PARENT_SCOPE)
    SET(TIFF_LIBNAME ${TIFF_LIBRARIES} PARENT_SCOPE)
    SET(TIFF_INCLUDE_DIRNAME ${TIFF_INCLUDE_DIR} PARENT_SCOPE)
  ELSE (TIFF_FOUND) # not found
    SET(OPJ_HAVE_TIFF_H 0 PARENT_SCOPE)
    SET(OPJ_HAVE_LIBTIFF 0 PARENT_SCOPE)
    message(STATUS "TIFF lib not found, activate BUILD_THIRDPARTY if you want build it")
  ENDIF(TIFF_FOUND)
ENDIF(BUILD_THIRDPARTY)

#------------
# Try to find lib LCMS2 (or by default LCMS)
SET(OPJ_HAVE_LCMS_H 0 PARENT_SCOPE)
SET(OPJ_HAVE_LIBLCMS 0 PARENT_SCOPE)

IF( BUILD_THIRDPARTY)
  # Try to build lcms2
  message(STATUS "We will build LCMS2 lib from thirdparty")
  ADD_SUBDIRECTORY(liblcms2)
  SET(LCMS_LIBNAME lcms2 PARENT_SCOPE)
  SET(LCMS_INCLUDE_DIRNAME ${OPENJPEG_SOURCE_DIR}/thirdparty/liblcms2/include PARENT_SCOPE) #
  SET(OPJ_HAVE_LCMS2_H 1 PARENT_SCOPE)
  SET(OPJ_HAVE_LIBLCMS2 1 PARENT_SCOPE)
ELSE (BUILD_THIRDPARTY)
  FIND_PACKAGE(LCMS2)
  IF(LCMS2_FOUND)
    message(STATUS "Your system seems to have a LCMS2 lib available, we will use it")
    SET(OPJ_HAVE_LCMS2_H 1 PARENT_SCOPE)
    SET(OPJ_HAVE_LIBLCMS2 1 PARENT_SCOPE)
    SET(LCMS_LIBNAME ${LCMS2_LIBRARIES} PARENT_SCOPE)
    SET(LCMS_INCLUDE_DIRNAME ${LCMS2_INCLUDE_DIRS} PARENT_SCOPE)
  ELSE (LCMS2_FOUND) # not found lcms2
    # try to find LCMS
    FIND_PACKAGE(LCMS)
    IF(LCMS_FOUND)
      message(STATUS "Your system seems to have a LCMS lib available, we will use it")
      SET(OPJ_HAVE_LCMS_H 1 PARENT_SCOPE)
      SET(OPJ_HAVE_LIBLCMS 1 PARENT_SCOPE)
      SET(LCMS_LIBNAME ${LCMS_LIBRARIES} PARENT_SCOPE)
      SET(LCMS_INCLUDE_DIRNAME ${LCMS_INCLUDE_DIRS} PARENT_SCOPE)
    ELSE (LCMS_FOUND) # not found lcms
      SET(OPJ_HAVE_LCMS2_H 0 PARENT_SCOPE)
      SET(OPJ_HAVE_LIBLCMS2 0 PARENT_SCOPE)
      message(STATUS "LCMS2 or LCMS lib not found, activate BUILD_THIRDPARTY if you want build it")
    ENDIF (LCMS_FOUND)
  ENDIF(LCMS2_FOUND)
ENDIF(BUILD_THIRDPARTY)
