
set(PSF_SRC
fdr.c
fft_helpers.c
real_complex_helpers.c
psfstack_helpers.c
)

INCLUDE_DIRECTORIES(
${MINC2_INCLUDE_PATH} ${HDF5_INCLUDE_PATH} ${NETCDF_INCLUDE_PATH}
${OPT_recon_SOURCE_DIR}/MINC
${OPT_recon_SOURCE_DIR}/PSF/FDR

)

IF(FFTW3_FOUND)
  INCLUDE_DIRECTORIES(${FFTW3_INCLUDE_DIRS})
ENDIF(FFTW3_FOUND)

ADD_LIBRARY(FDR SHARED ${PSF_SRC})

IF(FFTW3_FOUND)
  TARGET_LINK_LIBRARIES(FDR ${FFTW3_LIBRARIES} useMINC2)
ENDIF(FFTW3_FOUND)

# add the install targets
INSTALL(TARGETS FDR LIBRARY DESTINATION lib PERMISSIONS OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE  OWNER_READ GROUP_READ WORLD_READ)