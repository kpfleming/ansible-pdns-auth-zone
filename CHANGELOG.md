# Changelog

All notable changes to this project will be documented in this file.

The format is based on [*Keep a
Changelog*](https://keepachangelog.com/en/1.0.0/) and this project
adheres to [*Calendar Versioning*](https://calver.org/).

The **first number** of the version is the 2-digit year.

The **second number** is incremented with each release, starting at 1
for each year.

The **third number** is for fixes made against older releases (only
for emergencies).

## [Unreleased]

## [24.3.0] - 2024-10-13

### Changed

- Corrected bug in publishing workflow; no content changes.

## [24.2.0] - 2024-10-13

### Changed

- Added testing against PowerDNS Authoritative Server 4.9.x.

- Removed testing against PowerDNS Authoritative Server 4.6.x (EOL).

- Added testing against Python 3.13 (beta).

- Removed support for Python 3.8.

- Fix ability to make zone deligation

## [24.1.0] - 2024-02-09

### Changed

- Added testing against PowerDNS Authoritative Server 4.8.x.

- Removed testing against PowerDNS Authoritative Server 4.5.x (EOL).

- Switched to fork of `j2cli` for rendering Galaxy metadata YAML file
  (no behavioral changes).

- Switched from `j2cli` to `jinjanator` for rendering metadata file.

- Python code refactored to reduce duplication.

- Module documentation refactored to reduce duplication.

- Python code improved to no longer use global variables.

- Galaxy metadata updated to current specifications.

- Galaxy `requirements.txt` added so that `ansible-builder` will
  install the necessary Python packages.

- Switched to CalVer.

## [3.4.1] - 2023-07-02

No content changes, tag created for new docsite publishing workflow.

## [3.4.0] - 2023-06-24

### Changed

- zone: Use semantic markup in module documentation.

- collection: Include link to docsite generated from module documentation.

## [3.3.0] - 2023-04-20

### Added

- zone: Added ability to create RRsets during zone creation (contributed by SrX in PR #138).

## [3.2.3] - 2023-03-14

### Changed

- zone: Resolved bugs in code added in 3.2.2, which ended up replacing
  one crash with another.
- Improved tests to report failures if exceptions are thrown while
  executing modules.
- zone: Resolved bugs in handling 'falsy' metadata values (reported by
  @SrX in #136).
- zone: Ensure that metadata items which are not present in an API
  response are also not present in the 'zone' module's result.

## [3.2.2] - 2023-03-07

### Changed

- Improved validation of 'zone' module arguments to avoid crashes in
  some situations (reported by @kviset in #133).

## [3.2.1] - 2023-02-09

### Changed

- Added module parameters for `master_tsig_key_ids` and `slave_tsig_key_ids` (contributed by @SrX in PR #128).

## [3.2.0] - 2022-11-21

### Changed

- Added support for 'catalog' property of zones.

## [3.1.0] - 2022-11-16

### Changed

- Added support for 'catalog zones' feature available in PowerDNS
  Authoritative Server 4.7.x.

## [3.0.0] - 2022-10-20

### Changed

- Added testing against Python 3.11 pre-releases.
- Added testing against PowerDNS Authoritative Server 4.7.x.
- Removed testing against PowerDNS Authoritative Server 4.3.x.
- Many CI improvements, including linting of test playbooks.
- Build PowerDNS Authoritative Server from source instead of using
  packages, to reduce the size of the CI container image.
- Removed support for 'local file' API specification, since all
  supported versions of PowerDNS Authoritative Server supply the
  specification over HTTP.

## [2.0.0] - 2021-12-12

### Changed

- Converted to an Ansible Galaxy Collection, published as `kpfleming.powerdns_auth`.
  Existing users will need to change their playbooks to refer to the new module
  name, but there are no behavior changes.

- Added testing against PowerDNS Authoritative Server 4.6.x.

## [1.8.0] - 2021-10-02

### Changed

- Removed support for Python 3.6 and 3.7, as Ansible will require 3.8 soon.

- Pinned 'jsonschema' to versions below 4 to maintain compatibiity with
the pinned version of `swagger-spec-validator'.

## [1.7.0] - 2021-08-31

### Changed

- Added testing against PowerDNS Authoritative Server 4.5.x.

- Added testing against Python 3.10 release candidates.

## [1.6.0] - 2021-04-20

### Changed

- Removed testing against PowerDNS Authoritative Server 4.2.x, which is no longer
supported.

- Added testing against PowerDNS Authoritative Server 4.4.x, which includes HTTP
support for obtaining the API schema.

- Corrected flaws in test playbooks.

## [1.5.0] - 2020-11-29

### Changed

- Support for creation of SOA and NS records during zone creation, eliminating
requirement to set server configuration properties to synthesize the records.

## [1.4.0] - 2020-11-23

### Changed

- Support for direct reading of the Swagger spec from the server (instead
of a local file) has been added; this feature will be available in PowerDNS
Authoritative Server 4.4.0.

## [1.3.0] - 2020-08-19

### Changed

- Python 3.5 support has been removed.

## [1.2.2] - 2020-08-17

### Changed

- Correct population of existing zone properties.
- Handle API-RECTIFY as a binary zone property instead of ternary.
- Improve performance by requesting that rrsets not be returned in zone API calls.

## [1.2.1] - 2020-08-15

### Changed

- Improved handling of zone metadata during zone creation; default values are
  no longer sent, as they can trigger errors using the current development
  branch of the server.

## [1.2.0] - 2020-06-12

### Changed

- Improved handling of predictable exceptions from API operations.
- Corrected handling of changes to list of masters in slave zones.

## [1.1.0] - 2020-04-09

### Added

- pdns_auth_tsigkey.py module for managing TSIG keys.

- Support for metadata-in-zone properties.

### Changed

- Removed metadata elements which are immutable from the module parameters list;
  they will still be included in the return value if set on a zone.

- Updated to 0.0.15 version of API specification which documents all response objects.

## 1.0.0 - 2020-04-03

First release!

### Added

- pdns_auth_zone.py module for managing zones.

### Changed

[unreleased]: https://github.com/kpfleming/ansible-powerdns-auth/compare/24.1.0...HEAD
[24.1.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.4.1...24.1.0
[3.4.1]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.4.0...3.4.1
[3.4.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.3.0...3.4.0
[3.3.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.2.3...3.3.0
[3.2.3]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.2.2...3.2.3
[3.2.2]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.2.1...3.2.2
[3.2.1]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.2.0...3.2.1
[3.2.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/3.0.0...3.1.0
[3.0.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/2.0.0...3.0.0
[2.0.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.8.0...2.0.0
[1.8.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kpfleming/ansible-powerdns-auth/compare/v1.0.0...v1.1.0
