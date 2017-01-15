# Build the demo app, small examples

# First thing define the common source:
SET(common_SRCS
  convert.c
  ${OPENJPEG_SOURCE_DIR}/src/bin/common/opj_getopt.c
  )

# Headers file are located here:
include_directories(
  ${OPENJPEG_BINARY_DIR}/src/lib/openjp2 # opj_config.h
  ${OPENJPEG_SOURCE_DIR}/src/lib/openjp3d
  ${LCMS_INCLUDE_DIRNAME}
  ${OPENJPEG_SOURCE_DIR}/src/bin/common
  ${Z_INCLUDE_DIRNAME}
  ${PNG_INCLUDE_DIRNAME}
  ${TIFF_INCLUDE_DIRNAME}
  )

if(WIN32)
  if(BUILD_SHARED_LIBS)
    add_definitions(-DOPJ_EXPORTS)
  else()
    add_definitions(-DOPJ_STATIC)
  endif()
endif()

# Loop over all executables:
FOREACH(exe opj_jp3d_compress opj_jp3d_decompress)
  ADD_EXECUTABLE(${exe} ${exe}.c ${common_SRCS})
  TARGET_LINK_LIBRARIES(${exe} openjp3d)
  # On unix you need to link to the math library:
  IF(UNIX)
    TARGET_LINK_LIBRARIES(${exe} m)
  ENDIF(UNIX)
  # Install exe
  INSTALL(TARGETS ${exe}
    EXPORT OpenJP3DTargets
    DESTINATION ${OPENJPEG_INSTALL_BIN_DIR} COMPONENT Applications
  )
endforeach()
