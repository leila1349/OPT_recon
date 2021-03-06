#include <utility>

# include <boost/python.hpp>
# include <Python.h>
# include <Numeric/arrayobject.h>
# include <ct.h>


PyObject *get_data(const Projections &pj)
{
  int sizes[2] = { pj.nView(), pj.nDet() };
  char *ptr0, *ptr1;

  PyArrayObject  *array = 
      (PyArrayObject *) PyArray_FromDims(2, sizes, PyArray_FLOAT); 

  ptr0 = array->data;
  for (int iy = 0; iy < pj.nView(); iy++) {
    ptr1 = ptr0;
    const DetectorArray& detarray = pj.getDetectorArray (iy);
    const DetectorValue* detval = detarray.detValues();
    for (int ix = 0; ix < pj.nDet(); ix++) {
      *(float *) ptr1 = detval[ix];
      ptr1 += array->strides[1];
    }
    ptr0 += array->strides[0];
  }
  
  return (PyObject *) array;
}

void set_data(Projections &pj, PyObject *obj)
{

  int sizes[2] = { pj.nView(), pj.nDet() };
  char *ptr0, *ptr1;

  PyArrayObject  *array = 
    (PyArrayObject *) PyArray_ContiguousFromObject(obj, PyArray_FLOAT, 2, 2);
  if(array == NULL) {
    PyErr_SetString(PyExc_TypeError, "incorrect array type");
    throw boost::python::error_already_set();
  }

  if(array->dimensions[0] != sizes[0] || array->dimensions[1] != sizes[1]) {
    PyErr_SetString(PyExc_TypeError, 
                    "Array dimension do not match projections");
    throw boost::python::error_already_set();
  }

  ptr0 = array->data;
  for (int iy = 0; iy < pj.nView(); iy++) {
    ptr1 = ptr0;
    DetectorArray& detarray = pj.getDetectorArray (iy);
    DetectorValue* detval = detarray.detValues();
    for (int ix = 0; ix < pj.nDet(); ix++) {
      detval[ix] = *(float *) ptr1;
      ptr1 += array->strides[1];
    }
    ptr0 += array->strides[0];
  }
}

using namespace boost::python;

BOOST_PYTHON_MODULE(libprojections)
{


	class_<Projections,boost::noncopyable>("Projections", init<>())
	  .def("read", (bool (Projections::*)(const std::string&)) &Projections::read)
	  .def("write",(bool (Projections::*)(const std::string&)) &Projections::write)
	  .def("nDet", &Projections::nDet)
      .def("nView", &Projections::nView)
      .def("detStart", &Projections::detStart)
      .def("rotStart", &Projections::rotStart)
      .def("detInc", &Projections::detInc)
      .def("rotInc", &Projections::rotInc)
      .def("geometry", &Projections::geometry)
	  .def("setNView", &Projections::setNView)
	  .def("printProjectionData",(void (Projections::*)()) &Projections::printProjectionData)
	  .def("printProjectionData", (void (Projections::*)(int, int)) &Projections::printProjectionData)
	  .def("getLabel", (Array2dFileLabel& (Projections::*)()) &Projections::getLabel, return_value_policy<reference_existing_object>())
	  .def("getFilename", &Projections::getFilename, return_value_policy<copy_const_reference>())
	  .def("get_data", get_data)
      .def("set_data", set_data)
	  .def("setRotInc", &Projections::setRotInc)
	  .def("setDetInc", &Projections::setDetInc)
	  .def("viewLen", &Projections::viewLen)
	  .def("viewDiameter", &Projections::viewDiameter)
	  .def("phmLen", &Projections::phmLen)
	  .def("focalLength", &Projections::focalLength)
	  .def("sourceDetectorLength", &Projections::sourceDetectorLength)
	  .def("setPhmLen", (void (Projections::*)(double)) &Projections::setPhmLen)


	;

	class_<Array2dFileLabel>("Array2dFileLabel",init<>())
		.def("getLabelType", &Array2dFileLabel::getLabelType)
		.def("print", &Array2dFileLabel::print)
		.def("getLabelString", &Array2dFileLabel::getLabelString, return_value_policy<copy_const_reference>())
	;

	import_array();
}
