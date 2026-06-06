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
