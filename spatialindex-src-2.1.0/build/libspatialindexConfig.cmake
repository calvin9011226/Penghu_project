
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was libspatialindexConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

set(SIDX_VERSION_MAJOR 2)
set(SIDX_VERSION_MINOR 1)
set(SIDX_VERSION_PATCH 0)

set_and_check(SIDX_INCLUDE_DIR "${PACKAGE_PREFIX_DIR}/include")
set_and_check(SIDX_LIB_DIR "${PACKAGE_PREFIX_DIR}/lib")

include("${CMAKE_CURRENT_LIST_DIR}/libspatialindexTargets.cmake")

set(SIDX_LIBRARIES spatialindex_c spatialindex)

check_required_components(libspatialindex)
