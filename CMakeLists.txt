cmake_minimum_required (VERSION 3.2)
project(KatanaGDAssetPlugin)
#set(BOOST_LIBRARYDIR C:/dev/boost_1_61_0/lib64-msvc-14.0)
#set(CMAKE_IGNORE_PATH C:/workspace/USD)
set(KATANA_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../.." CACHE PATH "PATH TO KATANA")
list(INSERT CMAKE_MODULE_PATH 0 "${KATANA_ROOT}/plugins/Src/cmake")

set(CMAKE_CXX_STANDARD 11)

find_package(Katana PATHS "${KATANA_ROOT}/plugin_apis/cmake" REQUIRED)

if(NOT MSVC)
    add_compile_options(-Wall)
endif ()

if(CMAKE_SYSTEM_NAME MATCHES Linux)
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -W1, --no-undefined")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -W1, --no-undefined")
endif ()

if(MSVC)
    add_definitions(-DBOOST_ALL_NO_LIB)
endif()


#set(Boost_DEBUG ON)

set(KATANA_API_LOCATION "C:/Program Files/Katana4.5v1")

        # Setup the variables to use the Katana builds.
        set(BOOST_LIBRARYDIR ${KATANA_API_LOCATION}/bin)
        set(BOOST_INCLUDEDIR ${KATANA_API_LOCATION}/external/foundryboost/include)

        set(Boost_NO_SYSTEM_PATHS ON)
        set(Boost_NO_BOOST_CMAKE ON)
        set(Boost_USE_MULTITHREADED ON)
        set(Boost_USE_RELEASE_LIBS ON)
        set(Boost_USE_DEBUG_LIBS OFF)
        set(Boost_NAMESPACE foundryboost)
        set(Boost_USE_STATIC_LIBS OFF)
        if(MSVC)
            add_definitions(-DBOOST_ALL_NO_LIB)
            add_definitions(-DBOOST_ALL_DYN_LINK)
            set(Boost_ARCHITECTURE -x64)
            set(Boost_COMPILER -vc141)
        endif()
        add_compile_definitions(Boost_NAMESPACE=${Boost_NAMESPACE})
 
    find_package(Boost 1.70.0
        COMPONENTS
            filesystem
            regex
        REQUIRED)

add_subdirectory(gdAsset)