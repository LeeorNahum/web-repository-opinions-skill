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

A script, CLI, integration, or agent takes the route that actually moves bytes from where it runs. The browser flow above stays the interactive path.

- A CLI reads local files and uploads them through the same signed direct upload.
- An HTTP client sends file bytes in a signed direct or multipart upload rather than encoding them into JSON, while small text, such as a settings file, may travel in an ordinary request body under a stated cap.
- A remote agent passes a fetchable HTTPS URL, or an attachment reference its host documents as fetchable. Small text may travel inline under a stated cap. Any other file travels by URL or attachment reference, because a language model generates an inline base64 blob token by token, which is slow, expensive, and bounded by its context window.
- A local path or sandbox URI names a file only the caller can see and moves no bytes. When a caller has no route that moves bytes, refuse with an error that names the routes that work, and never report an upload that did not land.

Say which route each caller takes in the interface description and schema hints, so callers reach for the right shape by default. Keep host-specific attachment adapters at the protocol boundary, and upload staging and completion in the HTTP API and CLI. A server-fetched URL gets the same hardening as every server-side fetch of a caller-supplied URL. Every route, the browser's included, passes the same authorization, quota, validation, and durable finalize before content counts as added.
