# DOC - Librarian

- [ ] how it works: filtering True/False
- [ ] .librarian file rules and syntax


## Include/Exclude

- `!file/path` -> does not apply any modification (i.e. delete, overwrite) to the **local** folder
- `file/path`:
  - `filtering=True`: the files are not copied to **local**;
  - `filtering=False`: only the files according to the statement are copied to **local**.

- add a flag `filtering` for filtering files/folders:
-  `filtering=True`: files/folders copy from external to local will be excluded;
-  `filtering=False`: files/folders copy from external to local will be the only ones included;
-  in both the cases, local files will be handled in the same way;

| `.libignore` | `filtering=True` | `filtering=False` |
| --- | --- | --- |
| `dirname/filepath` | excluded from copy | the only one to be copied |
| `!filepath` | locks local file/folder`*` | locks local file/folder`*` |

`*`:local file will be excluded from any modification, i.e. delete nor overwrite