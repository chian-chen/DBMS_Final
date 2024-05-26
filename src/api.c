#include <Python.h>

// Wrapper method for python function 
#include <Python.h>
#include "clip_api.h"
// Wrapper method for python function 
int clip_label(const char* s) {
    PyObject *pModule = NULL, *pFunc = NULL, *pArgs = NULL, *pRes = NULL;
    int res = -1;

    // Import Python module & function
    PyImport_ImportModule("clip");
    // pModule = PyImport_ImportModule("pyapi");
    // pModule = PyImport_ImportModule("pyapi");
    pModule = PyImport_ImportModule("pyapi");
    if (!pModule) {
        PyErr_Print();
        goto cleanup;
    }

    pFunc = PyObject_GetAttrString(pModule, "api");
    if (!pFunc || !PyCallable_Check(pFunc)) {
        PyErr_Print();
        goto cleanup;
    }

    // Create args object to pass in
    pArgs = Py_BuildValue("(s)", s);
    if (!pArgs) {
        PyErr_Print();
        goto cleanup;
    }

    // Call function with args
    pRes = PyObject_CallObject(pFunc, pArgs);
    if (!pRes) {
        PyErr_Print();
        goto cleanup;
    }

    // Parse the return value into standard C types
    res = PyLong_AsLong(pRes);
    if (PyErr_Occurred()) {
        PyErr_Print();
        res = -1;
    }

cleanup:
    // Decrement reference counts to avoid memory leak
    Py_XDECREF(pModule);
    Py_XDECREF(pFunc);
    Py_XDECREF(pArgs);
    Py_XDECREF(pRes);

    return res;
}
// Main
int main() {
    // Init Python interpreter

    Py_Initialize();
    wchar_t *path = Py_DecodeLocale("/mysqludf/", NULL);
    PySys_SetPath(path);
    // PyObject* sysPath = PySys_GetObject("/home/fourcolor/Documents/db112/final/");
    // PyList_Append(sysPath, PyUnicode_DecodeFSDefault("."));
    // Call Python function
    printf("%d\n", clip_label("img.png"));

    // Frees memory allocated by Python interpreter 
    Py_Finalize();
    
    return 0;
}