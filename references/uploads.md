# Uploads

Upload user files directly from the browser to object storage. Vercel, the default host, caps a function request body at 4.5 MB, so a proxied upload breaks on ordinary files.

Flow:

```text
Browser asks the server for permission.
Server validates auth, quota, and metadata.
Server registers the object keys and signs upload URLs.
Browser uploads bytes directly to object storage.
Browser asks the server to finalize.
Server updates database state.
```

Use one signed PUT below 100 MB and multipart upload at 100 MB and above.

Why direct upload: it avoids server body limits, avoids server memory spikes, avoids tying up serverless functions during slow uploads, and works for future mobile clients.

For multipart upload, storage CORS is part of the feature, not an afterthought. Allow PUT from the product's app origins and expose the ETag header, which the completion step needs for every part.

## Steer File Input Away From Inline Blobs

When a public interface accepts file content from an automated caller, prefer passing the bytes out of band. For a language model, an inline base64 or otherwise encoded blob is generated token by token, which is slow, expensive, and bounded by the context window. A URL the server fetches is fast, cheap, and unbounded. For any HTTP client, a normal file upload beats embedding the same bytes in JSON or another encoded field. Make a server-fetched URL or multipart upload the documented primary input and reserve inline bytes for genuinely tiny content, and say so in the interface description and schema hints so callers reach for the right shape by default. Apply the same SSRF and size protections to a server-fetched URL that any server-side fetch requires.
