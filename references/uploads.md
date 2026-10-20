# Uploads

Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.

Flow:

```text
Browser asks the server for permission.
Server validates auth, quota, and metadata.
Server signs upload URLs.
Browser uploads bytes directly to object storage.
Browser asks the server to finalize.
Server updates database state.
```

Use a single signed PUT for small files and multipart upload for large files.

Why direct upload: it avoids server body limits, avoids server memory spikes, avoids tying up serverless functions during slow uploads, and works for future mobile clients.

For multipart upload, storage CORS is part of the feature, not an afterthought. The browser must be allowed to PUT, and the store must expose the headers the completion step needs, such as the part identifiers.

Create the database row before the long-running client upload begins, so an interrupted upload leaves a recoverable record rather than nothing.

## Programmatic Callers

A script, CLI, integration, or agent sends bytes by a route that works from where it runs. Small text may travel inline in an ordinary request under a cap the interface states. The browser flow above stays the interactive path.

- A CLI reads local files and uploads them through the same signed direct upload.
- An HTTP client sends a file's bytes in a signed direct or multipart upload rather than encoding them into JSON.
- A remote agent passes a fetchable HTTPS URL, or an attachment reference its host documents as fetchable, because a language model generates an inline base64 blob token by token, which is slow, expensive, and bounded by its context window.
- Refuse a local path or sandbox URI, which names a file only the caller can see, with an error that names the routes that work, and report an upload as done only once it has landed.

Say which route each caller takes in the interface description and schema hints, so callers reach for the right shape by default. Keep host-specific attachment adapters at the protocol boundary, and upload staging and completion in the HTTP API and CLI. A server-fetched URL gets the same hardening as every server-side fetch of a caller-supplied URL. Every route, the browser's included, passes the same authorization, quota, validation, and durable finalize before content counts as added.
