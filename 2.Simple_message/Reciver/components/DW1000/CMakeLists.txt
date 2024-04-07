set(srcs
  src/DW1000.cpp
  src/DW1000Device.cpp
  src/DW1000Mac.cpp
  src/DW1000Ranging.cpp
  src/DW1000Time.cpp

  )


idf_component_register(SRCS ${srcs}
                    INCLUDE_DIRS "src"
                    REQUIRES arduino)
target_compile_options(${COMPONENT_LIB} PRIVATE "-Wno-format")
