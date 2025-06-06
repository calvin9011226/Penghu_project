# Generated by CMake

if("${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}" LESS 2.8)
   message(FATAL_ERROR "CMake >= 2.8.3 required")
endif()
if(CMAKE_VERSION VERSION_LESS "2.8.3")
   message(FATAL_ERROR "CMake >= 2.8.3 required")
endif()
cmake_policy(PUSH)
cmake_policy(VERSION 2.8.3...3.29)
#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Protect against multiple inclusion, which would fail when already imported targets are added once more.
set(_cmake_targets_defined "")
set(_cmake_targets_not_defined "")
set(_cmake_expected_targets "")
foreach(_cmake_expected_target IN ITEMS libspatialindex::spatialindex libspatialindex::spatialindex_c)
  list(APPEND _cmake_expected_targets "${_cmake_expected_target}")
  if(TARGET "${_cmake_expected_target}")
    list(APPEND _cmake_targets_defined "${_cmake_expected_target}")
  else()
    list(APPEND _cmake_targets_not_defined "${_cmake_expected_target}")
  endif()
endforeach()
unset(_cmake_expected_target)
if(_cmake_targets_defined STREQUAL _cmake_expected_targets)
  unset(_cmake_targets_defined)
  unset(_cmake_targets_not_defined)
  unset(_cmake_expected_targets)
  unset(CMAKE_IMPORT_FILE_VERSION)
  cmake_policy(POP)
  return()
endif()
if(NOT _cmake_targets_defined STREQUAL "")
  string(REPLACE ";" ", " _cmake_targets_defined_text "${_cmake_targets_defined}")
  string(REPLACE ";" ", " _cmake_targets_not_defined_text "${_cmake_targets_not_defined}")
  message(FATAL_ERROR "Some (but not all) targets in this export set were already defined.\nTargets Defined: ${_cmake_targets_defined_text}\nTargets not yet defined: ${_cmake_targets_not_defined_text}\n")
endif()
unset(_cmake_targets_defined)
unset(_cmake_targets_not_defined)
unset(_cmake_expected_targets)


# Create imported target libspatialindex::spatialindex
add_library(libspatialindex::spatialindex SHARED IMPORTED)

# Create imported target libspatialindex::spatialindex_c
add_library(libspatialindex::spatialindex_c SHARED IMPORTED)

set_target_properties(libspatialindex::spatialindex_c PROPERTIES
  INTERFACE_LINK_LIBRARIES "libspatialindex::spatialindex"
)

# Import target "libspatialindex::spatialindex" for configuration "Debug"
set_property(TARGET libspatialindex::spatialindex APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(libspatialindex::spatialindex PROPERTIES
  IMPORTED_IMPLIB_DEBUG "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/Debug/spatialindex-64.lib"
  IMPORTED_LOCATION_DEBUG "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/Debug/spatialindex-64.dll"
  )

# Import target "libspatialindex::spatialindex_c" for configuration "Debug"
set_property(TARGET libspatialindex::spatialindex_c APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(libspatialindex::spatialindex_c PROPERTIES
  IMPORTED_IMPLIB_DEBUG "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/Debug/spatialindex_c-64.lib"
  IMPORTED_LOCATION_DEBUG "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/Debug/spatialindex_c-64.dll"
  )

# Import target "libspatialindex::spatialindex" for configuration "Release"
set_property(TARGET libspatialindex::spatialindex APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(libspatialindex::spatialindex PROPERTIES
  IMPORTED_IMPLIB_RELEASE "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/Release/spatialindex-64.lib"
  IMPORTED_LOCATION_RELEASE "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/Release/spatialindex-64.dll"
  )

# Import target "libspatialindex::spatialindex_c" for configuration "Release"
set_property(TARGET libspatialindex::spatialindex_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(libspatialindex::spatialindex_c PROPERTIES
  IMPORTED_IMPLIB_RELEASE "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/Release/spatialindex_c-64.lib"
  IMPORTED_LOCATION_RELEASE "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/Release/spatialindex_c-64.dll"
  )

# Import target "libspatialindex::spatialindex" for configuration "MinSizeRel"
set_property(TARGET libspatialindex::spatialindex APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(libspatialindex::spatialindex PROPERTIES
  IMPORTED_IMPLIB_MINSIZEREL "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/MinSizeRel/spatialindex-64.lib"
  IMPORTED_LOCATION_MINSIZEREL "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/MinSizeRel/spatialindex-64.dll"
  )

# Import target "libspatialindex::spatialindex_c" for configuration "MinSizeRel"
set_property(TARGET libspatialindex::spatialindex_c APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(libspatialindex::spatialindex_c PROPERTIES
  IMPORTED_IMPLIB_MINSIZEREL "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/MinSizeRel/spatialindex_c-64.lib"
  IMPORTED_LOCATION_MINSIZEREL "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/MinSizeRel/spatialindex_c-64.dll"
  )

# Import target "libspatialindex::spatialindex" for configuration "RelWithDebInfo"
set_property(TARGET libspatialindex::spatialindex APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(libspatialindex::spatialindex PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/RelWithDebInfo/spatialindex-64.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/RelWithDebInfo/spatialindex-64.dll"
  )

# Import target "libspatialindex::spatialindex_c" for configuration "RelWithDebInfo"
set_property(TARGET libspatialindex::spatialindex_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(libspatialindex::spatialindex_c PROPERTIES
  IMPORTED_IMPLIB_RELWITHDEBINFO "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/src/RelWithDebInfo/spatialindex_c-64.lib"
  IMPORTED_LOCATION_RELWITHDEBINFO "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/RelWithDebInfo/spatialindex_c-64.dll"
  )

# This file does not depend on other imported targets which have
# been exported from the same project but in a separate export set.

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
cmake_policy(POP)
