# Published Folders

One main repository holds everything a product owns, so an agent pointed at that one repository, on a machine or in a cloud session, sees and can edit every part of it, and an edit to shared text finds every place it appears. A part earns a repository of its own only when it needs what the main repository cannot give it: its own visibility, its own branches, or its own release workflow, as an agent plugin does when people install it from its own repository and it releases on its own schedule. A product with no such part has one repository and nothing to publish.

Such a part lives in the main repository as a plain folder of real files and is published out by a workflow. Agents edit only the folder, and the published repository is its output. Keep owned parts as plain folders rather than Git submodules, which most clones and cloud checkouts skip, and keep the publishing in the workflow rather than in agent rules, hooks, or a step someone remembers.

## The Publish Workflow

One workflow file per published folder, in the main repository. The exact file lives in `assets/publish-folder.yml`. Copy it rather than writing another:

- It runs on a push to `dev`, `preview`, or `main` that changes the folder, or when started by hand, and publishes to the branch of the same name in the target repository, so the target keeps the same branch roles.
- It replaces that branch's files with the folder's files and makes one commit on top of the branch. The message is `Release X.Y.Z` when the version in the folder's own manifest differs from the target's, and `Update` otherwise.
- A version change published to `main` also pushes the tag `vX.Y.Z` with the commit, so the target repository's own release workflow runs from the tag. `dev` and `preview` never tag, because a release comes from production. When the target already has that tag, the run stops before committing and asks for a new version, so a release tag never moves.
- Before pushing, it fails if the target branch's latest commit is not one it made, so a hand edit in the target stops publishing instead of being overwritten.
- Only the folder's files leave the main repository: no history, commit messages, or other folders.
- It authenticates with one fine-grained personal access token limited to the target repositories, with read and write access to contents, plus workflows when a published folder carries its own `.github/workflows`. It is stored as an Actions secret in the main repository. A token pushes the tag as a person would, which is what lets the target's release workflow run, since a push made with a workflow's own token starts no workflow.
- Publishing needs no approval beyond the push to the main repository.

Name the target repository for the product plus the part's role. Create it empty before the first publish, set its default branch to `main` once `main` is published, since an empty repository takes the first branch pushed, and set its visibility to whatever its audience and any directory it is submitted to require.

When the part already has a repository of its own, keep it and its history: move its files into the folder, then run the workflow once on each branch with its `adopt` input, so the first publish lands on top of the existing history instead of stopping at commits it did not make.
