add_library(gdAsset MODULE src/gdAsset.cpp)

target_include_directories(gdAsset PRIVATE include)

target_link_libraries(gdAsset
    PRIVATE
    Katana::FnAsset
    Katana::FnAssetPlugin
    Katana::FnAttribute
    Katana::FnLogging
    Katana::pystring
    Boost::regex
    Boost::filesystem
)

set_target_properties(gdAsset PROPERTIES PREFIX "")

#target_include_directories(gdAsset PRIVATE ${Boost_INCLUDE_DIRS})
#target_link_libraries(gdAsset PRIVATE ${Boost_LIBRARIES})

install(TARGETS gdAsset DESTINATION Libs)