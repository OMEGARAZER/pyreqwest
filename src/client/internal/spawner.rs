use crate::client::internal::ConnectionLimiter;
use crate::exceptions::utils::map_send_error;
use crate::exceptions::{ClientClosedError, PoolTimeoutError};
use crate::logging::logger::flush_logs_no_gil;
use crate::request::RequestData;
use crate::response::BaseResponse;
use crate::runtime::RuntimeHandle;
use pyo3::coroutine::CancelHandle;
use pyo3::prelude::*;
use tokio::sync::OwnedSemaphorePermit;
use tokio_util::sync::CancellationToken;

pub struct Spawner {
    client: reqwest::Client,
    runtime: RuntimeHandle,
    connection_limiter: Option<ConnectionLimiter>,
    close_cancellation: CancellationToken,
}
impl Spawner {
    pub fn new(
        client: reqwest::Client,
        runtime: RuntimeHandle,
        connection_limiter: Option<ConnectionLimiter>,
        close_cancellation: CancellationToken,
    ) -> Self {
        Self {
            client,
            runtime,
            connection_limiter,
            close_cancellation,
        }
    }

    async fn spawn_reqwest_inner(mut request: RequestData, cancel: CancelHandle) -> PyResult<BaseResponse> {
        let spawner = &request.spawner;
        let client = spawner.client.clone();
        let connection_limiter = spawner.connection_limiter.clone();
        let runtime = spawner.runtime.clone();

        let fut = async move {
            let limiter_permit = match connection_limiter.as_ref() {
                Some(lim) => Some(Self::limit_connections(lim, &mut request.reqwest).await?),
                _ => None,
            };
            let request_permit = SpawnedRequestPermit {
                request_semaphore_permit: limiter_permit,
                connection_verbose: request.connection_verbose,
            };

            let mut resp = client.execute(request.reqwest).await.map_err(map_send_error)?;

            if let Some(extensions) = request.extensions {
                resp.extensions_mut().insert(extensions);
            }

            BaseResponse::initialize(
                resp,
                Some(request_permit),
                request.body_consume_config,
                runtime,
                request.json_handler,
                request.error_for_status,
            )
            .await
        };

        let fut = spawner.runtime.spawn_handled(fut, cancel);

        tokio::select! {
            res = fut => res?,
            _ = spawner.close_cancellation.cancelled() => Err(ClientClosedError::from_msg("Client was closed"),)
        }
    }

    pub async fn spawn_reqwest(request: RequestData, cancel: CancelHandle) -> PyResult<BaseResponse> {
        Self::spawn_reqwest_inner(request, cancel).await
    }

    pub fn blocking_spawn_reqwest(py: Python, request: RequestData) -> PyResult<BaseResponse> {
        let rt = &request.spawner.runtime.clone();
        rt.blocking_spawn(py, Self::spawn_reqwest_inner(request, CancelHandle::new()))
    }

    async fn limit_connections(
        connection_limiter: &ConnectionLimiter,
        request: &mut reqwest::Request,
    ) -> PyResult<OwnedSemaphorePermit> {
        let req_timeout = request.timeout().copied();
        let now = std::time::Instant::now();

        let permit = connection_limiter.limit_connections(req_timeout).await?;
        let elapsed = now.elapsed();
        if let Some(req_timeout) = req_timeout {
            if elapsed >= req_timeout {
                return Err(PoolTimeoutError::from_msg("Timeout acquiring semaphore")); // :NOCOV
            } else {
                *request.timeout_mut() = Some(req_timeout - elapsed);
            }
        }

        Ok(permit)
    }
}
impl Clone for Spawner {
    fn clone(&self) -> Self {
        Self {
            client: self.client.clone(),
            runtime: self.runtime.clone(),
            connection_limiter: self.connection_limiter.clone(),
            close_cancellation: self.close_cancellation.child_token(),
        }
    }
}

pub struct SpawnedRequestPermit {
    request_semaphore_permit: Option<OwnedSemaphorePermit>,
    connection_verbose: bool,
}
impl Drop for SpawnedRequestPermit {
    fn drop(&mut self) {
        let _ = self.request_semaphore_permit.take();

        if self.connection_verbose {
            let _ = flush_logs_no_gil();
        }
    }
}
