
INCLUDE_DIRECTORIES(
${MINC2_INCLUDE_PATH} ${HDF5_INCLUDE_PATH} ${NETCDF_INCLUDE_PATH}
${OPT_recon_SOURCE_DIR}/MINC
${OPT_recon_SOURCE_DIR}/GetOPTData
${OPT_recon_SOURCE_DIR}/PSF/FDR
)

SET(GETOPTDATA_SRC
filehandle.cpp
optvars.cpp
optdarks.cpp
getoptdata.cpp
)
ADD_EXECUTABLE(optdataTOminc ${GETOPTDATA_SRC})
TARGET_LINK_LIBRARIES(optdataTOminc useMINC2)

INSTALL(TARGETS optdataTOminc DESTINATION bin)