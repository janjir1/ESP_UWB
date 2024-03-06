# For more information about build system see
# https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html
# The following five lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

#Set project name
set(proj "Simple_anchor")
#Set project root path
set(ROOT_DIR "d:\\Files\\Projects\\ESP_UWB")

#-----------Check if the global shell variable exists-----------
if(DEFINED ENV{ESP_UWB_ROOT_DIR})
    # Set a CMake variable based on the global shell variable
    set(ROOT_DIR $ENV{ESP_UWB_ROOT_DIR})
    message(STATUS "ROOT_DIR: ${ROOT_DIR}")
else()
    message(WARNING "ROOT_DIR is not defined. Using ${ROOT_DIR}")
endif()

#-------------Adding components------------------------------

# Set the source and destination directories
set(SOURCE_DIR "${ROOT_DIR}\\components")
set(DESTINATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

# Copy the contents of the source directory to the destination directory

message(STATUS "Adding components:")
if(IS_DIRECTORY ${DESTINATION_DIR}\\components)
    message(STATUS "Folder was already copied")
else()
    file(COPY ${SOURCE_DIR} DESTINATION ${DESTINATION_DIR})
    if(IS_DIRECTORY ${DESTINATION_DIR}\\components)
        message(STATUS "Folder copied successfully to: ${DESTINATION_DIR}")
    else()
        message(FATAL_ERROR "Failed to copy the folder.")
    endif()
endif()

#-------------Adding .vscode------------------------------

# Set the source and destination directories
set(SOURCE_DIR "${ROOT_DIR}\\build_settitngs\\.vscode")
set(DESTINATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

# Copy the contents of the source directory to the destination directory

message(STATUS "Adding .vscode:")
if(IS_DIRECTORY ${DESTINATION_DIR}\\.vscode)
    message(STATUS "Folder was already copied")
else()
    file(COPY ${SOURCE_DIR} DESTINATION ${DESTINATION_DIR})
    if(IS_DIRECTORY ${DESTINATION_DIR}\\.vscode)
        message(STATUS "Folder copied successfully to: ${DESTINATION_DIR}")
    else()
        message(FATAL_ERROR "Failed to copy the folder.")
    endif()
endif()

#-------------Adding sdkconfig------------------------------

# Set the source and destination directories
set(SOURCE_DIR "${ROOT_DIR}\\build_settitngs\\sdkconfig")
set(DESTINATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

# Copy the contents of the source directory to the destination directory

message(STATUS "Adding sdkconfig:")
if(EXISTS ${DESTINATION_DIR}\\sdkconfig)
    message(STATUS "File is already present")
else()
    file(COPY ${SOURCE_DIR} DESTINATION ${DESTINATION_DIR})
    if(EXISTS ${DESTINATION_DIR}\\sdkconfig)
        message(STATUS "File copied successfully to: ${DESTINATION_DIR}")
    else()
        message(FATAL_ERROR "Failed to copy the file.")
    endif()
endif()

#-------------Adding main CMakeLists------------------------------

# Set the source and destination directories
set(SOURCE_DIR "${ROOT_DIR}\\build_settitngs\\main\\CMakeLists.txt")
set(DESTINATION_DIR "${CMAKE_CURRENT_SOURCE_DIR}\\main\\")

# Copy the contents of the source directory to the destination directory

message(STATUS "Adding CMakelists:")
if(EXISTS ${DESTINATION_DIR}\\CMakeLists.txt)
    message(STATUS "File is already present")
else()
    file(COPY ${SOURCE_DIR} DESTINATION ${DESTINATION_DIR})
    if(EXISTS ${DESTINATION_DIR}\\CMakeLists.txt)
        message(STATUS "File copied successfully to: ${DESTINATION_DIR}")
    else()
        message(FATAL_ERROR "Failed to copy the file.")
    endif()
endif()

# ------------------------------
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

project(${proj})


# Set FreeRTOS tick rate to 1000 Hz
idf_build_set_property(FREERTOS_HZ 1000)
