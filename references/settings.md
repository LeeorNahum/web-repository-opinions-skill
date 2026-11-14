# Settings

A setting is a choice the product remembers for a workspace, a person, or a device. Declare each one once, store only what someone changed, and let everything else fall through to the default.

## One Declaration

Declare every setting once, in the domain package with the other product rules: its key, its type, its default, the layers it can be set at, and the label people see. The settings screen draws its rows from that declaration, the store checks values against it, and code reads a setting only through it, so a default or a label lives in one place.

## Keys

Behind every setting is a stable key that stays the same for as long as the setting means the same thing. The label people see is separate from the key, so renaming a setting on screen is a copy edit and leaves stored data alone.

When a setting's meaning changes, it becomes a new setting with a new key, and the old one leaves the declaration. Anyone who had changed the old one sets the new one again. Add a migration between keys only when an explicit supported contract requires it.

## Layers

Each layer stores only the keys someone changed at that layer, and a read takes the most specific layer that holds the key, with the default underneath everything:

```text
device -> person -> workspace -> default
```

A workspace sets values for everyone in it, a person changes what they want on top, and a device changes what makes sense only on that machine. Use only the layers the product has, and only the layers each setting declares.

Resetting a setting deletes its key from that layer, so it falls through to the layer below. A default the product improves later reaches everyone who never changed it.

## Writing

A write patches only the keys being changed against what is stored now, and leaves every other key as it was, including keys the running build does not declare. A read ignores keys it does not declare. Several keys that must change together go in one write.

- In a database, patch the changed keys inside the field in one atomic update, or read and write under a row lock, so two devices changing different settings both land.
- In a file, send every write through one writer, write the whole new file beside the old one, and rename it into place. A file that cannot be read is renamed aside, and the app starts on defaults.

## Where Each Layer Lives

| Layer | Store |
| --- | --- |
| Workspace and person | A JSON field on the workspace or person row in the database, holding only changed keys. The database is the source of truth across devices |
| Device | The platform's local store: browser storage on the web, one JSON file in the operating system's app config folder for a desktop app, the local key-value store on a phone. It stays on that device |

Secrets live apart from settings. On desktop and phone they go to the operating system's credential store, and on the web they stay on the server with the system that owns them.

A value the server's first render needs, such as theme or language, is also copied to a cookie, refreshed whenever the value, the signed-in person, or the workspace changes. The stored layer stays the source of truth, and the cookie only makes the first paint right.

## Saving

Saving starts the moment a change is made. Keep an explicit save for several fields that only make sense together, such as a connection's address and port, or for a change that affects other people, such as a workspace setting. A save that fails shows the value actually in force.

## When A Setting Cannot Be Honored

The stored value is what the person chose, and only the person changes it. When a feature cannot honor a setting at the moment it runs, it says so where it runs and the setting stays as set.

## The Settings Screen

Shape the screen to the product. Group settings by area, and give a long or busy group a page or tab of its own, the way phone and browser settings nest. Each setting's row offers a reset, in the form the platform uses for row actions.

Ask before changing the key of a setting people may already have set, or moving a setting to a different layer.
