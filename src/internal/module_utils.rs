use pyo3::prelude::*;
use pyo3::types::PyType;
use pyo3::{PyTypeInfo, intern};

pub fn register_submodule(module: &Bound<'_, PyModule>, submodule_name: &str) -> PyResult<()> {
    // https://github.com/PyO3/pyo3/issues/759
    module
        .py()
        .import("sys")?
        .getattr("modules")?
        .set_item(format!("pyreqwest._pyreqwest.{}", submodule_name), module)?;

    fix_module(module, submodule_name)
}

pub fn register_collections_abc<T: PyTypeInfo>(py: Python, base: &str) -> PyResult<()> {
    // Buffer ABC was added in Python 3.12
    if base == "Buffer" && py.version_info() < (3, 12) {
        return Ok(()); // :NOCOV
    }

    py.import("collections.abc")?
        .getattr(base)?
        .call_method1(intern!(py, "register"), (PyType::new::<T>(py),))
        .map(|_| ())
}

fn fix_module(module: &Bound<'_, PyModule>, submodule_name: &str) -> PyResult<()> {
    // Need to fix module names, otherwise pyo3 uses "builtin" as module name. This breaks doc generation.
    for attr_name in module.dir()?.iter() {
        let attr_name: &str = attr_name.extract()?;
        if attr_name.starts_with("_") {
            continue;
        }
        module
            .getattr(attr_name)?
            .setattr("__module__", format!("pyreqwest.{}", submodule_name))?;
    }
    Ok(())
}
