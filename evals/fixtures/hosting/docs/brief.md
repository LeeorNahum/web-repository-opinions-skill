# Plinth

Plinth lets people publish small web apps that they or their AI agents write: plain HTML, CSS, and JavaScript, often using `localStorage`. Our domain is `plinth.example`.

## Decided

- Every app gets a short address, `<name>.plinth.example`. Short addresses are the main reason people pick us.
- The signed-in product is `app.plinth.example`. Sign-in uses a managed auth provider whose production instance keeps the session on `plinth.example` and shares it across subdomains.
- Apps can be private to invited people.
