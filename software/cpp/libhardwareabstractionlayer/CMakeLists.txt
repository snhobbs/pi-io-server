cmake_minimum_required(VERSION 3.10.0)

project(hardwareabstractionlayer)
set(TargetName ${PROJECT_NAME})
message(STATUS "${PROJECT_NAME}")

add_library(${TargetName} SHARED)
set_property(TARGET ${TargetName} PROPERTY C_STANDARD 11)
set_property(TARGET ${TargetName} PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET ${TargetName} PROPERTY CMAKE_CXX_EXTENSIONS OFF)
set_property(TARGET ${TargetName} PROPERTY C_STANDARD_REQUIRED ON)
set_property(TARGET ${TargetName} PROPERTY CMAKE_C_EXTENSIONS OFF)

target_include_directories(${TargetName} PUBLIC source)
include_directories(source)

#aux_source_directory(${LIB_PATH} SOURCES)
set(HardwareSources
  source/writec.c
  source/dac.c
  source/adc.c
  source/Hardware.c
)

target_sources(${TargetName} PUBLIC ${HardwareSources})

target_link_libraries(${TargetName} PUBLIC bcm2835)
target_link_libraries(${TargetName} PUBLIC pthread)

target_compile_options(
    ${TargetName}
    PUBLIC
    -Wfatal-errors
    -Wall
    -Wextra
    -pedantic
    -Wpedantic
    -O3
    -g3
    #-pedantic-errors
    #-Werror=pedantic

    -Wconversion
    $<$<COMPILE_LANGUAGE:C>:-Wimplicit>
    $<$<COMPILE_LANGUAGE:C>:-Wunused>

    $<$<CXX_COMPILER_ID:GNU>:-Wsuggest-final-types>
    $<$<CXX_COMPILER_ID:GNU>:-Wmaybe-uninitialized>
    $<$<CXX_COMPILER_ID:GNU>:-Wdouble-promotion>
    $<$<CXX_COMPILER_ID:GNU>:-Wnull-dereference>
    -Winit-self

    $<$<CXX_COMPILER_ID:GNU>:-Wduplicated-cond>
    $<$<CXX_COMPILER_ID:GNU>:-Wduplicated-branches>
    $<$<CXX_COMPILER_ID:GNU>:-Wlogical-op>
    $<$<CXX_COMPILER_ID:GNU>:-Wrestrict>
    $<$<C_COMPILER_ID:GNU>:$<$<COMPILE_LANGUAGE:C>:-Wjump-misses-init>>
    $<$<COMPILE_LANGUAGE:CXX>:-Wold-style-cast>
    -Wshadow
)
