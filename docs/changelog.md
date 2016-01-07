### v0.2

- Fixed library transform for *nix platforms
- Fixed recursive glob expansion with more then 9 groups
- Added OS X tests
- Added IDE generators tests
- Added MSVS2015, Make, CMake and QtCreator project generators
- Added SSE3/SSSE3/SSE4.1 & no exceptions flags
- Added {path} and {file} properties to transforms
- Added filters in nested variables
- Added environment setup command in IDE project generators
- Added path/file flag to target path regex capture groups
- Renamed transform app -> application
- Renamed transform obj -> objects
- Renamed transform lib -> library
- Renamed transform shlib -> shared_library
- Removed transform shlib_dep (please check manual)
- Removed EOL comments (only newline commets are allowed)
- Misc : only allow transforms on whole path and not parts of it
- Misc : auto detection of MSVS version
- Misc : more detailed error reports

### v0.1

- Initial version
- Misc : release as v0.1.2 on PyPi because of a mistake