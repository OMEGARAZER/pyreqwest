use http::header::Entry;
use pyo3::PyResult;
use pyo3::exceptions::{PyRuntimeError, PyValueError};

pub struct RequestBuilderHeaders {
    default_headers: Option<http::HeaderMap>,
    headers: Option<http::HeaderMap>,
}
impl RequestBuilderHeaders {
    pub fn new(default_headers: Option<http::HeaderMap>) -> Self {
        RequestBuilderHeaders {
            default_headers,
            headers: None,
        }
    }

    pub fn drain_into_headers(&mut self, headers: &mut http::HeaderMap) {
        if let Some(default) = self.default_headers.take() {
            headers.extend(default);
        }
        if let Some(h) = self.headers.take() {
            headers.extend(h);
        }
    }

    pub fn header(&mut self, key: http::HeaderName, value: http::HeaderValue) -> PyResult<()> {
        if let Some(defaults) = self.default_headers.as_mut() {
            Self::remove_header(defaults, &key)?; // Default gets replaced
        }

        if let Some(headers) = self.headers.as_mut() {
            headers
                .try_append(key, value)
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        } else {
            let mut headers = http::HeaderMap::new();
            headers.insert(key, value);
            self.headers = Some(headers);
        }
        Ok(())
    }

    pub fn headers(&mut self, headers: http::HeaderMap) -> PyResult<()> {
        if let Some(defaults) = self.default_headers.as_mut() {
            for key in headers.keys() {
                Self::remove_header(defaults, key)?; // Default gets replaced
            }
        }

        if let Some(existing) = self.headers.as_mut() {
            existing.extend(headers);
        } else {
            self.headers = Some(headers);
        }
        Ok(())
    }

    fn remove_header(headers: &mut http::HeaderMap, key: &http::HeaderName) -> PyResult<()> {
        let entry = headers
            .try_entry(key)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        if let Entry::Occupied(entry) = entry {
            entry.remove_entry_mult();
        }
        Ok(())
    }
}
