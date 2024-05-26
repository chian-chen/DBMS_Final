#include <Python.h>
#include <iostream>

// Wrapper method for Python function
int complex_calc(const char* s) {
    PyObject *pName = NULL, *pModule = NULL, *pFunc = NULL, *pArgs = NULL, *pRes = NULL;
    int res = -1;

    // Import Python module
    pName = PyUnicode_DecodeFSDefault("api");
    if (!pName) {
        PyErr_Print();
        goto cleanup;
    }

    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (!pModule) {
        PyErr_Print();
        goto cleanup;
    }

    // Get the function from the module
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

    // Call the function with args
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
    Py_XDECREF(pName);
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

    // Call Python function
    int result = complex_calc("img.png");
    std::cout << "Result: " << result << std::endl;

    // Frees memory allocated by Python interpreter
    Py_Finalize();

    return 0;
}